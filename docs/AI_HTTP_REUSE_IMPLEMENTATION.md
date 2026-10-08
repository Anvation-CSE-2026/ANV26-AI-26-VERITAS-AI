# Request-scoped Ollama HTTP reuse implementation

## Result

Implemented one HTTP client per synchronous policy-retrieval operation, with deterministic closure before Gemini reasoning begins. Real synthetic Ollama retrieval, including initial connection setup, measured:

| Condition | Deduplicated fresh clients (median seconds) | Scoped reuse (median seconds) | Reduction | Embedding requests before / after |
|---|---:|---:|---:|---:|
| cold policy cache | 24.009864 | 2.601818 | 89.16% | 11 / 11 |
| warm policy cache | 8.606617 | 2.403496 | 72.07% | 4 / 4 |

All 12 measured runs preserved all 18 top-three outputs, six clause entries/IDs/order and similarity scores. Maximum absolute score difference: 0.0 (tolerance 1e-6). No live errors occurred; production SQLite/WAL/SHM hashes were unchanged. No Gemini calls were made.

Final regression: **147 discovered; 144 passed; 3 live-service tests skipped; 0 failures/errors**. Authentication, billing, contract interfaces, evidence verification and benchmark tests passed. These are offline/mocked compatibility checks, not actual billing or Gemini validation.

## Files modified

| File | Change |
|---|---|
| backend/app/services/ollama_embeddings.py | Context-local client scope, compatible borrowing, deterministic cleanup and unchanged standalone behavior. |
| backend/app/services/policy_matching.py | Decorates retrieval with the client lifecycle inside the existing timing span. |
| tests/test_http_reuse.py (new) | Ten lifecycle, concurrency, equivalence, configuration, privacy and error tests. |
| backend/evaluation/http_reuse_retrieval_benchmark.py (new) | Explicit local-only fresh-deduplicated versus scoped-reuse comparison. |
| backend/evaluation/reports/http-reuse-real-retrieval.json (new) | Raw real measurements and equivalence results. |
| backend/evaluation/reports/offline-tests.json | Actual final regression result. |
| docs/AI_HTTP_REUSE_IMPLEMENTATION.md (new) | This report. |

No requirements update was needed; contextvars/contextlib/functools/threading are standard library. Earlier uncommitted work and historical benchmark reports were preserved.

## Inspection and lifecycle decision

The four prior audit/benchmark reports were reviewed. The actual API analysis handler, analyze_contract, match_policies and embed_text are synchronous. All current analysis embeddings occur within match_policies: cold policy vectors first, then exact clause-text queries. The existing policy LRU is process-local; clause deduplication is a local dictionary. The previous embed_text created/closed httpx.Client for every call. HTTPX timeout phase settings are connect 5 s and read/write/pool 120 s in this environment; trust_env=false and no embedding retries. Ollama endpoint remains http://localhost:11434 and model qwen3-embedding:0.6b.

The smallest safe boundary is **one retrieval call**, which is the embedding portion of one contract-analysis operation. Retaining a socket while Gemini reasons or SQLite persists would add no current reuse benefit. The client therefore closes on retrieval success before those later stages; if retrieval fails, it closes before analysis failure persistence. No changes to the Gemini orchestration, evidence acceptance rules, authentication/billing lifecycle or public function signatures are needed.

The outer policy_retrieval timing decorator wraps client creation, retrieval and client closure. Inside it, with_embedding_client establishes a new embedding_client_scope for every call. The scope always creates its own client, even when nested; it does not inherit another analysis's client.

A ContextVar stores only the active client and compatibility key; no module-level customer embeddings or persistent client singleton is introduced. embed_text borrows it only when endpoint, model, timeout settings and executing thread identity match. Otherwise it uses a temporary fresh client. This guards incompatible settings or a context copied into another thread. Configuration is normally immutable during a request; runtime changes are not silently treated as compatible.

Standalone embed_text calls retain one-shot client creation/closure, the existing text validation, payload, response/vector validation and error classifications. The API embedding-test response remains unchanged.

## Cleanup and state isolation

The client is owned by its HTTPX context manager. A finally block resets the ContextVar token, and context exit closes the client on success, ordinary exceptions or interruptions such as KeyboardInterrupt. Nested scopes restore the parent token/client instead of leaving a closed inner client active. Clients are not put in production SQLite or reused by the next request.

A reused client clears response cookies before each embedding request. The old fresh-client behavior never carried cookies between embeddings; clearing preserves that behavior and avoids response-cookie state affecting a later request. No user authentication headers or credentials are added. No contract text or vectors are logged.

The exact JSON payload remains model, input=text, truncate=false. Timeout configuration and trust_env=false are unchanged, and no retry loop was added. Existing request failures abort retrieval instead of returning a fallback vector. Scope creation/transport timeouts map to EmbeddingTimeout; connection failures map to EmbeddingUnavailable. HTTP status failures and invalid vectors retain EmbeddingError. The existing Gemini retry logic is untouched.

