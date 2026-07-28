"""
Minimal HITL review CLI for raw.hitl_review_queue.
Usage: python hitl_cli.py
Run from main venv (uses google-cloud-bigquery).
"""
from google.cloud import bigquery
from datetime import datetime, timezone

client = bigquery.Client()

def review_pending(limit=10):
    query = """
        SELECT input_id, text, category, summary, confidence, queued_at
        FROM `raw.hitl_review_queue`
        WHERE reviewed = FALSE
        ORDER BY queued_at ASC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("limit", "INT64", limit)]
    )
    rows = list(client.query(query, job_config=job_config).result())

    if not rows:
        print("No pending reviews.")
        return
    for row in rows:
        print(f"\n--- {row.input_id} (confidence: {row.confidence:.2f}) ---")
        print(f"Text: {row.text[:200]}")
        print(f"Category: {row.category} | Summary: {row.summary}")
        decision = input("Approve / Reject / Skip [a/r/s]: ").strip().lower()
        if decision in ("a", "r"):
            update = """
                UPDATE `raw.hitl_review_queue`
                SET reviewed = TRUE, decision = @decision, reviewed_at = @now
                WHERE input_id = @input_id
            """
            client.query(update, job_config=bigquery.QueryJobConfig(query_parameters=[
                bigquery.ScalarQueryParameter("decision", "STRING", "approved" if decision == "a" else "rejected"),
                bigquery.ScalarQueryParameter("now", "TIMESTAMP", datetime.now(timezone.utc).isoformat()),
                bigquery.ScalarQueryParameter("input_id", "STRING", row.input_id),
            ])).result()
            print(f"  -> recorded as {'approved' if decision=='a' else 'rejected'}")

if __name__ == "__main__":
    review_pending()
