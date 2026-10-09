# Render backend + Vercel frontend

For Vercel backend + Neon, follow [the PostgreSQL deployment guide](VERCEL_DEPLOYMENT.md).
The SQLite disk instructions below apply only when `DATABASE_URL` is absent. Render can also use
the new backend-only PostgreSQL setting and then does not require a SQLite disk.

Code and offline tests are prepared for deployment. **Deployment is not verified.** No hosted
embedding call, deployment, or deployed PDF analysis was performed during this change.
Do not announce success until the acceptance workflow below completes against the deployed backend.

## Render settings

Create a Python web service with these exact settings:

| Setting | Value |
| --- | --- |
| Root directory | `backend` |
| Runtime | Python 3 |
| Build command | `python -m pip install -r requirements.txt` |
| Start command | `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Health check path | `/health` |
| Instances | 1, with autoscaling disabled |
| Persistent disk mount | `/var/data` |

`$PORT` is expanded by Render's shell; do not hardcode localhost or port 8000 in production.
Do not use `--reload`. The requirements file already includes google-genai, JWT and Razorpay;
no extra embedding dependency is needed. The older requirements-lock file does not include all
authentication/billing dependencies, so use the build command above.

### Render environment variables

Configure these in Render's environment dashboard. The following values are examples, not credentials:

| Name | Value / instruction |
| --- | --- |
| `PYTHON_VERSION` | `3.14.7` (matches the tested local Python version) |
| `ENVIRONMENT` | `production` |
| `EMBEDDING_PROVIDER` | `gemini` |
| `GEMINI_API_KEY` | Set the existing server-side key privately in Render |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` |
| `GEMINI_EMBEDDING_DIMENSIONS` | `768` |
| `GEMINI_EMBEDDING_TIMEOUT_SECONDS` | `60` |
| `GEMINI_MODEL` | `gemini-3.5-flash` (existing reasoning model; account access must still be verified) |
| `GEMINI_TIMEOUT_SECONDS` | `180` |
| `GEMINI_MAX_ATTEMPTS` | Existing value; default `3`. Set `1` for an explicitly approved single-attempt acceptance test |
| `GEMINI_RETRY_BASE_SECONDS` | `1` (existing reasoning retry policy) |
| `STORAGE_PATH` | `/var/data/veritas.sqlite3` |
| `CORS_ORIGINS` | `["https://YOUR-FRONTEND.vercel.app"]` — replace with the exact frontend origin |
| `JWT_SECRET_KEY` | Privately set a strong random secret; never use the example/default value |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` |
| `AUTH_REQUIRED` | `true` |
| `ALLOW_LEGACY_UNAUTHENTICATED_ACCESS` | `false` |

Optional unchanged upload settings: `MAX_UPLOAD_BYTES=10485760`, `MAX_CONTRACT_PAGES=30`,
`MAX_CONTRACT_CHARS=60000`, `MAX_CONTRACT_CLAUSES=100`. Ollama settings are ignored by the
Gemini embedding provider; Render does not need a local Ollama daemon.

For existing billing checkout functionality, set the backend-only variables
`RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`,
`RAZORPAY_STANDARD_PLAN_ID`, and `RAZORPAY_PRO_PLAN_ID` to the appropriate existing Test Mode
values privately. Configure the existing `/api/webhooks/razorpay` URL in the provider dashboard
if using webhooks. Do not switch payment mode or create real payments as part of deployment verification.
Without these settings registration, trials and analysis can work, but paid checkout cannot.

### SQLite initialization and durability

`STORAGE_PATH` was already supported. On the first storage operation the existing connection
function creates missing parent directories and initializes/migrates tables. A focused test verifies
this using an empty nested temporary directory. No schema or production database changes were needed.
Initialization occurs at runtime, not in the build command, because the mounted disk is a runtime resource.
`/health` reports process health and does not prove database or provider readiness.

Use a persistent disk on a paid service for durable accounts, uploads, analyses and billing state.
Without a disk these files are ephemeral and are lost on restart/redeploy. Pointing `STORAGE_PATH`
at `/var/data` alone does not provision a disk. Use one instance and one worker with this SQLite MVP;
do not attach the same database to horizontally scaled services. Back up the database using a consistent
SQLite backup procedure before changing infrastructure. Local data is not automatically migrated to Render.

## Vercel settings

| Setting | Value |
| --- | --- |
| Root directory | `frontend` |
| Framework preset | Vite |
| Node.js version | `24.x` |
| Install command | `npm ci` |
| Build command | `npm run build` |
| Output directory | `dist` |
| Environment variable | `VITE_API_BASE_URL=https://YOUR-BACKEND.onrender.com` |

Set the API origin without `/api` or a trailing slash. Set it separately for production and any
preview environments that should access this backend. Rebuild after changing it: Vite embeds this
public URL at build time. Keep **all API keys, JWT secrets and payment secrets out of Vercel/VITE variables**.
`BACKEND_URL` only controls the local Vite development proxy and is not used by the static production build.
The browser calls Render directly over HTTPS; no Vercel API proxy or function is required.
Add each authorized custom/preview origin explicitly to Render's JSON `CORS_ORIGINS` list;
do not use a wildcard to bypass authentication. Current navigation uses application state rather than
client-side URL routes, so no SPA rewrite is needed for the existing interface.

## Local behavior and provider identity

