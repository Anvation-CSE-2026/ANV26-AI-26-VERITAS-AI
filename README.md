# VERITAS AI

 Businesses, startups, and individuals frequently enter into legally binding contracts without fully understanding their risks, obligations, and potentially unfavorable clauses.

Traditional contract review is time-consuming, expensive, and often requires specialized legal expertise. Manual reviews can overlook critical issues such as unfair liability provisions, ambiguous terms, unfavorable termination conditions, intellectual property risks, and data privacy obligations.

The challenge is to develop an AI-powered contract intelligence platform that automatically analyzes uploaded legal agreements, identifies potentially risky clauses, extracts contractual obligations, and provides clear, actionable recommendations supported by evidence from the original document.

Evidence-grounded contract analysis MVP: PDF extraction, local Ollama policy retrieval, structured Gemini findings, and deterministic evidence checks. The existing React landing page and health endpoint are preserved. Decision support, not legal advice.

## Cloud deployment

See [Render + Vercel deployment instructions](docs/CLOUD_DEPLOYMENT.md) for exact build/start commands,
environment variables, persistent SQLite storage and the deployed PDF acceptance workflow.
`EMBEDDING_PROVIDER=ollama` remains the local default; `EMBEDDING_PROVIDER=gemini` enables
server-side `gemini-embedding-001` embeddings using the existing `GEMINI_API_KEY`.
The hosted embedding path has offline coverage; deployment and real hosted PDF analysis remain unverified.

## Requirements

Verified with Python 3.14.7, Node.js 24.19.0, npm 11.17.0 on Windows. Use Node 24 LTS and Python 3.14 to reproduce this environment. Health and the landing page require no AI service. Embedding requests require Ollama with qwen3-embedding:0.6b installed.

## First-time installation (PowerShell, workspace root)

```powershell
python -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements-lock.txt
npm.cmd --prefix frontend ci
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

Copy environment files only when they do not already exist, to preserve your settings. `requirements.txt` lists direct dependencies; `requirements-lock.txt` records the full verified Python environment. `package-lock.json` locks frontend dependencies. `npm.cmd` avoids PowerShell script execution policy errors; no activation or execution-policy change is needed.

## Start (two terminals, both initially at workspace root)

Terminal 1:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
cd frontend
npm.cmd run dev
```

Open http://127.0.0.1:5173. API documentation: http://127.0.0.1:8000/docs. Health: http://127.0.0.1:8000/health. Stop servers with Ctrl+C. Port 5173 is strict so mismatched origins do not silently occur.

## Configuration and communication

