# Request-local embedding deduplication report

## Result

Implemented exact-text clause embedding reuse inside a single match_policies invocation. For the synthetic SYN-supplier_red fixture, cold-policy-cache embedding calls fall from **13 to 11**, and warm-policy-cache calls fall from **6 to 4**. All six clause records, original IDs/order, 42 policy comparisons and 18 ranked outputs are preserved. No Gemini or Ollama calls were made for this task.

## Files modified

| File | Change |
|---|---|
| backend/app/services/policy_matching.py | Retrieval-local dictionary for identical clause embedding inputs/configuration. |
| tests/test_embedding_deduplication.py (new) | Eight isolation/equivalence/error/privacy tests plus a reproducible simulated measurement harness. |
| tests/test_observability.py | Expected real embedding spans in the mocked cold-cache pipeline updated from 13 to 11. |
| backend/evaluation/reports/embedding-deduplication-simulated.json (new) | Raw mock timing samples, call counts and medians. |
| backend/evaluation/reports/offline-tests.json | Actual full regression result. |
| docs/AI_EMBEDDING_DEDUPLICATION_REPORT.md (new) | This report. |

Earlier uncommitted work was preserved. No embedding client, Gemini prompt/model settings, evidence verifier, cosine implementation, ranking/thresholds, gold annotations, authentication, Razorpay, frontend or database schema/storage logic was changed. No requirements update was necessary. No database reset or Git push occurred.

## Implementation and isolation

The existing policy-vector LRU remains unchanged; this task introduces no additional persistent/shared policy or customer-data cache. The new clause_vectors dictionary is a local variable created for every match_policies call. It is not stored on a singleton, module, request object, application state, database or trace. It becomes unreachable as the invocation returns/unwinds, subject to normal Python frame/exception lifetimes.

The key is the exact input string plus configured embedding model, base URL, connection timeout, read timeout, /api/embed endpoint suffix and current truncate=false/trust_env=false flags. Keys are recomputed before each clause, so a changed model/endpoint/timeout does not reuse the old entry even inside an invocation. Nothing strips whitespace, normalizes Unicode, case-folds, hashes into a lossy representation or uses semantic similarity to merge inputs.

Only successfully returned embeddings are inserted. Existing embed_text validation, timeout types, connection errors, HTTP error behavior and no-retry behavior are untouched. Exceptions propagate immediately; no fallback vector or failed result is cached. A separate analysis request starts with a new empty clause dictionary. The pre-existing immutable policy cache can still be warm across requests; contract-specific vectors cannot.

The original clause loop is intact. On a cache hit it reuses the vector, then performs the unchanged per-policy cosine calculations, stable descending sort and top-three selection for that particular original clause ID. Duplicate texts and even duplicate clause entries are not removed; all original entries still produce outputs in original order. No threshold was introduced. Policy strings still use category + ': ' + rule and are handled by the existing policy_vectors cache.

Exact repeated inputs identified by the audit: P001-C001, P002-C001 and P003-C001 all contain the identical synthetic agreement page header. P001-C002, P002-C002 and P003-C002 are distinct substantive clauses. There are four unique clause inputs and seven unique policy inputs. The local map embeds the first header once and reuses it twice, without filtering page headers or changing segmentation.

## Retrieval equivalence and safety tests

All eight new tests passed:

1. Identical header text is embedded once; all clause IDs/order and 18 outputs remain intact; the input Contract is unchanged.
2. Different trailing whitespace, line endings and Unicode strings produce distinct embedding calls.
3. Separate retrieval requests do not share clause embeddings; cold first call makes 11 requests and second warm-policy call makes four.
4. Model, URL, connect timeout and read timeout changes between identical clauses force a new embedding call. Tests mutate only mocked settings and restore them afterward.
5. All 12 synthetic fixtures match the pre-change reference loop's clause/policy ordering; every cosine score agrees within abs/relative tolerance 1e-12 using deterministic 1024-dimensional synthetic vectors.
6. Equal-score ties preserve the original playbook ordering.
7. EmbeddingTimeout, EmbeddingUnavailable and EmbeddingError propagate as the original exception without retry/fallback; a later request recomputes rather than inheriting a failed/incomplete clause cache.
8. Sensitive synthetic sentinel text is absent from stdout/stderr; the implementation introduces no logging.

The existing mocked full extraction-to-persistence observability test now sees 11 embedding_request spans instead of 13. Cache hits do not call the instrumented client, so only actual simulated provider requests create embedding spans; policy_retrieval still measures the complete retrieval operation. No trace schema or raw logging changes were needed.