## Concurrency safety

Each synchronous FastAPI analysis invocation creates a distinct retrieval scope in its execution context/thread. Concurrent retrievals do not share clients, cookies or the local clause-vector dictionary. A thread-identity compatibility check prevents direct borrowing of a parent client from another thread. Every new match_policies invocation establishes its own scope; nested retrievals also create distinct clients.

A concurrent two-worker test synchronized first requests and verified two clients, four clause embedding requests per client under a warm mocked policy cache, equal rankings and closure of both clients. The existing immutable policy-vector LRU remains shared as before; cold concurrent misses can still compute duplicate policy tuples. No new cache or locking behavior was added.

This implementation is intentionally synchronous. A future asynchronous embedding path requires an explicit async lifecycle; do not assume ContextVar inheritance makes arbitrary async child-task borrowing safe.

## Automated testing and error validation

New tests cover:

1. One client reused across 11 cold embedding requests; closure on success; a second analysis uses a different client with four warm-policy calls.
2. Equal vectors, cosine scores, ranking and top-k against the deduplicated unscoped loop, retaining 18 outputs and every original clause ID/order.
3. Read timeout, connection error, HTTP failure and malformed embeddings: original classifications, one attempted request/no retry, scope reset and client closed.
4. KeyboardInterrupt cleanup and scope reset.
5. Exact payload, timeout fields and no response-cookie/authorization leakage across distinct inputs.
6. Two concurrent retrievals with isolated clients and correct request counts.
7. Nested scope restoration and standalone embeddings creating a separate client after scope exit.
8. Client-construction timeout classification without leaking a context token.
9. Actual production client factory preserves configured connect/read/write/pool timeout values and trust_env=false.
10. No synthetic sensitive sentinel/source output on stdout/stderr.

The existing exact-text deduplication tests still pass across all 12 fixtures, including configuration-key separation and separate-request cache isolation. Evidence, risk scoring, model prompts and gold annotations were not changed.

Executed from backend:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.run_offline_tests
~~~

The initial pre-benchmark suite passed with 143 passed/3 skipped. After adding the direct client-factory configuration assertion, the full suite passed again with **144 passed/3 skipped**. No production changes occurred after the pre-benchmark implementation. Live opt-ins are removed and outbound sockets blocked by the regression harness. An existing Starlette/httpx deprecation warning remains; no test failures occurred. Fixture benchmark scores remain TP=17/FP=3/FN=7, which are evaluator checks rather than Gemini accuracy.

## Real Ollama benchmark methodology

Executed once after the implementation tests passed:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.http_reuse_retrieval_benchmark --live-ollama
~~~

Both variants deduplicate exact clause text. In JSON, original means the previous **deduplicated no-HTTP-reuse loop**, not the older 13-request implementation; optimized means production match_policies with scoped reuse. A separate reference function copies the prior deduplicated loop without altering production code for the comparison. Both variants use the same production embedding payload, validation, policy cache, cosine/ranking and timing observer.

Environment: Windows-11-10.0.26200-SP0; Python 3.14.7; httpx 0.28.1; Ollama 0.40.1. Model qwen3-embedding:0.6b digest ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d; dimensions 1024. Contract SYN-supplier_red; playbook sample-company-policy v1.0; 3 pages/6 clauses/7 rules. Exact input/policy hashes and configuration are retained in JSON. The synthetic fixture loader validates PDF/source/hashes; no customer data was used.

One preflight embedding and one full cold-policy-cache warm-up per variant precede measurement. Three measured iterations per variant **in each cache state** give 12 measured retrievals. Pair order alternates original/optimized, optimized/original, original/optimized. Cold policy-cache groups run before warm groups. The model remains warmed; cold means Python policy-cache cold, not unloaded Ollama model.

For each cold run the policy LRU is cleared. For warm runs, seven policy vectors are prepared outside timing using a separate temporary client scope, identical for both variants; that preparation client closes before measurement. Thus the timed scoped-reuse retrieval always opens a **new, unconnected client**. Warm model or policy cache does not imply a warm HTTP connection. Time includes client construction, first connection setup, embedding requests, validation, ranking and client closure.

Version/tag/residency GETs and policy preparation are outside retrieval timing. The harness permits only local Ollama endpoints, captures sanitized per-request duration/status metadata and compares stored IDs/order/top-k and scores. It neither imports/calls generation nor opens a SQLite connection. Preparation calls are explicitly listed in JSON; no warmup/preparation work is presented as free end-to-end analysis.

## Raw retrieval and per-request measurements

All times are seconds; request sequences are in actual embedding order.

