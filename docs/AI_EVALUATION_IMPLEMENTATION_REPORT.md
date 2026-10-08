# VERITAS AI evaluation implementation report

Completed 2026-10-08. The benchmark is built and validated offline. **No live Gemini or Ollama calls were made, and no API evaluation charges were incurred.** Live execution awaits user approval.

## Files created

All implementation changes are new files: 55 under `backend/evaluation/`, `tests/test_evaluation.py`, and the two documentation files in this section. Existing application/frontend file hashes were compared for 4,577 files; none changed. Model settings, prompts, authentication, Razorpay, subscriptions, existing tests and production database were not edited or reset. No dependency changes were needed.

Benchmark files:

- `backend/evaluation/build_fixtures.py`
- `backend/evaluation/dataset_loader.py`
- `backend/evaluation/evaluator.py`
- `backend/evaluation/evidence_metrics.py`
- `backend/evaluation/fixtures/annotations/consulting_owned.json`
- `backend/evaluation/fixtures/annotations/consulting_retained.json`
- `backend/evaluation/fixtures/annotations/nda_durable.json`
- `backend/evaluation/fixtures/annotations/nda_short.json`
- `backend/evaluation/fixtures/annotations/saas_green.json`
- `backend/evaluation/fixtures/annotations/saas_red.json`
- `backend/evaluation/fixtures/annotations/services_balanced.json`
- `backend/evaluation/fixtures/annotations/services_exit.json`
- `backend/evaluation/fixtures/annotations/services_split.json`
- `backend/evaluation/fixtures/annotations/supplier_failure.json`
- `backend/evaluation/fixtures/annotations/supplier_green.json`
- `backend/evaluation/fixtures/annotations/supplier_red.json`
- `backend/evaluation/fixtures/benchmark_playbook.json`
- `backend/evaluation/fixtures/contracts/consulting_owned.json`
- `backend/evaluation/fixtures/contracts/consulting_owned.pdf`
- `backend/evaluation/fixtures/contracts/consulting_retained.json`
- `backend/evaluation/fixtures/contracts/consulting_retained.pdf`
- `backend/evaluation/fixtures/contracts/nda_durable.json`
- `backend/evaluation/fixtures/contracts/nda_durable.pdf`
- `backend/evaluation/fixtures/contracts/nda_short.json`
- `backend/evaluation/fixtures/contracts/nda_short.pdf`
- `backend/evaluation/fixtures/contracts/saas_green.json`
- `backend/evaluation/fixtures/contracts/saas_green.pdf`
- `backend/evaluation/fixtures/contracts/saas_red.json`
- `backend/evaluation/fixtures/contracts/saas_red.pdf`
- `backend/evaluation/fixtures/contracts/services_balanced.json`
- `backend/evaluation/fixtures/contracts/services_balanced.pdf`
- `backend/evaluation/fixtures/contracts/services_exit.json`
- `backend/evaluation/fixtures/contracts/services_exit.pdf`
- `backend/evaluation/fixtures/contracts/services_split.json`
- `backend/evaluation/fixtures/contracts/services_split.pdf`
- `backend/evaluation/fixtures/contracts/supplier_failure.json`
- `backend/evaluation/fixtures/contracts/supplier_failure.pdf`
- `backend/evaluation/fixtures/contracts/supplier_green.json`
- `backend/evaluation/fixtures/contracts/supplier_green.pdf`
- `backend/evaluation/fixtures/contracts/supplier_red.json`
- `backend/evaluation/fixtures/contracts/supplier_red.pdf`
- `backend/evaluation/fixtures/manifest.json`
- `backend/evaluation/fixtures/predictions.json`
- `backend/evaluation/live_adapter.py`
- `backend/evaluation/offline_guard.py`
- `backend/evaluation/README.md`
- `backend/evaluation/reports/offline-tests.json`
- `backend/evaluation/reports/synthetic_v1-fixture.csv`
- `backend/evaluation/reports/synthetic_v1-fixture.json`
- `backend/evaluation/reports/synthetic_v1-fixture.md`
- `backend/evaluation/risk_metrics.py`
- `backend/evaluation/runner.py`
- `backend/evaluation/run_offline_tests.py`
- `backend/evaluation/schema.py`
- `backend/evaluation/__init__.py`

Additional files:

- `tests/test_evaluation.py`
- `docs/AI_EVALUATION_METHODOLOGY.md`
- `docs/AI_EVALUATION_IMPLEMENTATION_REPORT.md`

## Architecture and dataset

Independent schemas, verified PDF/source dataset loader, deterministic evidence metrics, one-to-one risk matching, aggregation and an offline-default CLI. JSON/CSV/Markdown reports record source/config/prompt hashes, provenance and failures without full quoted contract text or secrets. A lazy, explicit `--live` adapter reuses the production service pipeline in an isolated temporary SQLite database; it has not been exercised against providers in this task.

Twelve original synthetic agreements: supplier (3), SaaS (2), NDA (2), services (3), consulting (2). Forty-two gold annotations: 21 present risks, 3 missing requirements, 14 non-risk targets and 4 ambiguous targets. Covers all eight requested categories, includes a two-page target and opposing-looking indemnity/IP clauses. Gold is hand-authored, pending independent manual review and not legally validated. Frozen sample playbook plus a distinctly marked benchmark-only governing-law assumption are preserved.

