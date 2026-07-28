"""
Dagster asset — lives in the MAIN venv (has dagster, dagster-dbt).
Does NOT import gemini_ingestion directly — that module needs the Gemini SDK,
which conflicts with dbt's protobuf requirement in this venv (verified,
not assumed). Instead, delegates to a subprocess running in venv-gemini.
"""

import json
import subprocess

from dagster import asset, AssetExecutionContext, MetadataValue
from google.cloud import bigquery

VENV_GEMINI_PYTHON = "/home/muhammad/n8n-practice/venv-gemini/bin/python"
MY_PROJECT_DIR = "/home/muhammad/n8n-practice/my_project"
RUNNER_SCRIPT = f"{MY_PROJECT_DIR}/gemini_batch_runner.py"

BQ_PROJECT = "n8n-self-practice"


@asset(
    group_name="ingestion",
    description=(
        "Fetches unprocessed records from raw.pending_enrichment, enriches "
        "via Gemini API (in an isolated venv-gemini subprocess due to a "
        "protobuf dependency conflict with dbt), validates schema, dedups "
        "against BigQuery, and lands results in raw.gemini_enriched. "
        "Upstream of dbt staging models."
    ),
)
def gemini_enriched_records(context: AssetExecutionContext):
    bq_client = bigquery.Client(project=BQ_PROJECT)

    rows = list(
        bq_client.query(
            f"SELECT id AS input_id, text FROM `{BQ_PROJECT}.raw.pending_enrichment`"
        ).result()
    )
    records = [{"input_id": r.input_id, "text": r.text} for r in rows]

    context.log.info(f"Fetched {len(records)} records from pending_enrichment")

    if not records:
        context.add_output_metadata({"note": MetadataValue.text("No pending records")})
        return {"inserted": 0, "skipped_duplicate": 0, "failed_validation": 0, "failed_api": 0}

    result = subprocess.run(
        [VENV_GEMINI_PYTHON, RUNNER_SCRIPT],
        input=json.dumps(records),
        capture_output=True,
        text=True,
        cwd=MY_PROJECT_DIR,
        timeout=600,
    )

    if result.stderr:
        context.log.info(f"venv-gemini subprocess log:\n{result.stderr}")

    if result.returncode != 0:
        raise RuntimeError(
            f"Gemini subprocess exited with code {result.returncode}. "
            f"stderr:\n{result.stderr}"
        )

    try:
        summary = json.loads(result.stdout.strip())
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Could not parse subprocess stdout as JSON: {e}\nRaw stdout: {result.stdout}"
        ) from e

    context.add_output_metadata(
        {
            "inserted": MetadataValue.int(summary.get("inserted", 0)),
            "skipped_duplicate": MetadataValue.int(summary.get("skipped_duplicate", 0)),
            "failed_validation": MetadataValue.int(summary.get("failed_validation", 0)),
            "failed_api": MetadataValue.int(summary.get("failed_api", 0)),
        }
    )

    if "fatal_error" in summary:
        raise RuntimeError(
            f"Batch halted after {summary.get('processed_before_fatal', '?')} records: "
            f"{summary['fatal_error']}"
        )

    total = (
        summary.get("inserted", 0)
        + summary.get("skipped_duplicate", 0)
        + summary.get("failed_validation", 0)
        + summary.get("failed_api", 0)
    )
    failed = summary.get("failed_validation", 0) + summary.get("failed_api", 0)
    if total > 0 and failed / total > 0.3:
        raise RuntimeError(
            f"Failure rate {failed}/{total} exceeds 30% threshold — "
            "check failed_llm_calls table before re-running."
        )

    return summary