| Order | Policy cache | Iteration | Variant | Total retrieval | Requests | Per-request embedding seconds |
|---:|---|---:|---|---:|---:|---|
| 1 | cold | 1 | Deduplicated fresh | 24.021708 | 11 | 2.245627, 2.171003, 2.215292, 2.215378, 2.279674, 2.132506, 2.211621, 2.149879, 2.124479, 2.129244, 2.133171 |
| 2 | cold | 1 | Scoped reuse | 2.601818 | 11 | 2.170172, 0.105446, 0.034383, 0.048808, 0.033958, 0.036606, 0.032275, 0.030034, 0.027327, 0.031129, 0.031270 |
| 3 | cold | 2 | Scoped reuse | 2.664917 | 11 | 2.150777, 0.104671, 0.103069, 0.055921, 0.033050, 0.034150, 0.032914, 0.029550, 0.032418, 0.031311, 0.034543 |
| 4 | cold | 2 | Deduplicated fresh | 24.009864 | 11 | 2.160504, 2.136602, 2.145665, 2.210040, 2.202968, 2.230297, 2.198456, 2.167384, 2.185904, 2.102071, 2.256132 |
| 5 | cold | 3 | Deduplicated fresh | 23.794259 | 11 | 2.162206, 2.131759, 2.161874, 2.151339, 2.148526, 2.222207, 2.161717, 2.194583, 2.106328, 2.201979, 2.137095 |
| 6 | cold | 3 | Scoped reuse | 2.585545 | 11 | 2.155028, 0.109272, 0.035026, 0.034095, 0.034080, 0.039013, 0.033786, 0.029090, 0.028045, 0.033390, 0.032078 |
| 7 | warm | 1 | Deduplicated fresh | 8.591030 | 4 | 2.096945, 2.200369, 2.115139, 2.164905 |
| 8 | warm | 1 | Scoped reuse | 2.403496 | 4 | 2.128091, 0.092633, 0.095364, 0.065498 |
| 9 | warm | 2 | Scoped reuse | 2.416086 | 4 | 2.105486, 0.103902, 0.090461, 0.095711 |
| 10 | warm | 2 | Deduplicated fresh | 8.606617 | 4 | 2.112083, 2.129008, 2.214102, 2.137507 |
| 11 | warm | 3 | Deduplicated fresh | 8.718233 | 4 | 2.117217, 2.216616, 2.114701, 2.256213 |
| 12 | warm | 3 | Scoped reuse | 2.327779 | 4 | 2.100356, 0.084674, 0.088373, 0.033455 |

Cold runs have seven policy calls followed by four unique clause calls; warm runs have only the four unique clause calls. Header embeddings are reused without dropping their page/ID entries. The first request in every pooled run includes initial connection setup (about two seconds); remaining calls use the scoped connection. Scope creation/closure are included in total retrieval, not necessarily in individual embedding spans.

Raw artifact: backend/evaluation/reports/http-reuse-real-retrieval.json. It preserves medians, every per-request latency, HTTP status, provider timing metadata, initial warm-ups, policy preparation counts, residency, results and comparison differences. No source contract quotations, API keys or full embedding vectors are emitted to logs/artifacts.

## Equivalence and safety results

- All 12 measured retrievals returned 18 results with exactly matching clause IDs, duplicate entries, result ordering and top-three policy IDs.
- Maximum score difference across all measured runs: **0.0**; no differences recorded.
- Cold calls remain 11 and warm calls remain 4 for both variants: deduplication and policy caching are preserved.
- All embedding HTTP responses succeeded. No service errors, retries or synthetic substitutions occurred.
- Production SQLite/WAL/SHM existence/hash checks match before/after; the benchmark used filesystem reads only.
- Preservation hashes show Gemini service/prompt code, evidence verifier, settings and gold manifest unchanged. No model replacement or prompt changes.

## Limitations and recommended next step

This is a one-contract/local-environment benchmark with three samples per variant/cache condition. Background load was uncontrolled, and alternating three pairs is not perfectly balanced. It establishes a retrieval improvement here, not a 97% end-to-end contract analysis speedup; Gemini generation was never called. Full analysis latency with persistence/generation remains unmeasured after this change.

Actual Ollama downtime, stale-socket restart recovery and pool contention were not deliberately induced; timeout/HTTP/connection error classifications were validated with mock transports. HTTPX may reconnect an expired/closed socket normally, but no explicit application retry is added. Each client is bounded to retrieval and reliably closed; settings/model mutation mid-operation is outside normal configuration and falls back to fresh clients when compatibility changes.

The approximately two-second initial localhost connection cost remains. Recommended next step: profile that connection phase/address resolution and stale-connection behavior using synthetic embedding-only checks, then repeat this benchmark on a second synthetic contract. Keep endpoint/model fixed until evidence justifies a change. A separately authorized live Gemini analysis can later measure end-to-end impact; no such call was made here. No further optimization, frontend/authentication/Razorpay change, database reset or Git push was performed.
