# VERITAS AI reliability benchmark

This package evaluates **original synthetic contracts**. It defaults to canned predictions and never calls Gemini or Ollama on the fixture path. No model accuracy baseline has been measured by this work.

Run from the project root in PowerShell:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --dry-run
.\.venv\Scripts\python.exe -m evaluation.run_offline_tests
```

Omitting `--dry-run` also uses fixtures. `--limit 1` selects the first contract. `--output <directory>` selects the report directory. Fixture analyses include intentional failures; a successful fixture evaluation returns exit code 0. Exit code 2 means the benchmark itself failed. A live run with failed analyses returns 1 while still producing reports.

**Do not execute the following until the user approves live API charges.** The explicit flag enables real Gemini and Ollama requests using current backend configuration:

```powershell
# From backend, AFTER explicit approval:
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live --limit 1
# Full approved benchmark:
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live
```

Live evaluation reuses production extraction, retrieval, Gemini analysis, evidence verification and SQLite persistence/retrieval. It uses a temporary benchmark SQLite database; existing users, subscriptions, quotas, payments and application records remain untouched. This is a service-level evaluation, not an authenticated HTTP/billing evaluation. Run it as a standalone process; it temporarily changes only that process's storage setting and restores it in a finally block.

The live adapter has **not** been executed against external services in this task. Fixtures validate the evaluator, not provider integration.

## Files

- `schema.py`: independent gold, prediction and outcome records (eight categories).
- `dataset_loader.py`: hashes, original PDF extraction round-trip, page/offset/ID/gold validation.
- `build_fixtures.py`: explicit original source text, author annotations and separate faulty prediction plans. Offline; no SDK clients.
- `evidence_metrics.py`: literal exact/whitespace and page/clause/policy checks.
- `risk_metrics.py`: maximum-cardinality one-to-one source-target matching and separate category/severity scoring.
- `evaluator.py`: aggregation, failures, usage availability and latency.
- `runner.py`: default offline CLI, metadata and JSON/CSV/Markdown reports.
- `live_adapter.py`: lazy-loaded, explicit opt-in reuse of the production pipeline.
- `offline_guard.py`, `run_offline_tests.py`: block outbound sockets during all regression tests, disable live opt-ins; allow only Windows stdlib internal socketpair creation.
- `fixtures/contracts/`: 12 PDFs and canonical extracted-text JSON records.
- `fixtures/annotations/`: 12 manually reviewable reference files.
- `fixtures/benchmark_playbook.json`: snapshot of production sample policy and separately marked benchmark-only governing-law assumption.
- `fixtures/predictions.json`: deliberately imperfect evaluator inputs, not Gemini output.
- `fixtures/manifest.json`: dataset version, provenance and SHA-256 digests.
- `reports/synthetic_v1-fixture.{json,csv,md}`: offline fixture baseline.
- `reports/offline-tests.json`: actual regression result counts.

To rebuild the fixtures deliberately:

```powershell
.\.venv\Scripts\python.exe -m evaluation.build_fixtures
```

Review changes to source, labels and hashes before accepting a dataset revision. PDFs use fixed metadata and no random file ID. Gold quotes preserve PyMuPDF extraction including line wraps; pages are 1-based.

Gold labels are author judgments under explicit synthetic company assumptions, **pending manual review and not legally validated**. Governing law is benchmark-only: production currently has no category or rule for it. The benchmark does not change production prompts, models or logic to conceal this gap.

See [methodology](../../docs/AI_EVALUATION_METHODOLOGY.md) for formulas, denominators, matching limits, current architecture and live-result caveats; see [implementation report](../../docs/AI_EVALUATION_IMPLEMENTATION_REPORT.md) for measured offline results.

## Optional synthetic observability

Tracing is disabled by default. The existing live command continues to use the same analysis/scoring behavior. **No live evaluation was run to implement observability.**

After separately approving a live test, explicitly enable private synthetic traces:

```powershell
# From backend; DO NOT run without approval for live calls:
.\.venv\Scripts\python.exe -m evaluation.runner --dataset synthetic_v1 --live --limit 1 --trace
```

`--trace` without `--live` is rejected. The tracer permits only unchanged, hash-validated repository synthetic fixture PDFs/source records. It does not enable tracing through production API requests.

Files are stored under ignored `evaluation/private_traces/<run-id>/<trace-id>/trace.json`, with owner-only Windows ACLs (or POSIX directory 0700/file 0600). Traces preserve original typed proposals, retained output, rejected-item metadata, monotonic nested spans and provider-reported usage when available. Ordinary JSON/CSV/Markdown reports contain counts, reason-code histograms and private trace references, not the raw proposals. Do not commit private traces; separately curate only synthetic examples if needed.

Raw source strings are available only in the private trace and are redacted for configured credentials/common email/phone/token identifiers. Never point the observer at customer data or treat its redaction patterns as a universal PII detector. Any trace collection error is marked explicitly and returns benchmark exit code 2; it does not alter the underlying analysis acceptance decisions.

The network-blocked regression suite exercises tracing using mocked providers. See [observability implementation](../../docs/AI_OBSERVABILITY_IMPLEMENTATION.md) for schema, diagnostic codes, overlap/usage limits and actual test results.