No existing `.env` or credentials were changed. Local development defaults to:

```dotenv
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=qwen3-embedding:0.6b
```

The new `app.services.embeddings.embed_text` dispatches to the selected provider. The original
Ollama module, HTTP reuse, timeouts, error types and cosine calculation are unchanged.
Gemini embeddings use `models.embed_content` with `SEMANTIC_SIMILARITY` for both policy and
clause inputs and a configured output dimension. The installed SDK sends a one-item
`batchEmbedContents` request; this is one provider request, not an asynchronous batch job.
The existing cosine implementation normalizes vector norms when comparing them.

Cache identity includes provider, model, endpoint/API version, timeouts, task, dimensions,
retry/transport settings and a credential fingerprint, as relevant to the provider. No plaintext key
is placed in a cache key. Static playbook vectors retain the bounded in-memory policy cache;
exact-text clause deduplication lasts only for one retrieval request. No contract-vector cache is shared
across users, persisted to disk, or stored in SQLite. Configuration changes during retrieval fail
before mixed vector spaces are compared. Restart after changing environment configuration.
PolicyMatch fields, stable top-three sorting and duplicate clause IDs/order remain unchanged.
Hosted and Ollama scores need not match: they use different models. Do not reuse one model's vectors
or infer equivalent retrieval accuracy from the offline interface tests.

Hosted failures return structured `detail` containing `state`, `failed_stage`, `error_category`,
`message`, `embedding_provider`, `embedding_model`, `upstream_http_status`, `analysis_id`,
and `failure_recorded`. Timeout maps to 504, connectivity/transient upstream failures to 503,
rate limits to 429, and upstream credential/model/invalid response failures to 502.
Upstream error messages and request contents are not returned. No fake vector, provider fallback,
or automatic embedding retry is used. Existing reasoning retry behavior is unchanged.
Failed analysis is recorded through the existing failure path and preserves the uploaded document.

No new endpoint was introduced. The existing `/api/embeddings/test` now requires the existing
Bearer authentication when hosted embeddings or a non-development environment is selected,
even if the legacy unauthenticated toggle is enabled. Local development with Ollama remains compatible.
Upload, analysis, retrieval, evidence verification, authentication and billing behavior otherwise remain unchanged.

## Verification and acceptance

Offline commands, from the indicated root directories:

```powershell
# backend/
.\.venv\Scripts\python.exe -m evaluation.run_offline_tests
# frontend/
npm.cmd run lint
npm.cmd run build
```

The offline runner disables live opt-ins and blocks outbound sockets. Hosted tests use mock responses,
including the actual installed SDK's serialization, transport failures, malformed vectors and bounded
429 handling. They do not prove real Gemini access, Linux dependency installation or deployed latency.

Local validation for this change: 173 backend tests ran, 170 passed, 3 live-service tests were skipped,
and there were 0 failures or errors. All 13 focused provider/storage tests passed. Frontend lint and
production build exited successfully. `pip check` found no broken installed requirements.

After an authorized deployment, perform these checks against the deployed services:

1. Check Render `/health` and browser CORS from the actual Vercel origin.
2. Register/log in to a test account and activate its existing trial.
3. With explicit approval for API usage, upload a real PDF through `POST /api/contracts/upload`.
   Confirm pages, clauses and contract ID were returned and the upload is stored on the mounted disk.
4. Submit exactly the approved analysis budget through authenticated `POST /api/analyze`.
   Confirm `embedding_model=gemini-embedding-001`, Gemini structured reasoning, strict evidence
   verification, supported findings/obligations and explicit exclusion of unsupported records.
5. Fetch authenticated `GET /api/analysis/{analysis_id}` and confirm the saved result matches.
   Verify quotations against the original PDF text and check frontend rendering and refresh restoration.
6. Restart the backend, re-login and fetch the same saved result to verify persistent storage.
7. Record IDs, status, verified/rejected counts, processing time and any errors without recording secrets.

Until all of these pass, deployed end-to-end functionality remains **unverified**.

## Remaining risks

- Gemini embedding model access, quota, charges and cloud latency have not been tested with this account.
  The documented model accepts at most 2,048 input tokens; unusual clauses may exceed provider limits.
  Provider failures remain explicit; the app does not silently truncate or substitute vectors locally.
- Reasoning remains synchronous with existing bounded retries; long requests can outlast an infrastructure
  timeout. Browser-to-Render requests avoid a Vercel function timeout but must still be tested on Render.
- SQLite is suitable for this single-instance MVP, not horizontal scaling. A paid persistent disk,
  backup practice and adequate disk capacity are needed for durable uploaded PDFs.
- Linux package installation has not been performed here. Local tests used Python 3.14.7 and Node 24.19.0.
- Frontend build reports an existing JavaScript bundle larger than 500 kB. Lint/build pass; no UI redesign
  or bundle refactoring was performed.
- The installed FastAPI TestClient reports an httpx deprecation warning; tests pass. No dependency migration
  was added to this deployment task.

## Platform and model references

- [Gemini embeddings and model limits](https://ai.google.dev/gemini-api/docs/embeddings)
- [Render FastAPI configuration](https://render.com/docs/deploy-fastapi)
- [Render Python version selection](https://render.com/docs/python-version)
- [Render persistent disk requirements](https://render.com/docs/disks)
- [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [Vercel Node.js versions](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions)
