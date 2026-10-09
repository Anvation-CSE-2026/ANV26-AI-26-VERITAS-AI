# Vercel + Neon deployment preparation

The backend now selects PostgreSQL whenever backend-only `DATABASE_URL` is nonblank. Without it,
the existing local SQLite database and `STORAGE_PATH` behavior remain available. Existing SQLite
files are not changed or copied automatically into Neon. This change migrates the storage implementation;
moving existing local accounts/data is a separate deliberate data import.

## Files and storage behavior

- `backend/app/services/storage.py`: psycopg 3 connection/transaction lifecycle, parameter binding,
  PostgreSQL migrations, PDF `BYTEA`, and insertion-order analysis history.
- `backend/app/config.py`, `backend/requirements.txt`, `backend/.env.example`: private database setting,
  bounded connection/statement timeouts and binary psycopg dependency.
- `backend/app/main.py`, `backend/app/routes/contracts.py`, `backend/app/services/contract_analysis.py`:
  PostgreSQL errors handled without returning database URLs, server details, SQL values or credentials.
- `backend/index.py`, `backend/pyproject.toml`, `backend/vercel.json`, `backend/.vercelignore`:
  FastAPI serverless export, dependency metadata, runtime duration, resource inclusion and secret exclusion.
- `frontend/vercel.json`, `frontend/.vercelignore`, `.gitignore`: Vite build/SPA configuration and exclusions.
- `tests/test_postgres_storage.py` and existing test fixtures/offline runner: PostgreSQL coverage and
  explicit SQLite isolation so a configured Neon URL cannot redirect offline tests to customer data.
- `backend/scripts/verify_postgres.py`: opt-in real database verification using unique synthetic records
  followed by deletion of only those records. It never invokes Gemini, Ollama or Razorpay providers.
- `docs/POSTGRES_VERIFICATION.json`: sanitized verification outcome; no URL, password, token or API key.

All existing storage function names/signatures are preserved. Registration, login, subscriptions,
payment events, usage records, contract bytes, verified analyses, failure records and scoped history
retain their existing JSON/API behavior. The existing legacy `user_id IS NULL` compatibility behavior
is retained; new authenticated uploads/analyses remain assigned to their account.

Database values remain bound separately from SQL. The small adapter translates fixed application qmark
placeholders to psycopg `%s`; no value interpolation occurs. Allowed subscription update fields remain
unchanged. PostgreSQL uses `BYTEA` rather than `BLOB`, `ALTER TABLE ADD COLUMN IF NOT EXISTS` rather
than `PRAGMA`, and a durable identity sequence rather than SQLite `rowid` for history order.

Migrations only create missing tables, columns and indexes. PostgreSQL cold starts serialize migration
transactions using an advisory lock, and cache successful initialization per connection-string identity
inside the process. Failed migrations are not cached. Application operations use separate managed
transactions: commit on success, rollback on failure, close on exit. No connection remains globally shared.
Automatic prepared statements are disabled for Neon pooled URL compatibility. Statement timeout is
transaction-local, preventing settings from leaking between pooled clients. A configured PostgreSQL
failure never silently switches the application to SQLite.

## Two Vercel projects

### Backend project

| Setting | Value |
| --- | --- |
| Root directory | `backend` |
| Framework preset | FastAPI |
| Python | 3.14, selected by `pyproject.toml` |
| Entrypoint | `index:app` (`backend/index.py`) |
| Install/build command overrides | Leave unset; the Python framework builder installs dependencies |
| Output directory override | Leave unset |
| Function duration | 300 seconds, configured for `index.py`; enable Fluid compute |

The root `pyproject.toml` exports the entrypoint and obtains its dependencies from `requirements.txt`
through setuptools dynamic metadata, keeping one dependency source. Local installation remains
`python -m pip install -r requirements.txt`. Do not use the older requirements-lock file: it lacks some
existing authentication/billing dependencies. Do not run Uvicorn or set a listening port on Vercel;
the platform invokes the existing ASGI app. Render/Uvicorn local startup still works.

Set these variables privately in the backend Vercel project for each authorized environment:

```dotenv
ENVIRONMENT=production
EMBEDDING_PROVIDER=gemini
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_EMBEDDING_DIMENSIONS=768
GEMINI_EMBEDDING_TIMEOUT_SECONDS=60
GEMINI_MODEL=gemini-3.5-flash
GEMINI_TIMEOUT_SECONDS=180
GEMINI_MAX_ATTEMPTS=1
DATABASE_CONNECT_TIMEOUT=10
DATABASE_STATEMENT_TIMEOUT_MS=15000
AUTH_REQUIRED=true
ALLOW_LEGACY_UNAUTHENTICATED_ACCESS=false
MAX_UPLOAD_BYTES=4000000
CORS_ORIGINS=["https://YOUR-FRONTEND.vercel.app"]
```

Also set **`DATABASE_URL`**, **`GEMINI_API_KEY`**, and **`JWT_SECRET_KEY`** using your private dashboard
values. `DATABASE_URL` must be the exact bare Neon connection URL, including its TLS settings, not a
`psql` command or a malformed query string. Prefer Neon's pooled connection URL for serverless traffic
and keep database/function regions near one another. No TLS verification setting is weakened by the code.
Use a strong JWT secret and maintain the same value across instances/redeploys to preserve issued tokens.
`STORAGE_PATH` is ignored while PostgreSQL is configured. The Vercel entrypoint refuses startup without
`DATABASE_URL`; ephemeral SQLite is unsuitable for accounts, payments and saved uploads.

