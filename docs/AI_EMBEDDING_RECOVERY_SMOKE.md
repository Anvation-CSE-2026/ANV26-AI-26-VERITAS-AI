# Ollama configuration recovery and single live smoke test

Run UTC: 2026-10-08T15:57:58.106741+00:00. Branch: feature/ai-reliability. Exactly one live contract evaluation was executed; no full benchmark, automatic evaluation retry, commit or push.

## Configuration diagnosis

The actual backend setting was http://localhost, sourced from backend/.env, with no process override. It omitted port 11434 and overrode the correct application default http://localhost:11434. The original direct backend request failed with connection refusal (WinError 10061). Only OLLAMA_BASE_URL in backend/.env was corrected to http://localhost:11434. No production pipeline, authentication, billing or frontend code changed.

The existing embedding service then succeeded using POST /api/embed and qwen3-embedding:0.6b, yielding 1024 dimensions. Its connect/read timeouts remain 5/120 seconds and trust_env=False. Gemini metadata GET confirmed models/gemini-3.5-flash is accessible and supports generateContent; no generation was used for that preflight. All 12 PDFs and 42 gold annotations validated before the run.

## Exact evaluation command

From backend:

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live --limit 1
```

## Actual results

- Contract ID: SYN-supplier_red.
- Analysis ID: a1aaa7af-7bfc-432c-abc1-abbd4d474f9d.
- Status: partial; CLI exit 0 means the benchmark completed without a failed analysis, not that every proposal passed verification.
- Gemini reached: yes. Configured and actual response model: gemini-3.5-flash.
- Gemini generation attempts: 1; no request retry occurred.
- Proposed findings: 7; retained: 5; rejected: 2. These counts are inferred from returned records plus production rejection metadata; discarded raw findings are not exposed.
- Rejected obligations: 2; retained obligation count is not exposed by this benchmark report.
- Exact and normalized quote match: 1/1 retained quote-eligible finding. Exact cited-page verification: 1/1.
- Four retained policy-only omission candidates have no quote and do not establish verified absence.
- Unsupported finding count: 2, all from production rejections; verification failure rate 2/7 = 28.57%. Rejected raw quotation details/reasons are not preserved by the adapter, so their precise rejection causes cannot be reconstructed from this report.
- Processing latency: 48.6054 seconds, including extraction, actual retrieval/reasoning, verification and temporary SQLite persistence/retrieval.
- Token usage and API cost: N/A; the production result does not expose them.

## Risk scoring against current gold

TP 2, FP 3, FN 1; precision 40.00%, recall 66.67%, F1 50.00%. Liability and the annotated missing termination target matched; indemnification was missed in the returned output. Three other omission predictions were unmatched and scored as FPs under the existing gold inventory. The inventory is sparse: unannotated categories/omission claims require manual review, and these FPs are not proof that the legal interpretations are incorrect. Gold was not changed to fit this result. A single smoke contract is not a stable Gemini accuracy baseline.

## Preservation and limits

Post-run hash checks confirm application source, production SQLite and gold manifest unchanged. The application database is not the benchmark database; temporary SQLite is removed after the run, and this analysis ID is retained in reports rather than the production API. The prior live report files were overwritten by the documented default runner; the earlier failure remains documented in docs/AI_LIVE_SMOKE_REPORT.md.

Partial status reflects rejected records and potential omissions requiring human review. Request/pipeline connectivity passed after configuration repair. No further external requests or evaluations were launched after completion. Do not proceed automatically to all 12; review rejected-record diagnostics and unannotated omission targets before authorizing a broader run.

## Files changed in this task

- backend/.env: corrected only OLLAMA_BASE_URL (credentials not disclosed).
- backend/evaluation/reports/embedding-recovery-preflight.json: new sanitized checks and preservation hashes.
- backend/evaluation/reports/synthetic_v1-live.json: updated single-contract live report.
- backend/evaluation/reports/synthetic_v1-live.csv: updated summary.
- backend/evaluation/reports/synthetic_v1-live.md: updated summary.
- docs/AI_EMBEDDING_RECOVERY_SMOKE.md: this report.

Temporary diagnostic Python helpers were removed. No production code changes or gold edits.
