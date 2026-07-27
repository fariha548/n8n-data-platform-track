"""
Module 5 — Gemini-as-ingestion-source into BigQuery.
Uses the current `google-genai` SDK (the old `google.generativeai` package
is deprecated as of 2026 — this was verified by hitting a live 404/deprecation
warning during testing, not assumed).

Flow:
    input record -> Gemini API call (retry+backoff) -> schema validation
    -> dedup check (input hash) -> BigQuery insert (or route to failed table)

Design decisions (documented, not assumed):
- Dedup key = sha256(input_id + input_text), NOT the Gemini output — because
  Gemini's output is non-deterministic across calls, so content-based dedup
  would incorrectly treat two valid different responses as duplicates.
- Retry uses tenacity (exponential backoff + jitter), capped at 4 attempts —
  hand-rolled sleep loops risk thundering-herd behavior when the API recovers.
- Malformed/invalid Gemini output is never silently dropped — it goes to a
  separate `failed_llm_calls` table so failure rate is visible, not hidden.
- Structured output enforced via response_mime_type="application/json" +
  response_schema, so we're not manually parsing free text.
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
load_dotenv()  # load .env explicitly — don't rely on the parent shell's env,
                # since this module now also runs as a subprocess invoked by Dagster

from google import genai
from google.genai import types
from google.cloud import bigquery
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini_ingestion")

# ---- Config (env-driven, never hardcode secrets) ----------------------------
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]  # fails loudly if unset — good
BQ_PROJECT = os.environ.get("BQ_PROJECT", "n8n-self-practice")
BQ_DATASET = os.environ.get("BQ_DATASET", "raw")
TARGET_TABLE = f"{BQ_PROJECT}.{BQ_DATASET}.gemini_enriched"
FAILED_TABLE = f"{BQ_PROJECT}.{BQ_DATASET}.failed_llm_calls"
MODEL_NAME = "gemini-3.5-flash"  # verified live — gemini-1.5-flash is deprecated/404s

bq_client = bigquery.Client(project=BQ_PROJECT)
genai_client = genai.Client(api_key=GEMINI_API_KEY)


# ---- Expected shape of Gemini's output ---------------------------------------
class EnrichmentResult(BaseModel):
    category: str
    summary: str
    confidence: float


@dataclass
class InputRecord:
    input_id: str
    text: str


def _input_hash(record: InputRecord) -> str:
    """Dedup key: based on the INPUT, never the LLM output (non-deterministic)."""
    return hashlib.sha256(f"{record.input_id}:{record.text}".encode()).hexdigest()


class GeminiTransientError(Exception):
    """Raised for retryable failures (timeouts, 429s, 5xxs)."""


class GeminiFatalError(Exception):
    """
    Raised for errors that are the SAME for every record in the batch —
    invalid/expired API key, permission denied, quota exhausted at the
    project level. These must NOT be swallowed into failed_llm_calls
    per-record, because that would silently misreport "500 records had
    bad content" when the real story is "the key was bad the whole run."
    process_batch lets this propagate and stops the batch immediately.
    """


# ---- Step 1: call Gemini, with bounded retry/backoff -------------------------
@retry(
    retry=retry_if_exception_type(GeminiTransientError),
    stop=stop_after_attempt(4),
    wait=wait_exponential_jitter(initial=2, max=30),
    reraise=True,
)
def call_gemini(record: InputRecord) -> dict:
    """
    Calls Gemini via the current google-genai SDK, with structured JSON
    output enforced by the API itself (response_schema) rather than
    hoping the model returns parseable free text.
    """
    try:
        response = genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=(
                f"Categorize and summarize this text.\n\n{record.text}"
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EnrichmentResult,
            ),
        )
    except Exception as e:
        msg = str(e)
        # Fatal, batch-wide problems — same for every record, don't retry,
        # don't log per-record, stop the whole run and surface it loudly.
        if (
            "API_KEY_INVALID" in msg
            or "PERMISSION_DENIED" in msg
            or "API key not valid" in msg
            or "RESOURCE_EXHAUSTED" in msg  # project-level quota, not per-call rate limit
        ):
            raise GeminiFatalError(msg) from e
        # Transient, per-call problems -> safe to retry.
        if "429" in msg or "timeout" in msg.lower() or "503" in msg or "UNAVAILABLE" in msg:
            raise GeminiTransientError(msg) from e
        raise

    return json.loads(response.text)


# ---- Step 2: validate the shape before trusting it ---------------------------
def validate_response(raw: dict) -> Optional[EnrichmentResult]:
    try:
        return EnrichmentResult.model_validate(raw)
    except ValidationError as e:
        logger.warning("Gemini response failed schema validation: %s", e)
        return None


# ---- Step 3: dedup check against BigQuery ------------------------------------
def already_ingested(input_hash: str) -> bool:
    query = f"""
        SELECT 1 FROM `{TARGET_TABLE}`
        WHERE input_hash = @input_hash
        LIMIT 1
    """
    job = bq_client.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("input_hash", "STRING", input_hash)
            ]
        ),
    )
    return job.result().total_rows > 0


# ---- Step 4: write to BigQuery (success or failure path) --------------------
def write_success(record: InputRecord, input_hash: str, result: EnrichmentResult):
    row = {
        "input_id": record.input_id,
        "input_hash": input_hash,
        "category": result.category,
        "summary": result.summary,
        "confidence": result.confidence,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    errors = bq_client.insert_rows_json(TARGET_TABLE, [row])
    if errors:
        raise RuntimeError(f"BQ insert failed: {errors}")


def write_failure(record: InputRecord, input_hash: str, reason: str, raw: dict | None):
    row = {
        "input_id": record.input_id,
        "input_hash": input_hash,
        "reason": reason,
        "raw_response": json.dumps(raw) if raw else None,
        "failed_at": datetime.now(timezone.utc).isoformat(),
    }
    errors = bq_client.insert_rows_json(FAILED_TABLE, [row])
    if errors:
        logger.error("Even the failure log insert failed: %s", errors)


# ---- Orchestrating function — this is what the Dagster asset calls ----------
def process_record(record: InputRecord) -> str:
    """Returns one of: 'inserted', 'skipped_duplicate', 'failed_validation', 'failed_api'."""
    input_hash = _input_hash(record)

    if already_ingested(input_hash):
        logger.info("Skipping duplicate input_id=%s", record.input_id)
        return "skipped_duplicate"

    try:
        raw = call_gemini(record)
    except GeminiFatalError:
        # Don't log this as a per-record failure — re-raise so process_batch
        # (or whatever caller) stops the run instead of misattributing a
        # project-wide problem to this one record's content.
        raise
    except GeminiTransientError as e:
        write_failure(record, input_hash, f"api_error_after_retries: {e}", None)
        return "failed_api"

    result = validate_response(raw)
    if result is None:
        write_failure(record, input_hash, "schema_validation_failed", raw)
        return "failed_validation"

    write_success(record, input_hash, result)
    return "inserted"


def process_batch(records: list[InputRecord]) -> dict:
    """Runs process_record over a batch, returns a summary count. This is
    what the Dagster asset actually invokes and logs as metadata."""
    summary = {"inserted": 0, "skipped_duplicate": 0, "failed_validation": 0, "failed_api": 0}
    for i, record in enumerate(records):
        try:
            status = process_record(record)
        except GeminiFatalError as e:
            logger.error(
                "FATAL: stopping batch after %d/%d records — %s",
                i, len(records), e,
            )
            summary["fatal_error"] = str(e)
            summary["processed_before_fatal"] = i
            return summary
        summary[status] += 1
    logger.info("Batch summary: %s", summary)
    return summary