Equivalence is validated offline with deterministic mock vectors. Real Ollama vector repeatability and live speed were not tested in this task, and no Gemini accuracy claim is made.

## Before/after performance measurement

Executed from backend:

~~~powershell
.\.venv\Scripts\python.exe ../tests/test_embedding_deduplication.py --measure
~~~

**SIMULATED MOCK TIMING — NOT REAL OLLAMA PERFORMANCE.** The same synthetic contract, seven policies and deterministic 1024-dimensional vectors were used for both implementations. Each mock embedding invocation slept 20 ms, then returned a copy of its predefined vector. The baseline reference reproduces the original no-clause-cache loop and uses the same existing policy cache, cosine utility and ranking behavior.

Each variant ran five times. Before/after order alternated; the policy cache was cleared for every variant. Warm variants prefilled policy vectors outside the measured interval, then reset the mock call counter. All runs were network-blocked and all output rankings/scores were equal. Full regression tests ran concurrently with this measurement; scheduler noise is possible, so medians are diagnostic simulated measurements, not a precision microbenchmark.

| Policy cache condition | Calls before | Calls after | Median seconds before | Median seconds after |
|---|---:|---:|---:|---:|
| Cold | 13 | 11 | 0.283621 | 0.243471 |
| Warm | 6 | 4 | 0.149452 | 0.108253 |

These observed simulated reductions are approximately two 20-ms delays plus measurement overhead. They do not establish the live improvement. The historical pre-change live retrieval time was 28.099807 seconds, with two redundant header spans totaling 4.218655 seconds; **no comparable real post-change latency is available**. Do not subtract those old durations and present the result as a measured live latency.

Raw samples and configuration are in backend/evaluation/reports/embedding-deduplication-simulated.json.

## Full backend regression

Executed from backend:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.run_offline_tests
~~~

Actual result: **137 discovered; 134 passed; 3 live-service tests skipped; 0 failures; 0 errors.** The suite disables live opt-ins and blocks outbound network.

Authentication registration/login/token access/isolation tests passed. Billing trial, quotas, checkout, payment signature and idempotent webhook tests passed with mocked payment interactions; no actual payment was triggered. Contract upload/analysis/retrieval and error response tests passed. Evidence provenance, omissions, party/deadline handling and all existing benchmark metrics/tests passed. These are automated compatibility checks, not live external-service or payment validation.

The fixture evaluation still reports TP=17, FP=3, FN=7 across 12 cases; fixture results are evaluator checks, not Gemini accuracy. The suite emitted the existing Starlette/httpx deprecation warning, with no test failures.

SHA-256 preservation checks found no change to the embedding client, Gemini service, evidence verifier, settings file, risk/evidence scoring modules or dataset manifest. All 38 manifest-listed fixture files match their frozen hashes. The only production implementation change is the local clause-vector lookup in policy_matching.py.

## Known limitations

- Real provider performance and nondeterministic vector variation remain unmeasured. Exact input/config reuse assumes stable embeddings from the same model for the duration of one request; tests prove control-flow/ranking equivalence for identical deterministic vectors.
- The local key tracks the current client configuration. Future request options (instruction prefixes, dimensions, truncation or endpoint changes) must be reflected in the key if added. Same model tag changing its weights during one request is not detected; normal configuration should remain fixed during an analysis.
- The existing policy LRU remains process-local and cold on restart. Seven policy calls still occur on a cold cache. The new dictionary does not address repeated embeddings across requests, because cross-user customer-data reuse is deliberately outside scope.
- The dictionary retains one vector per unique clause plus text/config keys until retrieval ends. Memory scales with unique clauses/dimension under existing extraction limits; no persistent text/vector storage is added. Python float/list overhead exceeds packed numeric-vector sizes.
- Failed request frames may remain while their exception traceback is held, as with existing Python processing; no module/application cache retains the dictionary or failed embeddings.
- No batching, connection pooling, precompute artifacts or new retries were implemented. Unique inputs still use sequential independent clients.
- Counts/timings in historical reports describe their original runs and were not rewritten to claim deduplication was active then.

## Recommended next optimization

Profile and then consider **HTTP client/connection reuse within one retrieval operation**, preserving trust_env=false, timeout settings, singleton request payloads and current error handling. It avoids persistent customer-vector caching and has low ranking risk. First measure client setup, transport and server compute using approved synthetic embedding-only checks; do not assume this removes the approximately two-second cost seen in old spans. Evaluate batching separately only after compatible array-response validation and actual throughput measurements. Gemini calls are unnecessary for those retrieval checks.
