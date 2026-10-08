# Policy retrieval performance audit

## Conclusion and scope

The 28.099807-second retrieval span consists almost entirely of **13 sequential, single-text Ollama requests**: seven policy embeddings and six clause embeddings. Their measured sum is 28.085011 seconds (99.947% of retrieval); the remaining 0.014797 seconds covers all other retrieval work, including Python ranking and observer overhead, rather than a separately measured cosine-search duration.

Three clause inputs are identical page headers. The seven policy vectors already have a process-local cache, but a new benchmark process starts cold. Every request creates and closes a new HTTP client, preventing connection reuse across calls. These facts explain the call count and additive latency; they do not establish why each request takes approximately 2.16 seconds. Server compute, model load and transport/client setup were not timed separately.

This audit used source inspection, the existing synthetic live trace and offline mocks/tests only. No Gemini or Ollama requests were made. No optimization was implemented and no production behavior, model, prompt, ranking, threshold, evidence rule, gold label, authentication, billing or frontend was changed. Branch: feature/ai-reliability. The prior dirty working tree was preserved.

## Current architecture

Relevant source:

- backend/app/services/policy_matching.py: policy_vectors and match_policies.
- backend/app/services/ollama_embeddings.py: embed_text and cosine_similarity.
- backend/app/services/pdf_extraction.py: original extracted clause segmentation.
- backend/app/services/contract_analysis.py: retrieval precedes Gemini generation.
- backend/evaluation/live_adapter.py: fresh standalone process, sequential cases, isolated SQLite.
- tests/test_contract_analysis.py: RetrievalTests.test_actual_vector_ranking_and_cache.
- tests/test_observability.py: mocked full-pipeline trace/count test.

match_policies first requests the complete policy vector tuple. For each playbook rule, the input is exactly category + ': ' + rule.rule. It then iterates all extracted clauses in order, embedding each original clause.text without query expansion, model-generated queries, instruction prefixes, normalization, deduplication or header filtering. The segmenter preserves page headers as clauses, hence six clauses for three substantive provisions.

Each clause vector is compared against every policy vector using the existing finite/nonzero-vector checks and normalized cosine computation. Scores are clamped to [-1, 1]. Python sorts in descending score order and retains three matches per clause. Equal-score ordering follows the stable playbook order. For this case: 6 clauses × 7 policies = 42 comparisons and 18 returned semantic matches. There is no vector database, ANN index or similarity cutoff in this path. All policy rules remain available to Gemini; retrieval ranks contextual matches rather than restricting the complete playbook.

### Cache and request lifecycle

policy_vectors uses lru_cache(maxsize=16), keyed by endpoint, model identifier and the ordered tuple of exact category/rule strings. It caches a whole playbook vector tuple, not individual rules. Recommendation-only or policy-ID changes with identical embedding texts can safely reuse vectors, since the downstream mapping uses current rules. Any changed rule/order creates a new cache entry and re-embeds every policy. Failures are not cached. The cache is per process, lost on restart, not shared across workers and can allow concurrent duplicate fills. There is no clause/query embedding cache.

The standalone live benchmark's new Python process had no warmed policy_vectors entry. The separate preflight embedding ran in another process and could not warm this Python cache. Ollama daemon residency is a separate matter. A persistent backend worker can reuse all seven policy embeddings on subsequent analyses without an optimization change.

embed_text opens httpx.Client(timeout=..., trust_env=False) inside each invocation and closes it afterward. It posts one string to /api/embed with the configured model and truncate=false, validates exactly one finite, nonzero vector, then returns Python floats. There is no batch interface, connection pool surviving across invocations or embedding retry loop. The code does not instantiate an Ollama model directly, explicitly unload it, or set keep_alive. A new HTTP client is not proof of server model reinitialization.

Existing trace configuration: connect timeout 5 seconds; read timeout 120 seconds. The httpx default timeout also supplies the other phase defaults. These are phase/inactivity limits, not a whole-retrieval deadline; 13 sequential slow requests can accumulate substantial duration. Timeout/HTTP/connection failures stop retrieval with the existing explicit error, without embedding retries or synthetic fallback. Gemini retries are downstream and did not contribute to this retrieval span.

## Explanation of every request

Input associations below are reconstructed from the deterministic source loop order and validated fixture/playbook order. The trace has ordered embedding spans, but no per-span purpose/input hash, so the IDs are source-based attribution rather than directly logged trace fields. The network-blocked mock independently confirmed the exact order and repeated header inputs.