## Metrics implemented

Category-independent target detection TP/FP/FN, precision/recall/F1; per-category classification counts, macro/micro F1; category/severity accuracy and confusion on matched positives; independently supported-evidence detection; exact/normalized quote rates; exact/normalized cited-page rates; unsupported evidence count/rate; rejected obligations; failed/partial statuses and error breakdown; unmatched predictions/missed gold; observed latency and usage/cost availability. Zero denominators and unavailable measurements use null/N/A. Failed analyses remain failures and contribute missed risks.

## Measured offline fixture results

**These are intentionally imperfect canned-prediction results, not Gemini accuracy or provider reliability.**

| Measurement | Result |
|---|---:|
| Contracts | 12 |
| Annotated risks (including missing) | 24 |
| TP / FP / FN | 17 / 3 / 7 |
| Detection precision | 85.00% |
| Detection recall | 70.83% |
| Detection F1 | 77.27% |
| Classification micro F1 | 72.73% |
| Classification macro F1 | 71.88% |
| Category accuracy on matched targets | 94.12% |
| Severity accuracy on matched targets | 88.24% |
| Supported-evidence detection F1 | 66.67% |
| Returned findings / quote-eligible / omission candidates | 21 / 19 / 2 |
| Exact quote match | 84.21% |
| Normalized quote match | 89.47% |
| Exact correct cited page | 78.95% |
| Normalized correct cited page | 84.21% |
| Unsupported evidence | 6 (5 returned + 1 simulated rejection) |
| Unsupported evidence rate | 27.27% |
| Simulated completed / partial / failed | 10 / 1 / 1 |
| Actual model latency / tokens / estimated API cost | N/A / N/A / N/A |

Per-category classification:

| Category | TP | FP | FN | F1 |
|---|---:|---:|---:|---:|
| liability | 3 | 2 | 1 | 66.67% |
| indemnification | 1 | 0 | 1 | 66.67% |
| termination | 2 | 0 | 2 | 66.67% |
| payment | 2 | 1 | 1 | 66.67% |
| confidentiality | 3 | 0 | 0 | 100.00% |
| data_protection | 3 | 1 | 1 | 75.00% |
| intellectual_property | 1 | 0 | 1 | 66.67% |
| governing_law | 1 | 0 | 1 | 66.67% |

The simulated failure is `SYN-supplier_failure`, Gemini reasoning stage, category `fixture_provider_transient`, HTTP/upstream 503 and three canned attempts. This was not a real request. The partial fixture is `SYN-services_split`, with one simulated evidence rejection. Quote denominators exclude missing records and unavailable raw rejected quotes. Full IDs, reason codes, matching details and conditional confusion matrices are in the JSON report.

## Tests and preservation

The complete backend suite ran with live opt-ins disabled and outbound network blocked. **106 tests discovered: 103 passed, 3 live-service tests skipped, 0 failures, 0 errors.** This comprises 32 new benchmark tests and 71 passing existing tests, including authentication/billing/quota regressions. Existing three live integration tests stayed skipped.

Validation includes PDF/source round-trip, valid/invalid quotes/pages/clauses/policies, whitespace diagnostics, omissions, duplicate/maximal matching, missing risks, false positives, ambiguous targets, category/severity separation, empty/zero-denominator cases, failed/partial output, malformed gold, integrity tampering, complete CSV reporting and explicit tests that the network guard rejects Ollama/external connects while allowing Windows asyncio internals. The fixture builder was rerun separately to verify byte-identical regeneration of all 39 fixture files.

During validation, the Windows network guard was corrected to support internal socketpair creation and nested guards; the final suite passes. A pre-existing Starlette TestClient/HTTPX deprecation warning remains non-blocking.

Reports: `backend/evaluation/reports/synthetic_v1-fixture.json`, `.csv`, `.md` and `offline-tests.json`.

## Live results and remaining limits

**Live model evaluation: not run.** Effective configuration loads `gemini-3.5-flash` and `qwen3-embedding:0.6b`; the key-present boolean was checked without exposing its value. Provider connectivity, real model scores, real benchmark latency and API charges were not tested. There is no live baseline report.

Production currently supports seven categories; governing law is a documented gap and is not silently added to the engine. Other limits: small short-text synthetic PDFs, unreviewed author labels, source-target matching rather than legal entailment, raw rejected predictions unavailable, no OCR/multilingual evaluation, no production token/cost telemetry and no confidence intervals. Exact evidence does not prove an interpretation correct.

Recommended next steps: independent label review/adjudication, approved one-contract live smoke run followed by the full baseline, larger untouched holdout and variance runs, richer issue-span matching, and separately authorized usage/rejection telemetry and obligation/retrieval metrics. No prompts or models were tuned.

## Repeat commands

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --dry-run
.\.venv\Scripts\python.exe -m evaluation.run_offline_tests
```

After explicit user approval only (not executed):

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live --limit 1
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live
```
