"""
Runs INSIDE venv-gemini. Never imported directly by Dagster (which lives in
the main venv and doesn't have the Gemini SDK installed — protobuf conflict).

Contract:
    stdin  = JSON list of {"input_id": ..., "text": ...}
    stdout = single JSON object: the process_batch() summary dict
             (all logging goes to stderr, so stdout stays clean JSON)

Called via subprocess from orchestration/orchestration/gemini_asset.py like:
    venv-gemini/bin/python gemini_batch_runner.py < records.json
"""

import json
import logging
import sys

# Redirect gemini_ingestion's logging to stderr, so stdout is pure JSON
# that the parent process (Dagster, in the other venv) can safely parse.
logging.basicConfig(level=logging.INFO, stream=sys.stderr)

from gemini_ingestion import InputRecord, process_batch


def main():
    raw_input_data = sys.stdin.read()
    records_data = json.loads(raw_input_data)

    records = [
        InputRecord(input_id=r["input_id"], text=r["text"]) for r in records_data
    ]

    summary = process_batch(records)

    # Only this line goes to stdout — everything else (logging) is on stderr.
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