| Request | Source ID | Purpose/input construction | Repetition | Seconds | Contract-specific source? |
|---:|---|---|---|---:|---|
| 1 | POL-LIAB-001 | Policy category + literal rule | Unique in this run | 2.219771 | No |
| 2 | POL-INDEM-001 | Policy category + literal rule | Unique in this run | 2.152777 | No |
| 3 | POL-TERM-001 | Policy category + literal rule | Unique in this run | 2.135307 | No |
| 4 | POL-CONF-001 | Policy category + literal rule | Unique in this run | 2.152182 | No |
| 5 | POL-PAY-001 | Policy category + literal rule | Unique in this run | 2.133348 | No |
| 6 | POL-DATA-001 | Policy category + literal rule | Unique in this run | 2.134128 | No |
| 7 | POL-IP-001 | Policy category + literal rule | Unique in this run | 2.213702 | No |
| 8 | P001-C001 | Original extracted clause text | Unique in this run | 2.107463 | Yes |
| 9 | P001-C002 | Original extracted clause text | Unique in this run | 2.206934 | Yes |
| 10 | P002-C001 | Original extracted clause text | Same as request 8 | 2.114590 | Yes |
| 11 | P002-C002 | Original extracted clause text | Unique in this run | 2.210045 | Yes |
| 12 | P003-C001 | Original extracted clause text | Same as request 8 | 2.104066 | Yes |
| 13 | P003-C002 | Original extracted clause text | Unique in this run | 2.200697 | Yes |

Requests 1–7 correspond to liability, indemnification, termination, confidentiality, payment, data protection and intellectual property respectively. Requests 8/10/12 are the identical synthetic agreement page header. Requests 9/11/13 are substantive liability, indemnification and payment clauses. No real contract text was read or logged for this audit; the table uses fixture IDs instead of repeating source text.

### Independence, reuse, batching and caching

| Requests | Independent? | Batch candidate? | Safe reuse/cache scope | Contract dependence |
|---|---|---|---|---|
| 1–7 policies | Yes: each embedding is based on its own immutable input. Clause embedding does not require policy output. | Potentially: exact strings in a validated multi-input interface, retaining original order. Actual version behavior/performance must be tested later. | Existing in-memory policy cache; future per-rule or persistent vectors keyed by exact text, endpoint and pinned model identity. Reusable across eligible analyses using the same policy/model. | None; rules are playbook data, which can still be sensitive company information. |
| 8 first header | Yes. | Potentially with unique clauses or policies. | Request-local exact-text map. Preserve a vector reference for all three clause IDs. Cross-contract caching is unnecessary and increases privacy risks. | Extracted contract content, even though it is a synthetic header here. |
| 10, 12 duplicate headers | Yes; computation inputs equal request 8. | Deduplicate before any batch, rather than batch three identical strings. | Reuse request 8 vector within this analysis; do not remove the clauses or their output matches. | Same contract header repeated on other pages. |
| 9 liability, 11 indemnification, 13 payment | Yes; distinct texts. Ranking waits for vectors but vector generation has no cross-input data dependency. | Potentially; verify vector-to-input mapping and failure semantics. | Request-local cache if later repeats occur. Across repeated analysis of the same contract, reuse requires exact text/model match and deliberate secure scope/invalidation. | Yes; never use an unscoped global customer-text cache. |

No semantic query generation repeats exist beyond exact source text repetition. In this run there are 11 distinct total inputs and four distinct clause inputs. There are no duplicates among the seven policy strings and none equal to clause strings.

## Measured bottlenecks and missing instrumentation

Source trace: backend/evaluation/private_traces/1a9c514b-3b7b-4f60-839a-8d14558f60de/d2144a9f-147a-4468-9ec0-7763481b2c2b/trace.json (owner-only and gitignored).

| Measurement | Seconds |
|---|---:|
| Total traced analysis | 53.278278 |
| Retrieval inclusive span | 28.099807 |
| All 13 embedding spans, sequential sum | 28.085011 |
| Seven policy embedding spans | 15.141215 |
| Six clause embedding spans | 12.943796 |
| Two avoidable duplicate header spans (10 + 12) | 4.218655 |
| Residual retrieval work | 0.014797 |
| Mean single embedding request | 2.160385 |
| Minimum / maximum single request | 2.104066 / 2.219771 |
| Gemini inclusive generation | 25.125053 |

