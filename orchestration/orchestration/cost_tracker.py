"""
Cost/latency tracking wrapper for Gemini calls, plus a hard per-run
budget ceiling. Wraps whatever call function you pass in - does not
call Gemini itself, so it works from either venv.
"""
import uuid
from datetime import datetime, timezone
from google.cloud import bigquery

COST_PER_1K_INPUT_TOKENS = 0.000075
COST_PER_1K_OUTPUT_TOKENS = 0.0003
BUDGET_CEILING_USD = 1.00


class BudgetExceededError(Exception):
    """Raised when a batch run would exceed BUDGET_CEILING_USD."""


class CostTracker:
    def __init__(self, run_id=None):
        self.run_id = run_id or str(uuid.uuid4())
        self.total_cost_usd = 0.0
        self.client = bigquery.Client()

    def check_before_call(self):
        """Call BEFORE hitting the API — stops the next call outright if
        the budget is already exhausted, so we don't spend money just to
        find out afterward."""
        if self.total_cost_usd >= BUDGET_CEILING_USD:
            raise BudgetExceededError(
                f"Run {self.run_id} already at/over ${BUDGET_CEILING_USD:.2f} "
                f"ceiling (${self.total_cost_usd:.6f}) — refusing further API calls."
            )

    def record_call(self, input_tokens, output_tokens, latency_ms, record_id, status):
        cost = (input_tokens / 1000 * COST_PER_1K_INPUT_TOKENS
                + output_tokens / 1000 * COST_PER_1K_OUTPUT_TOKENS)
        self.total_cost_usd += cost

        if self.total_cost_usd > BUDGET_CEILING_USD:
            raise BudgetExceededError(
                f"Run {self.run_id} exceeded ${BUDGET_CEILING_USD:.2f} ceiling "
                f"at record {record_id} (running total ${self.total_cost_usd:.4f})"
            )

        row = {
            "run_id": self.run_id,
            "record_id": record_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
            "latency_ms": latency_ms,
            "status": status,
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }
        errors = self.client.insert_rows_json("raw.llm_cost_log", [row])
        if errors:
            raise RuntimeError(f"Cost log insert failed: {errors}")

    def summary(self):
        return {"run_id": self.run_id, "total_cost_usd": round(self.total_cost_usd, 8)}
