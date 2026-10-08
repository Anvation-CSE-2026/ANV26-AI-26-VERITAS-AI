# Ollama HTTP connection benchmark

## Conclusion

HTTP client reuse provides a large, repeatable improvement for warm pooled connections on this local environment. Five iterations per variant, each with three real embedding requests, gave a setup-inclusive median of **6.453617 s fresh versus 0.167557 s pooled: 97.40% lower elapsed time**. All 1024-dimensional vectors were exactly equivalent, with maximum absolute difference 0.0. No live request failed.

The dominant observed cost is **new connection establishment, not HTTP client object construction**. Fresh client construction takes about 6–7 ms, while its connect_tcp trace takes about 2.036 s. A warmed pooled client makes no new TCP connection in its measured requests. This identifies the expensive phase; it does not identify why localhost connection establishment takes two seconds.

The headline improvement excludes the initial pool connection warm-up. That initial connection still costs approximately two seconds and must be paid by a newly created retrieval-scoped pool. Do not apply the 97% figure to an entire cold-start retrieval or contract analysis.

## Production inspection

backend/app/services/ollama_embeddings.py uses synchronous **httpx.Client**. Every embed_text invocation creates a client, posts one text to /api/embed, reads the response and closes the client context. Each client has its own default pool, but closing it prevents reuse across embedding invocations. There is no embedding retry loop, explicit model creation/unload or keep_alive override. Creating a client is not the same as loading an Ollama model.

Timeout configuration is unchanged: connect 5 s, read 120 s, with HTTPX's other phase defaults inherited from the configured timeout. trust_env=false; truncate=false; no authentication headers or Gemini client are used. Existing HTTP/status/timeout/connection/invalid-vector errors are explicitly handled. No production code changes were made.

## Environment and methodology

- Branch: feature/ai-reliability.
- OS: Windows-11-10.0.26200-SP0; Python 3.14.7; httpx 0.28.1.
- Ollama 0.40.1; endpoint http://localhost:11434.
- Model qwen3-embedding:0.6b; installed digest ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d; dimensions 1024.
- One fixed synthetic clause, same exact request body for both variants; input SHA-256 f05421c40ffe4a67bd29e298d14115438d10029a0820e0bb5372fa189fdc0eea. No customer contents.
- Identical timeout, model, input, truncate=false, trust_env=false and zero retry settings. Default HTTPX connection-pool limits/expiry are retained; no special retry/transport performance tuning.

Executed once from backend:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.http_connection_benchmark --live-ollama
~~~

The standalone harness requires an explicit live-Ollama flag and asserts the exact local endpoint/model. It only issues /api/version, /api/tags and /api/embed requests. It does not import or invoke Gemini generation, database storage, authentication, billing or frontend services.

A preflight embedding confirmed availability/dimensions and warmed the model. Five paired measured iterations then used alternating order: fresh/pooled, pooled/fresh, fresh/pooled, pooled/fresh, fresh/pooled. Five pairs cannot perfectly balance order, but reduce systematic first/second bias.

Each variant/iteration executes one excluded warm-up request, followed by **three measured requests**. Thus there are 15 measured requests per variant, 10 excluded warm-ups and one preflight embedding: 41 local embedding requests total. There were no additional live calls for the safety checks.

- Fresh: its warm-up client is closed; each measured request creates/closes its own client. Warm-up warms the model, but each measured connection remains new.
- Pooled: create one client per iteration, warm its connection with one excluded request, use it for all three measured requests, then close it. Clients are never shared between iterations or users.
- Client creation and close are measured independently with perf_counter. Request latency covers post through complete response-body receipt; total additionally includes JSON/vector validation, equivalence checks and cleanup.
- Fresh total includes all three creations. Pooled creation occurs before warm-up, so a separate setup-inclusive total adds that measured construction time back. The initial warm-up connection/request is excluded from both totals by design.
- HTTPcore trace callbacks record connect_tcp started/complete elapsed time and connection-event count without request text or header dumps. No request payload/model option is changed by these diagnostic callbacks.

## Raw measurements

All times below are seconds. Comma-separated values are the three requests in actual order; pooled construction has one value per iteration. Total includes close; complete individual close and warm-up durations are in JSON.

| Run order | Iteration | Variant | Measured total | Setup-inclusive total | Client creation times | Request latencies | connect_tcp durations |
|---:|---:|---|---:|---:|---|---|---|
| 1 | 1 | fresh | 6.393241 | 6.393241 | 0.008144, 0.006439, 0.006610 | 2.057726, 2.102221, 2.210511 | 2.028714, 2.019264, 2.055090 |
| 2 | 1 | pooled | 0.161463 | 0.167557 | 0.006095 | 0.078901, 0.056682, 0.024669 | 0.000000, 0.000000, 0.000000 |
| 3 | 2 | pooled | 0.235540 | 0.243955 | 0.008415 | 0.081183, 0.076968, 0.075536 | 0.000000, 0.000000, 0.000000 |
| 4 | 2 | fresh | 6.524000 | 6.524000 | 0.006430, 0.005796, 0.005989 | 2.180762, 2.149019, 2.174244 | 2.019511, 2.037961, 2.036751 |
| 5 | 3 | fresh | 6.453617 | 6.453617 | 0.005663, 0.005876, 0.011195 | 2.196540, 2.084455, 2.148243 | 2.026450, 2.044580, 2.059703 |
| 6 | 3 | pooled | 0.172519 | 0.180134 | 0.007614 | 0.116326, 0.025828, 0.028861 | 0.000000, 0.000000, 0.000000 |
| 7 | 4 | pooled | 0.115359 | 0.122495 | 0.007136 | 0.038541, 0.038532, 0.036909 | 0.000000, 0.000000, 0.000000 |
| 8 | 4 | fresh | 6.507568 | 6.507568 | 0.006202, 0.006531, 0.006412 | 2.131746, 2.163375, 2.191243 | 2.023358, 2.022288, 2.029038 |
| 9 | 5 | fresh | 6.394862 | 6.394862 | 0.006380, 0.006138, 0.005745 | 2.131341, 2.116502, 2.126748 | 2.049985, 2.036218, 2.039270 |
| 10 | 5 | pooled | 0.083852 | 0.089797 | 0.005945 | 0.025931, 0.030101, 0.026332 | 0.000000, 0.000000, 0.000000 |