All embedding spans completed. Retrieval is about 52.74% of total traced analysis. Narrow request-time dispersion across short headers and longer inputs is consistent with a common per-call cost, but does not prove excess network overhead. The first request is only modestly slower; neither repeated model loading nor absence of loading is established by that fact.

Unmeasured: HTTP client construction versus connection versus server processing, provider model-load/evaluation timing fields, keep-alive state, queue contention, CPU/GPU utilization, per-input tokens, batch throughput, warm-daemon versus cold-daemon latency and a standalone cosine-search span. The client keeps only embeddings from the response; any server timing fields are not captured. No model initialization optimization is justified until those causes are measured.

## Ranked optimization opportunities and trade-offs

Ranks prioritize observed removable work, then implementation/ranking risk. Unknown gains are explicitly unquantified; batching and connection reuse may outperform measured call elimination but cannot be ranked numerically from this trace alone.

| Rank / opportunity | Expected latency reduction | Complexity | Retrieval-result risk | Memory/storage | Security considerations |
|---|---|---|---|---|---|
| 1. Exploit existing warm policy cache; optionally precompute/persist immutable policy vectors | Seven cold requests account for 15.14 s here. Warm-cache call reduction 13→6 is confirmed offline. Persistent precompute can remove that cost from first analysis, but preparation work still exists. | No code for ordinary worker reuse; medium for warmup lifecycle or durable precompute. | Low with exact keys/pinned model; stale vectors are the main risk. | Seven × 1024 scalars per playbook; persistent artifact small but needs metadata. | Playbooks may be confidential. Controlled private artifacts; verify integrity and trusted serialization. No unapproved live startup calls. |
| 2. Exact-text deduplication within an analysis | Two repeated header requests account for 4.22 s here; cold calls 13→11, warm 6→4 for this fixture. General benefit depends on repeated text. | Low; compute once then expand to all original clause IDs. | Low, but confirm fixed-model repeatability and preserve all matches/tie order. No whitespace or semantic normalization. | Map proportional to unique clause inputs; discard after analysis. | Avoid global customer-text retention and cross-tenant caches. Bound memory; do not log map keys/text. |
| 3. Reuse an HTTP connection/client during a retrieval operation | Unknown; removes repeated client setup and allows connection reuse across up to 13 calls. Not measured independently. | Low–medium; lifecycle/timeout cleanup and injection for tests. | Very low if exact requests/options remain identical. | Small bounded connection pool. | Preserve trust_env=false, endpoint isolation, timeouts and cleanup. Do not reuse authenticated Gemini clients or mix tenants/secrets. |
| 4. Batch independent unique inputs | Unknown. Could reduce transport/call overhead substantially; server may still compute sequentially or batches may increase queue/memory pressure. No batch latency measurement. | Medium; array interface, ordered mapping, chunking, response validation and explicit batch-error behavior. | Low–medium until singleton-versus-batch vectors and rank order are verified. Never concatenate texts into one embedding. | Larger input/response buffers and potentially server tensor memory. Bounded batches required. | Prefer one contract per batch; avoid exposing other tenants' data through mixed batches/error reporting. Preserve truncation/error handling. |
| 5. Per-rule persistent cache/precomputed vectors beyond the existing whole-playbook LRU | Can avoid seven calls across process restarts, and re-embed only changed rules. Same removable policy cost as rank 1; not additive. | Medium–high for invalidation, concurrency, artifact schema and atomic writes. | Medium if tags are reused for changed model weights or different server builds. | Durable vector storage scales with rule/model revisions and retained snapshots. | Private policy data; checksum/signature validation, no pickle/untrusted executable format. Explicit retention/access controls. |

Storage estimates: seven 1024-dimensional vectors require 28 KiB if float32, or 56 KiB if float64. Current cache stores Python float tuples, with substantially higher interpreter overhead; these packed sizes are not current heap measurements. maxsize=16 bounds entry count, not total bytes when playbooks have variable rule counts. Contract-local maps must also be byte/input bounded.

Cache identity must include exact embedding input and endpoint/model identity; a model tag alone can remain unchanged while weights change. Pin/record a model digest or other validated model revision for persistent caches. The present policy_vectors function uses URL/model arguments as keys but embed_text reads current global settings; future concurrent mutable settings must not be mistaken for independently scoped embedding configuration. Normal match_policies calls pass current settings; no such configuration race was demonstrated here.