The frontend requests `/health` and `/api/*`. Vite proxies these paths unchanged to `BACKEND_URL` (default http://127.0.0.1:8000). This is a development proxy, not a production deployment configuration. For a separately hosted frontend, set `VITE_API_BASE_URL` to the backend origin and configure its allowed origins. Vite environment changes require a server restart or production rebuild.

Backend `CORS_ORIGINS` is a JSON array allowing only localhost and 127.0.0.1 on port 5173 by default. Browser credentials are disabled. Backend settings load `backend/.env` regardless of working directory. Keep `GEMINI_API_KEY` exclusively in backend configuration; never put secrets in `VITE_*` variables.

`GEMINI_MODEL=gemini-3.5-flash` powers contract analysis through the official google-genai SDK. Local embeddings use `OLLAMA_BASE_URL=http://localhost:11434` and `OLLAMA_EMBED_MODEL=qwen3-embedding:0.6b`. The legacy `OLLAMA_EMBEDDING_MODEL` setting is also accepted; the new name takes precedence. Health describes the backend process, not AI-service readiness. The UI offers an offline message and retry if the API cannot be reached within five seconds.

## Checks

```powershell
.\backend\.venv\Scripts\python.exe -m pip check
.\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
npm.cmd --prefix frontend run lint
npm.cmd --prefix frontend run build
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:5173/api/health
```

Expected health JSON: `{"status":"ok","service":"VERITAS AI","version":"0.1.0","environment":"development"}`. Tests assume the default development configuration.

## Structure

- `frontend/`: branded responsive landing screen and live health indicator.
- `backend/app/main.py`: FastAPI application and typed health response.
- `backend/app/config.py`: server-only environment settings.
- `backend/app/services/ollama_embeddings.py`: embedding service and cosine similarity.
- `backend/app/routes/embeddings.py`: metadata-only embedding test endpoint.
- `data/contracts/`: local SQLite storage of original PDFs, extracted text, and verified analyses; ignored by Git.
- `backend/app/resources/sample_playbook.json`: synthetic policy rules across seven contract categories.
- `tests/fixtures/`: synthetic contract source and reproducible PDF fixture.
- `tests/`: extraction, evidence, retrieval, Gemini, API, health/CORS, and opt-in live integration verification.
- `docs/`: reserved documentation directory.

PDF uploads, evidence-verified contract analysis, and obligation extraction are implemented. Chat, dashboards, and agent workflows are not implemented. Existing pinned PyMuPDF, google-genai, HTTPX, and multipart dependencies cover this MVP; requirements files need no changes.

## Troubleshooting

If the UI says backend unavailable, start FastAPI, verify its port and `BACKEND_URL`, then retry. If a port is already occupied, stop the previous server or deliberately update the ports, proxy, and CORS settings together. Installation requires access to npm and PyPI. The initial restricted npm download failed with EACCES; installation succeeded with authorized network access. An initial non-UTF-8 source error was fixed; source files use UTF-8.

Setup references: [Vite](https://vite.dev/guide/), [Tailwind Vite plugin](https://tailwindcss.com/docs/installation/using-vite), [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/).

## Local embeddings

Install the model with `ollama pull qwen3-embedding:0.6b` and ensure Ollama is running. The service uses only [Ollama POST /api/embed](https://docs.ollama.com/api/embed); it makes no chat calls. `embed_text(text)` returns a validated vector for retrieval, evidence discovery, and clause/policy matching. `cosine_similarity(left, right)` compares equal-length vectors from the same model; similarity alone does not establish policy compliance.

Call the backend directly (the existing Vite proxy removes `/api`):

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/embeddings/test -ContentType application/json -Body '{"text":"The supplier must notify the company within 48 hours."}'
```

Success returns only `success`, `model`, and the actual `dimensions`, never the embedding vector. Blank/invalid text returns 422. Connection failures return 503, timeouts 504, and upstream HTTP errors or malformed embeddings 502. `OLLAMA_CONNECT_TIMEOUT=5` and `OLLAMA_READ_TIMEOUT=120` configure seconds. Inputs exceeding model context are rejected rather than silently truncated. HTTPX is already a pinned dependency; no requirements changes are needed.

Unit tests use mocked responses. To also run the real model comparison and endpoint tests (failures are not skipped):

```powershell
$env:RUN_OLLAMA_INTEGRATION="1"
.\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
Remove-Item Env:RUN_OLLAMA_INTEGRATION
```

The real comparison prints measured scores and checks that a breach notification paraphrase is closer to the contract clause than an unrelated invoice rule.

## Contract analysis MVP

Backend-only implementation. Use the backend directly at `http://127.0.0.1:8000` or Swagger `/docs`; the unchanged Vite development proxy removes `/api` and is not wired to these new endpoints.

| Endpoint | Input | Result |
| --- | --- | --- |
| `POST /api/contracts/upload` | Multipart field `file`, PDF | HTTP 201 with `contract_id`, original extracted page text, stable clause IDs, original page offsets, and extraction warnings |
| `POST /api/analyze` | JSON `{"contract_id":"<uploaded-id>"}` | Synchronous analysis with `analysis_id`, verified findings/obligations, measured semantic matches, coverage gaps, and verification rejections |
| `GET /api/analysis/{analysis_id}` | Saved analysis ID | Stored analysis; unknown IDs return 404 |

Set `GEMINI_API_KEY` only in `backend/.env`. Configuration is loaded relative to the backend, independent of working directory. The key is excluded from settings representations and never returned in API responses or SDK error messages. `GEMINI_TIMEOUT_SECONDS=90` sets the SDK timeout. Gemini retries HTTP 429/500/502/503/504 and transport failures with bounded exponential backoff: `GEMINI_MAX_ATTEMPTS=3` and `GEMINI_RETRY_BASE_SECONDS=1` give at most three calls and delays of one and two seconds. SDK internal retries are disabled. Exhausted rate limits or quota return HTTP 429 with `Retry-After: 60`; no synthetic output is substituted. Authentication/request failures return sanitized 502 errors, service/connection failures 503, and timeouts 504. Ollama errors use 502/503/504 as appropriate. Failures return no fallback AI findings and create no successful analysis record.

The sample playbook covers liability, indemnification, termination, confidentiality, payment, data protection, and intellectual property. These rules are synthetic demonstration policies, not actual company requirements. Edit `backend/app/resources/sample_playbook.json` and change its version to adapt it. Rule IDs must be unique. Ollama embeds each clause and rule; the three highest measured cosine similarities are retained per clause. All rules are also provided to Gemini so retrieval does not exclude a relevant policy. Scores are retrieval signals, not risk or compliance scores.

Each risk finding includes risk level, clause category, explanation, exact quote, page number, clause ID, policy ID, the resolved policy rule, and recommended action. The backend requires the quote to be an exact substring of both the cited clause and the original extracted page text, with verified original offsets. It checks policy IDs and category correspondence. It never repairs quotes with fuzzy matching or substitutes invented evidence. Invalid records are excluded and listed by reason; mixed output has `status=partial`. If every proposed record is rejected, analysis fails with 502. An empty valid model response stays empty and does not imply a safe contract. Detected document instructions always make the analysis partial and require human review.

Obligations include a quote, page, clause ID, description, and optional responsible party/deadline. Party and deadline must be exact substrings of the evidence quote or null; relative deadlines are preserved without calculating dates. Potential omissions use `finding_status=missing`, valid policy references, null contract quote/page/clause ID, `evidence_status=needs_review`, and an explicit full-document review requirement. Absence is never confirmed automatically. `unassessed_policy_ids` means no verified risk finding addressed those policies; it is not a claim of absence or compliance. Verification proves provenance, not legal reasoning or analysis completeness.

Storage is a local SQLite database at `data/contracts/veritas.sqlite3`, configurable with an absolute `STORAGE_PATH`. Original PDF bytes, extracted pages/clauses, and verified results persist across server restarts. The MVP supports one fixed playbook and synchronous analysis; it has no authentication, user isolation, background job system, or deletion/retention API. It is intended for local hackathon use. Only extracted text and policy rules are sent to Gemini; embeddings remain local.

Default input limits: 10 MiB PDF, 30 pages, 60,000 extracted characters, 100 clauses. `MAX_UPLOAD_BYTES`, `MAX_CONTRACT_PAGES`, `MAX_CONTRACT_CHARS`, and `MAX_CONTRACT_CLAUSES` configure these. Inputs over limits return 413. Invalid PDFs, encrypted PDFs, and textless scans return 422; OCR is not implemented. Mixed documents with blank/image-only pages produce warnings and partial analysis. Clause segmentation uses numbered headings, blank paragraphs, and 2,000-character chunks; it is not a legal clause parser. Extraction order and accuracy depend on PDF layout.

### Try the synthetic fixture

Ensure Ollama is running with `qwen3-embedding:0.6b`, configure Gemini, and start FastAPI. From the workspace root:

```powershell
.\backend\.venv\Scripts\python.exe tests/sample_pdf.py
$upload = curl.exe -s -F "file=@tests/fixtures/synthetic_supplier_contract.pdf" http://127.0.0.1:8000/api/contracts/upload | ConvertFrom-Json
$body = @{ contract_id = $upload.contract_id } | ConvertTo-Json
$analysis = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/analyze -ContentType application/json -Body $body
Invoke-RestMethod "http://127.0.0.1:8000/api/analysis/$($analysis.analysis_id)"
```

### Tests

Offline automated checks (no Gemini requests; live tests explicitly skipped):

```powershell
.\backend\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\backend\.venv\Scripts\python.exe -m pip check
```

Real service checks (sends the synthetic contract text to Gemini and can consume quota):

```powershell
.\backend\.venv\Scripts\python.exe tests/diagnose_gemini.py
.\backend\.venv\Scripts\python.exe tests/run_live_tests.py
```

The live runner enables both `RUN_AI_INTEGRATION=1` and `RUN_OLLAMA_INTEGRATION=1`. Unavailable services, provider errors, or failed evidence checks fail the tests rather than claiming success. The real HTTP E2E launches an isolated Uvicorn server with temporary SQLite storage, uploads the synthetic PDF, calls real Ollama and Gemini, independently verifies all returned evidence, fetches the saved result, and stops the server. Run `tests/verify_ai_http.py` directly for only that flow. Network access to Google is required. The safe diagnostic prints key presence and connection/status information only.

Optional: set `AI_E2E_REPORT_PATH` to an output JSON path to retain the actual synthetic contract and verified analysis from a successful E2E run. No report is written on failure.

Gemini structured output uses a compact JSON schema through the [official SDK](https://googleapis.github.io/python-genai/) and [structured-output API](https://ai.google.dev/gemini-api/docs/structured-output). The provider schema retains field types, required fields, and enums; Pydantic applies all size limits and rejects extra fields locally. The previous `gemini-2.5-flash` configuration was rejected for generation by this account; the model setting and defaults were updated to `gemini-3.8-flash` at the user’s request. Provider high-demand responses are propagated as sanitized 503 failures, without fake findings or successful storage writes.

## Strict reasoning boundaries

Gemini is a bounded reasoning engine, not a source of contractual facts. The system instruction is sent through `GenerateContentConfig.system_instruction` on every generation attempt. It restricts factual conclusions to supplied contract/playbook material, forbids autonomous approvals, legal guarantees, document modification, external instructions, secret disclosure, and invented evidence, and requires explicit uncertainty. Contract and playbook text remain JSON data in user contents; embedded role/schema/secret/verdict instructions are not promoted into the system instruction. No tool calls are enabled.

Finding statuses: `compliant`, `risky`, `ambiguous`, `conflicting`, `missing`. Evidence statuses are assigned by Python, never Gemini: `verified` confirms quotation provenance; `unsupported` identifies excluded records; `needs_review` covers ambiguity, unreliable matching, assumptions, potential omissions, and ambiguous obligation deadlines. A source-supported ambiguous finding can have a verified quote while still needing interpretation review. `requires_human_review=true` is present on every analysis, and no approval decision is generated.

New findings separate `source_facts`, `model_interpretation`, and the stored `applicable_policy_rule`. Any model-supplied policy requirement must equal the stored rule exactly. Referenced party/date fields must occur verbatim in quoted evidence. Strict model-output validation rejects extra fields, numeric string page coercion, model-supplied evidence statuses/confidence, and graph output. This MVP has no graph layer; graph edges are not accepted rather than permitting unverified entities. Existing persisted result fields remain readable for compatibility.

Deadline types are backend-classified as `fixed_date`, `relative`, `ambiguous`, or `unspecified`. Exact strings are preserved; dates are never calculated. Ambiguous date formats and unsupported calendar values need review. Detection of recognizable document-instruction patterns is conservative and can have false positives/negatives. It cannot guarantee resistance to every prompt injection. Verbatim evidence checks cannot independently establish all factual implications inside free-form explanations, party-role interpretation, legal correctness, or completeness.

Explicit offline demonstration when live services are unavailable:

```powershell
.\backend\.venv\Scripts\python.exe tests/show_synthetic_demo.py
```

This command uses the synthetic PDF and a hand-authored finding, labels `output_origin=synthetic_demo` and `live_ai_used=false`, and never runs automatically after a live failure.

Model verification: `tests/verify_gemini_model.py` lists the actual API model inventory and generateContent capability, tests real structured JSON with exact evidence/deadline checks, and only updates `.env`/`.env.example` when invoked with `--apply` after a successful test. The latest check selected `gemini-3.5-flash`; the preferred `gemini-3.8-flash` was listed but returned 503. Full catalog, capability flags, and actual response are in `docs/gemini-model-verification.json`. Listed capability alone does not guarantee account-level generation availability.

## Hackathon demonstration readiness

The full live pipeline was verified with `gemini-3.5-flash`: PDF upload/extraction, ten source clauses, thirty measured Ollama policy matches, seven accepted and verified findings, zero unsupported findings, five obligations, SQLite retrieval, and backend restart persistence. Gemini succeeded on the first attempt. See `docs/live-e2e-result.json` for actual IDs, counts, timing, and provider model version. Model environment settings were written only after this complete verification succeeded.

Frontend integration contract: [docs/frontend-api-contract.md](docs/frontend-api-contract.md). Exact OpenAPI schemas: [docs/frontend-openapi.json](docs/frontend-openapi.json). Five-minute presentation workflow: [docs/demo-workflow.md](docs/demo-workflow.md).

Offline demo is explicitly separate: `GET /api/demo/analysis` returns the precomputed synthetic snapshot labeled **SAMPLE ANALYSIS — DEMO DATA**. It has seven hand-authored/evidence-verified findings and three obligations, never claims live Gemini output, and calls no AI service. `tests/show_synthetic_demo.py` displays only its summary by default; `--full` deliberately shows evidence. `tests/build_demo.py` rebuilds the precomputed artifact only when explicitly run.

Failed analysis attempts are now stored separately from successful results, with sanitized failure stage/category, provider HTTP code when available, actual Gemini attempts, and timing. When an analyze error reports `failure_recorded=true`, retrieve its ID using GET `/api/analysis/{analysis_id}`; branch on `status=failed` and do not assume findings exist. Successful results retain completed/partial statuses. Retries remain bounded and authentication errors are not retried.

Repeat the same live verification (sends synthetic inputs to providers and uses default persistent storage):

```powershell
.\backend\.venv\Scripts\python.exe tests/verify_ai_http.py --model gemini-3.5-flash --keep-storage --report docs/live-e2e-result.json --apply-model-on-success
```

The runner defaults to temporary storage without `--keep-storage`, suppresses full source logging, writes sanitized summaries on success/failure, and never applies model configuration after a failed full request.