Raw artifact: backend/evaluation/reports/http-connection-benchmark.json. It includes every warm-up, request status, response timing metadata, cookie count, client creation/close durations and offline safety results. No embedding vectors or contract source text are persisted.

## Median results and variability

| Variant | Median measured total | Median setup-inclusive total | Median client creation | Median single request | Total range | Sample standard deviation |
|---|---:|---:|---:|---:|---|---:|
| fresh | 6.453617 | 6.453617 | 0.006380 | 2.148243 | 6.393241–6.524000 | 0.061148 |
| pooled | 0.161463 | 0.167557 | 0.007136 | 0.038532 | 0.083852–0.235540 | 0.058011 |

- Measured TCP connections: fresh **15**, pooled **0**. Each pooled warm-up established one connection, excluded from those measured counts.
- Measured request counts: 15 each; error counts: 0 each.
- Setup-inclusive median improvement: 97.40%, computed as (fresh median - pooled median) / fresh median × 100.
- Fresh connect_tcp median: 2.036218 s. The pooled request connect_tcp fields are zero because no connection-start event occurred, not because the initial connection was free.
- Small sample size and pooled scheduling/model-time variability limit fine-grained estimates, but the observed gap is much larger than the variation.

The connection trace covers the library's connection phase, not a packet-level DNS/address-family/OS breakdown. DNS, IPv6-to-IPv4 fallback, socket negotiation and environment behavior remain possible causes requiring further profiling. None is confirmed by this experiment. Initial model loading was not isolated; preflight/warm-ups prevent conflating a model-cold start with this connection comparison.

## Correctness, error behavior and state

- Every live response succeeded with HTTP 200, exactly one nonzero finite embedding and dimension 1024.
- All 30 measured vectors matched the preflight vector: maximum absolute element difference **0.0**, tolerance 1e-6. No scores or successful outcomes were fabricated.
- No response cookies were received. Every pooled iteration used its own new client; there is no cross-iteration/client sharing and no customer data. No live evidence of state leakage occurred.
- This single-text experiment alone cannot prove arbitrary cross-input/tenant isolation. Clients are stateful (for example, they can retain cookies), so any future production pool should be retrieval/request scoped and must not carry user authentication state.
- Six **offline MockTransport** checks exercised read timeout, connection failure and HTTP 503 mappings under fresh and borrowed/reused client lifecycles. They used unchanged production embed_text error mapping, preserved timeout values and verified a later distinct synthetic input succeeds on the reusable client without retry, stale body, authorization or cookie state. These were not real-service failures/timeouts.

Reproducible offline checks:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.http_connection_safety
~~~

All six checks passed. During preparation, the temporary helper first had a mock-factory recursion bug; extracting it into a reusable module then omitted a small wrapper class. Both benchmark-helper issues were corrected, and the final standalone checks passed. Neither affected live measurements or production code. No provider failure occurred.

Actual behavior on a stale socket, service restart, pool contention or real timeout remains untested. Offline mappings do not establish production concurrency safety. Any implementation must preserve exception categories and per-request timeouts, not silently retry or substitute a vector.

Production SQLite/WAL/SHM hashes and existence were unchanged. Protected production source hashes match pre-benchmark values. No authentication/billing calls, model/prompt/gold-label changes, frontend edits, database reset or Git push occurred.

## Recommendation

**Proceed with a separately scoped implementation of one reusable HTTP client per retrieval operation.** The improvement is meaningful on this machine. Keep exact requests/models/inputs, trust_env=false, timeouts and existing error handling; use deterministic cleanup and avoid a global authenticated or cross-user client. The first connection remains necessary, but subsequent independent embeddings can reuse it.

Before production adoption, test stale connections/service restarts, concurrent analyses, cleanup after exceptions, bounded pool behavior and no cross-user headers/cookies. Re-run retrieval top-k/vector equivalence and a full offline regression suite. Profile the approximately two-second localhost connect phase separately; fixing endpoint resolution or OS connection behavior may be another opportunity, but no endpoint change is recommended without measurement.

No production change is implemented in this task. The warmed-pool 97.40% result should not be represented as the expected end-to-end Gemini analysis improvement. A fresh retrieval-scoped client pays an initial connection cost; real mixed-text retrieval must be measured after implementation.

## Files added

- backend/evaluation/http_connection_benchmark.py: explicit local synthetic experiment.
- backend/evaluation/http_connection_safety.py: offline lifecycle/error recovery checks.
- backend/evaluation/reports/http-connection-benchmark.json: raw real measurements and safety results.
- docs/AI_HTTP_CONNECTION_BENCHMARK.md: this report.

No full regression rerun was needed for production behavior, because production source was unchanged; the preceding 134-pass/3-live-skip result remains the existing regression record.