### Quantified scenarios, not performance promises

If the observed request durations were unchanged and only the indicated calls disappeared:

- A warm policy cache would remove 15.141215 s, leaving about 12.958592 s of retrieval.
- Exact within-contract deduplication would remove 4.218655 s, leaving about 23.881152 s on a cold cache.
- Combining both would remove 19.359871 s, leaving about 8.739937 s of retrieval (four unique clause inputs).

These are arithmetic scenarios from one trace, **not measured optimized latencies**. Cache warming moves work earlier; persistent reuse amortizes work across analyses. Connection reuse/batching effects cannot be estimated from these scenarios, and gains cannot be added blindly. Gemini remains about 25.13 s in this run, so retrieval changes would not eliminate the other large stage.

## Recommended first change

For the first new implementation, choose **request-local exact-text clause deduplication**, while retaining the existing policy cache. It removes two confirmed redundant computations with low complexity and no persistent customer-data cache. Reuse vectors, not clause records: every original clause must still receive the same policy comparisons, IDs and ordered top-three outputs. Do not remove headers or change segmentation, prompts, cosine math, ranking, thresholds or evidence rules.

Operationally, first recognize the existing warm-cache benefit in persistent workers; a cold standalone benchmark does not represent every backend request. Do not add startup/provider calls or precompute artifacts without a separately authorized implementation/validation task. HTTP client reuse is the next low-ranking-risk candidate after profiling its contribution. Benchmark batching against singleton/client-reuse variants before choosing it; batching is not assumed faster.

## Verification strategy for a future approved change

1. Freeze exact source/policy strings and baseline rankings for all synthetic cases. Offline mocks assert cold/warm call counts, exact duplicate mapping, unchanged clause/policy IDs, stable ties and full top-three ordering. Never compare fixture scores as Gemini accuracy.
2. Test exact duplicates, same text on different pages/IDs, nonduplicates, cache invalidation on text/model/endpoint changes, failed fills, eviction, bounded memory and concurrent fills. No fuzzy normalization or global customer cache.
3. Preserve current singleton API and failure behavior. For batch candidates, validate input count/order, 1024-dimensional alignment, finite/nonzero vectors, mixed invalid entries, truncation=false, timeouts and cleanup; do not silently substitute vectors when a batch fails.
4. Under separate authorization, run embedding-only synthetic microbenchmarks for fresh process/cold policy cache and reused process/warm cache, recording daemon residency separately. Compare singleton clients, shared client, deduplication and bounded batches. Multiple repeated measurements are needed for median/p95; none were run here.
5. Capture client setup and HTTP request spans plus sanitized server timing metadata if actually supplied by the installed Ollama version. Avoid raw customer text; use synthetic input identifiers/hashes scoped to the audit. Record model revision and environment without credentials.
6. Compare actual singleton/batch/cached vectors and cosine scores within a stated numeric tolerance, then require exact ranked policy IDs/order including tie cases. If vector changes alter ranking, investigate rather than declaring an optimization equivalent. Do not change scoring thresholds to make tests pass.
7. Run the existing offline regression guard. No Gemini calls are needed to validate retrieval correctness or embedding microbenchmark speed; no customer dataset or production SQLite changes are needed.

## Offline validation and artifacts

This task executed a temporary network-blocked inspection harness against actual match_policies with mocked vectors: cold calls=13; second invocation adds six calls; policy cache hits=1/misses=1; output lists identical. It confirmed calls 8/10/12 have exactly equal inputs. Mock equality verifies control flow, not real embedding determinism or live performance.

Seven targeted existing tests passed (0 failures/errors): the retrieval/ranking/cache test, five embedding client/cosine/settings/API-contract tests and the mocked full-pipeline observability test. No live tests ran. The first helper attempt could not import sample_pdf because the test directory was missing from its import path; fixing only that temporary helper resolved it. The successful run emitted an existing Starlette/httpx deprecation warning. No production fixes were made for either diagnostic.

Evidence summary: backend/evaluation/reports/retrieval-performance-offline-audit.json. The temporary helper was removed. The previous full regression result remains 126 passed / 3 live-service tests skipped; it was not rerun for this documentation-only audit.

Files added by this task: this report and the offline audit JSON. Existing source files, traces, live reports, models, prompts and gold fixtures were only read. No Git push occurred.
