"""
Schema-validation failure test.

Doesn't call the real Gemini API — monkeypatches call_gemini() to return
a deliberately malformed response (missing required field), and confirms
process_record correctly routes it to failed_validation / failed_llm_calls
instead of crashing or silently dropping it.
"""

import gemini_ingestion
from gemini_ingestion import InputRecord


def fake_call_missing_field(record):
    return {"category": "Test", "summary": "Missing confidence field"}


def fake_call_wrong_type(record):
    return {"category": "Test", "summary": "Wrong type", "confidence": "high"}


def run_case(name, fake_fn, input_id):
    original = gemini_ingestion.call_gemini
    gemini_ingestion.call_gemini = fake_fn
    try:
        result = gemini_ingestion.process_record(
            InputRecord(input_id=input_id, text="irrelevant for this test")
        )
        expected = "failed_validation"
        status = "PASS" if result == expected else "FAIL"
        print(f"[{status}] {name}: got '{result}', expected '{expected}'")
    finally:
        gemini_ingestion.call_gemini = original


if __name__ == "__main__":
    run_case("missing required field", fake_call_missing_field, "test-schema-001")
    run_case("wrong field type", fake_call_wrong_type, "test-schema-002")

    print("\nNow check BigQuery — both rows should appear in failed_llm_calls:")
    print(
        "  bq query --use_legacy_sql=false "
        "'SELECT input_id, reason, raw_response FROM "
        "`n8n-self-practice.raw.failed_llm_calls` "
        "WHERE input_id IN (\"test-schema-001\", \"test-schema-002\")'"
    )
