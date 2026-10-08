# VERITAS AI hackathon demonstration runbook

Validated 2026-10-09 on feature/ai-reliability. Local demonstration at http://127.0.0.1:5173. Backend at http://127.0.0.1:8000. Do not reset storage, delete accounts, replace secrets or rerun benchmarks.

## Startup

Open three PowerShell terminals. From the repository root:

~~~powershell
# Terminal 1 — only if Ollama is not already listening on 11434
ollama serve
~~~

~~~powershell
# Terminal 2
cd backend
$env:GEMINI_TIMEOUT_SECONDS='180'
$env:GEMINI_MAX_ATTEMPTS='1'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

~~~powershell
# Terminal 3
cd frontend
npm.cmd run dev
~~~

Use npm.cmd to avoid PowerShell's npm.ps1 execution-policy block. Dependencies are already installed. Do not launch a second process on an occupied port. The Vite server has strictPort=true. Backend health: http://127.0.0.1:8000/health; same-origin proxy health: http://127.0.0.1:5173/health. Health is process health, not provider readiness.

Required for live analysis: local Ollama with qwen3-embedding:0.6b, the existing backend/.env Gemini key/model settings, writable existing SQLite storage and an authenticated account with an active trial or plan. Never print .env. Gemini is configured as gemini-3.5-flash. Blank VITE_API_BASE_URL uses the Vite /api and /health proxies; BACKEND_URL defaults to http://127.0.0.1:8000. Set an explicit frontend API origin only for a separately hosted backend, with matching CORS. The proxy is a development-server configuration; a standalone production deployment needs equivalent routing or a build-time API origin. Use the development server for this local hackathon demo, not npm preview as a substitute API proxy.

## Five-minute demonstration

1. **0:00–0:45 — open and authenticate.** Open the local URL. Register a demonstration account with your own chosen password, or log into an existing account. Activate the offered Pro trial once. Do not use hardcoded credentials. The automated smoke accounts were synthetic and their randomly generated passwords were not retained; they are not shared demo logins. Login or successful trial activation should lead to the workspace.
2. **0:45–1:15 — upload.** Open Contract and upload backend/evaluation/fixtures/contracts/supplier_red.pdf. This three-page equipment contract has explicit fraud/data liability-cap and indemnification issues. Explain that inputs and playbook are synthetic.
3. **1:15–2:15 — analyze once.** Click Analyze once. Loading shows elapsed time and informational steps, without claiming server stage completion. Analysis duration varies; the approved smoke took 22.181 seconds. Do not repeatedly click or refresh during processing. A live run uses Gemini credits; this task authorized one run, which is already complete. Obtain approval before any further agent-run Gemini calls.
4. **2:15–3:30 — inspect evidence.** Overview shows response-derived severity counts, categories, actions and provenance. Open Risks, then Evidence. Distinguish exact quotations/page/clauses from potential omissions with needs-review status. Partial means some items need review, not necessarily a provider failure. Open Action Plan for explicit obligations/deadlines and Policy Comparison/Knowledge Graph for existing views.
5. **3:30–4:15 — persistence.** After a successful UI analysis, refresh the same tab while logged in: the last analysis ID is retained in sessionStorage and reauthorized through GET /api/analysis/{id}. Only the reference/user ID is stored, not contract text. Results restore; the uploaded PDF/extracted clause view is not restored because no contract-fetch endpoint exists. Upload a new PDF if needed. Switching to demo clears the last-live reference. The app does not yet expose a saved-history picker.
6. **4:15–5:00 — backup / honest limits.** Load Demo Data if providers are slow/unavailable. State explicitly: SAMPLE ANALYSIS — DEMO DATA; hand-authored, precomputed synthetic findings, not live Gemini. Show backend-verified citations, actions and obligations. Keep payment out of the core demo unless manual Test Mode checkout has been rehearsed.

## Contracts and backups

- Clear-risk live input: backend/evaluation/fixtures/contracts/supplier_red.pdf.
- Compliant-clause input: backend/evaluation/fixtures/contracts/saas_green.pdf. Existing source clauses have compliant reference labels; this is not a claim of independently reviewed whole-contract legal compliance. No extra live run was performed on it.
- Existing precomputed UI backup: backend/app/resources/demo_analysis.json, supplied through GET /api/demo/analysis and verified before serving. If the backend is unavailable, frontend/src/api/demoData.json is the existing offline fallback. Its provenance explicitly says synthetic_demo and live_ai_used=false. Selecting it is an explicit demo action, never a silent replacement for failed live analysis.
- Genuine approved live snapshot: [hackathon-live-synthetic-analysis.json](hackathon-live-synthetic-analysis.json). This is the exact saved response from the approved synthetic Gemini smoke, not a manufactured result. Contract ID 9bb56ae0-13b9-4f30-8c98-a5d3838bc8e1; analysis ID 314aabeb-168d-43f3-9c2c-91cc4ecc0dc3. It remains in SQLite scoped to the synthetic smoke account. Account passwords/tokens are not included in the snapshot. This snapshot is an offline JSON inspection backup; there is no new UI import mechanism.

