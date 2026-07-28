# STRIDE Threat Model — Gemini Enrichment Asset (Module 5/7)

Scope: gemini_asset.py (Dagster, main venv) -> subprocess bridge ->
gemini_batch_runner.py (venv-gemini) -> Gemini API -> BigQuery
(raw.gemini_enriched, raw.failed_llm_calls, raw.pending_enrichment).

| Threat | Category | Applies here? | Mitigation status |
|---|---|---|---|
| Free-text input contains prompt-injection payload aimed at altering model behavior or exfiltrating system prompt | Tampering | Yes | Not tested yet - see adversarial test file (next step) |
| raw.failed_llm_calls.raw_response stores full Gemini response verbatim, may contain PII echoed from input | Information Disclosure | Yes | Not mitigated - flagged as a known gap, not fixed in this pass |
| Malformed/adversarial input causes uncontrolled retry loop leading to cost spike | Denial of Service (cost-based) | Yes - no budget ceiling exists today | Being fixed this module - cost tracker with hard budget cutoff |
| Low-confidence LLM output written straight to gemini_enriched and consumed by dbt without human review | Repudiation / bad data treated as ground truth | Yes | Being fixed this module - HITL queue for confidence below 0.7 |
| GEMINI_API_KEY exposure via subprocess env inheritance or logs | Information Disclosure | .env is gitignored, 600 perms, confirmed never committed (Module 5) | Not re-verified in this pass |
| Gemini API outage or auth failure cascading into silent data gaps | Denial of Service | Yes | Already handled - GeminiFatalError (Module 5) |

Honest gap, stated plainly: redaction of raw_response before storage is
identified but NOT implemented in this pass.