For existing billing features set private backend `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`,
`RAZORPAY_WEBHOOK_SECRET`, `RAZORPAY_STANDARD_PLAN_ID` and `RAZORPAY_PRO_PLAN_ID` to the existing
appropriate Test Mode configuration. Point webhooks at `/api/webhooks/razorpay` on the backend origin.
No billing mode, provider behavior or authentication requirement was changed.

The single-attempt setting above is a deployment recommendation within the existing configurable retry
policy. Local defaults were not changed. Obtain separate approval before any live Gemini acceptance call.

### Frontend project

| Setting | Value |
| --- | --- |
| Root directory | `frontend` |
| Framework | Vite |
| Node.js | 24.x |
| Install | `npm ci` |
| Build | `npm run build` |
| Output | `dist` |
| Public environment variable | `VITE_API_BASE_URL=https://YOUR-BACKEND.vercel.app` |

Set only the backend origin, without `/api` or a trailing slash. Existing client code already supports
this setting and sends Bearer tokens. Rebuild when changing it. `BACKEND_URL` is for the local Vite proxy;
it does not route production traffic. Add exact custom/preview frontend origins to backend `CORS_ORIGINS`.
No wildcard or authentication bypass is necessary. The frontend SPA rewrite preserves refresh navigation.
Never set `DATABASE_URL`, `GEMINI_API_KEY`, JWT secrets or payment secrets in frontend/VITE variables.

## Serverless limits and checks

1. **Uploads:** Vercel Functions limit request/response bodies to 4.5 MB, including multipart overhead.
   Production `MAX_UPLOAD_BYTES=4000000` leaves room for that overhead. Local default remains 10 MiB.
   Larger PDFs require the existing Render deployment or a separately designed direct-upload workflow;
   configuration cannot lift this platform limit.
2. **Duration:** the function is configured for 300 seconds. Sequential embeddings plus reasoning can
   exceed this, especially with large contracts, cold starts or provider failures. The unchanged local
   default permits three reasoning attempts of up to 180 seconds each. Use the production single-attempt
   setting above; it still does not guarantee that all contracts finish within 300 seconds.
3. **Size:** a local Windows measurement found installed dependencies at 133.59 MiB and backend app/resources
   at 0.34 MiB. This is not a Linux Vercel bundle measurement. Native PyMuPDF, psycopg-binary and transitive
   dependencies must be validated by the real Vercel build. Python's standard bundle limit is 500 MB.
4. **PDF handling:** extraction uses PyMuPDF's in-memory stream API. Multipart uploads may spool to the
   runtime's writable temporary directory; Vercel ephemeral temp storage is adequate for processing, not
   persistence. PDFs are stored in PostgreSQL `BYTEA`, not the deployed application directory.
5. **Resources:** the company playbook and clearly labeled demo JSON under `app/resources` are explicitly
   bundled. Evaluation fixtures/private traces, local virtual environments, local database files and
   `.env` files are excluded. No eval code is required by the production application.
6. **Connections/concurrency:** each operation closes its database connection. Use a pooled Neon URL for
   autoscaling. Existing quota checks/webhook side effects are not redesigned into distributed atomic
   workflows in this task; high concurrency still warrants separate review.
7. **Cold starts:** database/provider readiness is not established by `/health`. Migrations happen on
   database access, not via a new public endpoint, and no startup calls spend Gemini credits.

## Verification commands

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m evaluation.run_offline_tests
.\.venv\Scripts\python.exe scripts/verify_postgres.py
```

The first test runner blocks external services and forces SQLite. The last command is an explicit real
database test: it runs additive migrations, creates uniquely named synthetic records, validates all
storage functions and removes only its own records. It tests registration/login and evidence-verified
synthetic persistence, **not live AI generation**. Inspect the sanitized JSON outcome rather than logging
the connection string or complete documents. No customer data is printed.

From `frontend/`: `npm.cmd run lint` and `npm.cmd run build`.

## Deployed acceptance still required

Local results: **182 backend tests passed, 3 live-service tests skipped, 0 failures/errors**
(185 total). All 12 focused PostgreSQL/serverless tests passed. Frontend lint/build and `pip check`
passed. Backend package metadata built successfully with a dry-run installation, including every
runtime requirement from `requirements.txt`.

Real Neon verification passed after the malformed connection URL was corrected locally by the user.
All seven tables were confirmed, migrations ran repeatedly, PDF `BYTEA` and user/contract/analysis/
failure/subscription/event/usage records round-tripped, account scoping and history order were checked,
registration/login worked, and rollback and synthetic-record cleanup succeeded. The initial connection
format failure and a missing field in the diagnostic's synthetic analysis fixture were corrected before
this successful verification. No live model or payment-provider call was made.

No deployment was performed. After approval and deployment, verify actual Linux dependency installation,
function size, CORS/authentication, synthetic PDF upload, one separately approved live Gemini analysis,
strict quote verification, persistence across independent function instances, and saved-result rendering.
Confirm the production upload and execution limits using the actual plan. A local Neon check alone
does not establish that deployed AI analysis works.

References: [Vercel FastAPI](https://vercel.com/docs/frameworks/backend/fastapi),
[Python runtime/dependency handling](https://vercel.com/docs/functions/runtimes/python),
[Function payload, size and duration limits](https://vercel.com/docs/functions/limitations),
[psycopg transaction/connection usage](https://www.psycopg.org/psycopg3/docs/basic/usage.html).