## Executed validation

| Check | Result | Evidence / scope |
|---|---|---|
| Backend startup / health | PASS | Uvicorn started on 8000; direct and proxy health HTTP 200 |
| Frontend serving / API proxy | PASS | Existing Vite listener on 5173; frontend HTTP 200 and auth/upload/analysis via proxy |
| Direct backend CORS | PASS | Origin 127.0.0.1:5173 preflight HTTP 200 with matching allow-origin; same-origin Vite OPTIONS 204 is normal |
| Registration / login / JWT | PASS | HTTP 201 / 200 / authenticated profile 200 with synthetic accounts |
| Trial / subscription / quota | PASS | Pro trial activated; usage 0/30 → 1/30 after successful analysis |
| PDF extraction / upload | PASS | Three-page synthetic PDF uploaded via authenticated endpoint HTTP 201 |
| Ollama | PASS | Model installed; real /api/embed produced 1024 dimensions |
| Live Gemini + retrieval + evidence + persistence | PASS, partial result | One approved analysis invocation, HTTP 200; 7 findings, 3 verified, 4 potential omissions, 2 obligations; saved retrieval exactly matched |
| Synthetic demo API | PASS | HTTP 200, SAMPLE ANALYSIS — DEMO DATA |
| Frontend component rendering | PASS | Seven result views rendered against live and demo responses (14 checks); server-render only |
| Frontend build / lint | PASS | npm.cmd run build and npm.cmd run lint; bundle-size warning remains |
| Backend regression suite | PASS | 144 passed, 3 live-service tests skipped, 0 failures/errors; network-blocked runner, 9.413 seconds |
| Razorpay Test Mode checkout | PASS | Actual test subscription initialized HTTP 200; no payment made |
| Actual Test Mode payment / activation | NOT TESTED | Provider checkout interaction not performed; HMAC verification, activation and quota paths covered by mocked regression tests |
| Browser clicks, refresh, console and visual responsiveness | NOT TESTED | No connected browser surface available; manual rehearsal required |
| Contract narrative summary / downloadable report | NOT AVAILABLE | Backend Analysis schema has no narrative summary/report export; overview is response-derived, not an invented summary |

## Focused fixes

The immediate login failure was caused by no backend listener on port 8000. Backend was started without authentication rewrite. Frontend requests now use the already-configured same-origin proxy by default, with a health proxy added; network failures explain how to start/reach FastAPI. Authentication completion navigates to workspace. A request-local UI guard prevents simultaneous upload/analysis submissions. Gemini provider 429 responses no longer incorrectly trigger a quota-upgrade modal, and repeated quota-modal state updates are guarded. Missing evidence no longer defaults to verified provenance; compliant and omission cards are labeled explicitly. Last successful analysis reference is restored on refresh for the same authenticated user. Loading no longer marks stages completed based on timers.

No production backend, authentication, billing implementation, Gemini prompt/model, gold label or scorer was changed. Environment secrets were untouched. Smoke tests appended two synthetic accounts, one trial, one contract, one analysis/quota event and one pending Test Mode checkout record through existing APIs; no database reset or user deletion occurred. No real payment or Git push occurred.

## Recovery and limitations

- **Failed to fetch / offline:** verify health at 8000, restart the backend terminal if needed, verify frontend proxy target, then refresh the frontend. Do not disable authentication or broadly open CORS. For other origins, configure the exact origin. API failures show a user-facing message.
- **Ollama unavailable:** start Ollama and confirm ollama list contains the configured model. No model downloads or switches are needed on this machine. Use explicit Demo Data if embeddings fail.
- **Gemini rate limit/unavailable:** stop clicking Analyze; read the error and use the separately labeled demo. Do not invent success or automatically rerun agent calls. Existing retries/timeouts are bounded. The backend receives no frontend stage-streaming channel.
- **Quota/subscription:** use the existing trial for the core demo; do not fake payment success. A pending checkout is not active entitlement. Rehearse paid checkout on a separate synthetic account so a pending payment does not disrupt the core trial workflow.
- **Refresh while running:** UI duplicate suppression is in-memory, not server-wide idempotency. Refreshing or opening another tab can submit another analysis and consume credits; wait for completion. Last-result restoration is tab/session scoped, not a full history browser.
- **Visual readiness:** manually check desktop and mobile widths, login/trial, upload, evidence expansion, refresh and browser console before presenting. No visual or click-pass is claimed here. Bundle is large but builds; code splitting was deferred as nonessential.
- **Unavailable features:** no PDF analysis report download, dedicated narrative contract summary, full saved-history picker, contract extraction rehydration or genuine-snapshot UI importer was added.

## Final rehearsal checklist

Confirm local servers stay running. Use your own demo login, activate trial, upload the synthetic PDF and authorize any further live call budget. Prefer the existing labeled demo if preserving credits. Manually check risk/evidence/action/graph screens, logout isolation and refresh. If showing billing, use only rzp_test_ credentials and manually complete a Test Mode payment; never use real charges. Keep the JSON snapshot and this runbook open as backup. Stop polishing once this flow is rehearsed.
