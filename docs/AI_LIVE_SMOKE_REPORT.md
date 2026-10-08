# Controlled live benchmark smoke test

Branch: feature/ai-reliability. Run UTC: 2026-10-08T15:15:46.552342+00:00. Exactly one analysis was attempted; no full benchmark and no repeat smoke run.

## Audit

- Explicit --live is required; --limit 1 selects only SYN-supplier_red. The loader validates unique contract IDs and the adapter calls analyze_contract once per selected contract; only bounded provider request retries may occur inside that analysis.
- Uses existing production extraction, Ollama retrieval, Gemini structured reasoning, deterministic evidence verification and SQLite persistence/retrieval functions. No prompts or pipeline changes.
- Standalone process redirects storage to temporary SQLite and restores settings in finally. Original application database and all application source hashes remained unchanged after this attempt.
- Calls the analysis service directly, not authenticated or billing routes. No Razorpay operations or usage/quota billing operations are called. Shared storage creates empty schema tables only in temporary SQLite.
- Metadata is a configuration whitelist; exceptions are sanitized; no API keys or complete contract text are printed.
- Effective Gemini limits: 3 attempts, 90 seconds per request; bounded retry backoff and SDK retries disabled. Ollama connect/read timeouts: 5/120 seconds, no application embedding retry. These are request timeouts, not an absolute whole-run deadline.
- Ctrl+C propagates KeyboardInterrupt and runs storage/client context cleanup; it cannot undo sent requests or charges. No interruption checkpoint/report is guaranteed, and force-killing may leave temporary files. Production storage remains isolated.

## Gold validation

All 12 PDFs round-tripped to canonical extracted text. 42 valid annotations, 42 unique IDs, 40 exact gold evidence spans with correct 1-based pages and source clause offsets. Three missing annotations contain no invented quote; one cross-page target has two spans. The authored builder's label definitions are separate from canned prediction plans and contain no model calls. This establishes repository provenance, not independent human/legal validation; all labels remain pending review. Labels were not changed. Manifest hash unchanged.

Governing law: 4 annotations, including 2 definite positives; separately identified as unsupported in metadata/per-category reporting. Full-dataset aggregates currently include this unsupported category and must not be interpreted as seven-category model-only accuracy. The selected smoke contract contains no governing-law annotation.

## Exact command

Working directory: backend.

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live --limit 1
```

CLI exit: 1 (failed analysis, reports successfully written).

## Observed result

- Configured model: gemini-3.5-flash; actual Gemini response model: N/A, Gemini was not reached.
- Contract ID: SYN-supplier_red.
- Analysis ID: 547cd69a-d1ec-49a0-888c-a44c32ed19bb.
- Status: failed.
- Failing stage: policy_retrieval.
- Error category: embedding_connection.
- Recorded backend HTTP status: 503; upstream HTTP status: N/A (connection failure, not an upstream HTTP response).
- Gemini generation attempts: 0; no Gemini retries or generation calls occurred.
- Findings: 0; rejected findings/obligations: 0/0.
- Evidence quotation and page verification rates: N/A; no generated findings to verify. Zero unsupported count is an empty result, not successful verification.
- Failure recorded and retrieved in isolated SQLite: true. Temporary database was removed when the run exited; the JSON report retains the failure details, and this ID is not a production API record.
- Measured failed-pipeline latency: 4.1492 seconds; runner overhead-inclusive duration: 4.6337 seconds.
- Token usage and full-12-contract estimated API cost: N/A. Production analysis results do not expose token usage/pricing, and no successful Gemini response was observed. No Gemini generation cost was incurred by this attempt because it failed before generation.

End-to-end scoring correctly counted the three gold positives as missed (TP 0, FP 0, FN 3). F1/recall zero here measure pipeline unavailability, not Gemini reasoning accuracy.

## Problems and recommendation

Ollama was unreachable from this process. The report alone does not establish whether it is stopped, misconfigured or otherwise inaccessible; no extra service request or automatic restart was attempted after the smoke test.

Other measurement limits: raw rejected predictions and token usage unavailable; source-target matching does not verify interpretation; gold is pending review; unsupported governing-law targets affect full aggregates; report metadata live_services_used describes selected mode, not proof that both providers were reached.

Recommendation: do not proceed to all 12. Restore Ollama connectivity, then obtain approval for another single-contract test and require successful retrieval, Gemini output and evidence verification before approving the full benchmark. No frontend, authentication, Razorpay, production AI logic or gold changes; no commits or pushes.

Artifacts: backend/evaluation/reports/synthetic_v1-live.json, .csv, .md and smoke-audit.json.
