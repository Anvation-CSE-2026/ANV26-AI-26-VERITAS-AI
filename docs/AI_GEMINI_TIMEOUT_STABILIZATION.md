# Gemini timeout stabilization

2026-10-09; feature/ai-reliability. No Gemini/Ollama request made by this investigation. Provider behavior has not been revalidated live.

## Confirmed observations and remaining uncertainty

The approved run of 01_High_Risk_Software_Development.pdf took 95.416 seconds and returned HTTP 504 at gemini_reasoning with upstream_http_status=504 and one provider attempt. Failure was saved/retrieved; extraction succeeded; evidence verification was not reached. Upstream status indicates the SDK API-error branch, rather than the separate local httpx timeout branch. It does not prove whether Google's gateway, model processing or the propagated deadline caused the timeout.

The application supplied 90000 milliseconds (90 seconds), which the installed google-genai _api_client.py converts correctly to 90 seconds and propagates as X-Server-Timeout: 90. No milliseconds/seconds bug was found. This local configured deadline is a plausible avoidable restriction; the total runtime includes other stages, so the exact time spent inside generation cannot be inferred by subtracting 90 seconds. No individual stage trace or token metadata is available for this failed response.

## Payload and token review

Read-only local source inspection: one page, twelve clauses, 2191 extracted clause characters. Serializing the exact clauses and synthetic policy playbook with an empty retrieval list yields 6262 UTF-8 bytes. The real prompt also includes up to 36 clause-policy-score entries, whose original scores were not retained; 6262 is explicitly a base-size measurement, not the exact transmitted payload size. System instruction: 3784 characters; compact response schema: 1902 serialized characters. No clause truncation or duplication of full policy text inside retrieval entries was found. Policy entries contain IDs/similarity only. These sizes do not establish an oversized-input cause.

Actual input/output/thinking token usage is **unavailable**, because generation timed out before a response. No countTokens call was made and no character-to-token estimate is presented as measured usage. max_output_tokens=12000 is an output ceiling, not actual consumed tokens or proof of the latency cause. It was left unchanged to avoid truncated structured JSON. Model remains gemini-3.5-flash; prompts and evidence rules were not changed in this timeout task.

## Calls and transport review

There is one generate_content operation after local policy retrieval, with SDK retry_options.attempts=1. Application retries are separately configurable; the failed run and currently running demonstration backend are explicitly capped at one application attempt. The pre-existing configurable retry implementation was not expanded or removed. The code default remains configurable for other deployments; use the explicit demonstration startup budget below.

Retrieval sequentially embeds seven static policies on a cold policy cache and each unique clause text within the request. With twelve distinct clauses, cold work can include up to nineteen local embedding requests, warm up to twelve; exact count for the failed run was not instrumented. This is local Ollama work preceding Gemini, not sequential Gemini generation. Existing deduplication/policy-vector cache/client scope remains unchanged; no retrieval optimization was attempted.

HttpOptions.timeout is the request timeout passed to the SDK. No conflicting shorter backend HTTP client timeout was found in the request path. The installed SDK defaults to environment-aware HTTP transport; no proxy-origin fault is demonstrated by the existing failure record. Vite config supplies neither timeout nor proxyTimeout. Its installed proxy implementation applies those socket/request deadlines only if configured. Frontend analyzeContract has no internally created AbortSignal timeout and App supplies no signal. The five-second signal applies only to health checks. The HTTP smoke client allowed 400 seconds and received the structured backend failure at 95.416 seconds. Thus no shorter frontend/Vite/client limit explains this run.

## Smallest applied change

- backend/app/config.py: default configurable GEMINI_TIMEOUT_SECONDS increased from 90 to 180.
- backend/.env.example: corresponding timeout example changed to 180; backend/.env and secrets were untouched (no timeout override existed there).
- backend/app/services/gemini_analysis.py: user-facing timeout message states no analysis returned before the deadline, uploaded contract is preserved, and retry is manual or use explicit labeled demo.
- frontend/src/components/AnalysisProgressModal.jsx: waiting message says processing may take several minutes and warns against resubmission. No simulated completion or retry added.
- tests/test_gemini_deadline.py: three mocked regressions for correct millisecond conversion/SDK retry cap and intact clauses, single-attempt provider/transport timeouts with no backoff, and failure persistence with upload preservation and no successful result.
- backend/evaluation/reports/offline-tests.json: regenerated test summary.

The same local backend was restarted with process-scoped GEMINI_TIMEOUT_SECONDS=180 and GEMINI_MAX_ATTEMPTS=1. No environment-file secret, model, database schema, gold or score change. A longer bound provides headroom but **does not establish that a live response will succeed**. All unsupported-evidence safeguards remain in effect.

## Executed tests

160 backend tests discovered: **157 passed, 3 live-service tests skipped, 0 failures/errors**, 9.784 seconds, outbound network blocked. Evidence/quote regression tests remain passing. Frontend build and lint passed. Bundle-size warning and existing test dependency deprecation warning remain nonblocking. No live request was made.

## Demonstration restart command

From backend, in PowerShell:

~~~powershell
$env:GEMINI_TIMEOUT_SECONDS='180'
$env:GEMINI_MAX_ATTEMPTS='1'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

The settings are process/terminal-scoped, not secret replacements. Do not launch a duplicate server on occupied port 8000. Do not set a shorter frontend timeout than this generation window plus retrieval time. Generation timeout is not an overall analysis SLA; Ollama and persistence add time, and existing local embedding connect/read bounds still apply.

## Retest recommendation

One controlled, explicitly approved analysis of the same uploaded contract is warranted, using 180 seconds and exactly one provider attempt. Approval has not been requested or inferred as an already authorized second run; no retest executed. If it times out again, stop retries and use the genuine saved synthetic snapshot or separately labeled demo. Do not change model, lower evidence standards or fabricate results. A new successful generation is still needed to validate the quote-grounding fix against provider output. No Git push.
