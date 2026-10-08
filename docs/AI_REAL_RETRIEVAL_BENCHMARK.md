# Real Ollama retrieval benchmark

## Result

Measured the unchanged original retrieval loop against production request-local deduplication using SYN-supplier_red and the same synthetic company playbook. This benchmark made real local Ollama embedding requests, **no Gemini calls**, no authentication/billing calls and no database writes.

| Condition | Original median seconds | Optimized median seconds | Median difference seconds | Improvement | Embedding call reduction |
|---|---:|---:|---:|---:|---|
| cold policy cache | 28.066308 | 23.812411 | 4.253897 | 15.16% | 13 → 11 (15.38%) |
| warm policy cache | 12.889586 | 8.696566 | 4.193020 | 32.53% | 6 → 4 (33.33%) |

All 12 measured runs produced the same 18 results in exactly the same clause/policy order. Maximum absolute similarity-score difference: **0.0**, within tolerance 1e-6. All six original clause entries, including the three identical-text headers on separate pages, remained present. This verifies retrieval equivalence for this fixture/model/environment; it does not measure Gemini risk-analysis accuracy.

## Environment and preflight

- Started UTC: 2026-10-08T17:12:48.316426+00:00.
- Host: Windows-11-10.0.26200-SP0; Python 3.14.7; httpx 0.28.1.
- Ollama: 0.40.1, reachable at http://localhost:11434.
- Installed model: qwen3-embedding:0.6b; digest ac6da0dfba84a81fdbfbaf330198c33cd77c4cdfc53e8bc50eb581914a15621d.
- Actual preflight embedding dimensions: 1024.
- Embedding configuration: /api/embed, single text input, truncate=false, trust_env=false; connect timeout 5 s and read timeout 120 s. No model/prompt or runtime options were changed.
- Contract: SYN-supplier_red, 3 pages/6 clauses, from hash-validated synthetic_v1 fixtures. Contract-input SHA-256: 9e59abf24a3780a94161554ac415a0a6d582f8badff9b7519dfcceaba379098a.
- Policy: sample-company-policy v1.0, 7 rules; policy SHA-256: 55469357fe63f51cb85b6107480eb2c73ba6046430699ebc3b71a801ed9a3ca5.
- Ranking: unchanged cosine implementation, stable descending sort, top 3 per clause; no similarity threshold.
- /api/ps reported the selected model resident before and after every measured variant; reported size_vram was 2370652077 bytes. This is provider-reported residency metadata, not an independent GPU utilization or memory measurement. CPU/GPU utilization and host load were not recorded.

The harness imports only configuration, fixture/extraction models, retrieval, embeddings, playbook and observer utilities; it does not invoke the contract analysis service, Gemini SDK, application authentication or billing services. Its synchronous HTTP guard permits only http://localhost:11434 or the equivalent 127.0.0.1 endpoints /api/version, /api/tags, /api/ps and /api/embed. No customer contracts were involved.

Production SQLite and its WAL/SHM existence/hash snapshot matched before/after. The harness never opened a SQLite connection. No production source, frontend, prompts/models, evidence rules or gold labels were modified. No database reset or Git push occurred.

## Methodology and reproducibility

Executed once from backend:

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.real_retrieval_benchmark --live-ollama
~~~

The explicit --live-ollama flag prevents accidental live execution. The script permits only the selected locally installed model and synthetic fixture. A failed/unavailable preflight stops without fabricating results.

The original function is a separate reference copy of the pre-change loop in the benchmark harness: it embeds every clause and uses the same production policy cache, client, cosine function, stable sort and top-three selection. The optimized variant calls the existing production match_policies function. Neither production implementation nor configuration was altered to create the comparison. The same observer timing wrapper applies to both variants, and all requests use the actual production embedding client.

One preflight embedding confirmed dimensions and warmed the local model. Each variant then completed one full cold-policy-cache warm-up, excluded from medians: original 27.994850 s / 13 calls; optimized 23.857009 s / 11 calls.

There were three measured iterations per variant **for each of two policy-cache states**, 12 total measured retrievals. Within each state the pair order was original/optimized, optimized/original, original/optimized. Alternating order reduces bias, but with an odd number of pairs it is not perfectly balanced. Cold-cache runs completed before warm-cache runs; this ordering is a limitation for comparing states, though each state has an internal before/after comparison.

- **Cold policy cache:** clear the existing policy-vector LRU before each timed retrieval. The model itself is already warm/resident. Original makes seven policy plus six clause requests; optimized makes seven policy plus four unique-clause requests.
- **Warm policy cache:** clear and prefill the same seven policy vectors before each variant, outside the timed interval; reset the request timing/count offset. Original then makes six clause requests; optimized makes four. Prefill calls are recorded separately, not silently counted as free preparation.
- The clause deduplication map is new for every optimized invocation. No customer-vector cross-request cache is used.
- Total retrieval time is measured with perf_counter around the complete function. Per-request embedding spans include client creation, transport, validation and teardown. The benchmark's extra duration-metadata extraction is inside each embedding request for both variants; it may add small symmetric instrumentation overhead.
- /api/ps snapshots occur outside timed retrieval. No model unload, keep_alive override, batching, HTTP pooling change or retries were introduced.

Measured embedding requests: **102**. Additional excluded calls: 24 initial variant warm-up requests, 42 policy-cache preparation requests for six warm variants and one preflight request. Total local embedding requests in this controlled invocation: **169**. Version/tag/residency GETs are separate and outside timing. No Gemini request was made.

## Raw retrieval measurements

Run numbers below are actual execution order. The preparation column reports embeddings outside the timed interval.

| Run | Policy cache | Iteration | Variant | Retrieval seconds | Timed embedding requests | Excluded preparation requests |
|---:|---|---:|---|---:|---:|---:|
| 1 | cold | 1 | original | 28.066308 | 13 | 0 |
| 2 | cold | 1 | optimized | 23.797033 | 11 | 0 |
| 3 | cold | 2 | optimized | 23.924766 | 11 | 0 |
| 4 | cold | 2 | original | 28.256461 | 13 | 0 |
| 5 | cold | 3 | original | 28.038049 | 13 | 0 |
| 6 | cold | 3 | optimized | 23.812411 | 11 | 0 |
| 7 | warm | 1 | original | 12.889586 | 6 | 7 |
| 8 | warm | 1 | optimized | 8.697031 | 4 | 7 |
| 9 | warm | 2 | optimized | 8.643574 | 4 | 7 |
| 10 | warm | 2 | original | 12.871934 | 6 | 7 |
| 11 | warm | 3 | original | 12.902867 | 6 | 7 |
| 12 | warm | 3 | optimized | 8.696566 | 4 | 7 |

### Raw per-request embedding latencies

Each comma-separated sequence is in actual request order; units are seconds.

| Run | Embedding request durations |
|---:|---|
| 1 | 2.146734, 2.153244, 2.128985, 2.134167, 2.124685, 2.249676, 2.139712, 2.199314, 2.105150, 2.121862, 2.191411, 2.106378, 2.249787 |
| 2 | 2.065418, 2.255701, 2.143898, 2.250900, 2.157763, 2.243868, 2.097289, 2.204964, 2.117670, 2.105252, 2.139678 |
| 3 | 2.249128, 2.141382, 2.168542, 2.138730, 2.193755, 2.132807, 2.229463, 2.082571, 2.224943, 2.211913, 2.135994 |
| 4 | 2.265088, 2.097074, 2.271465, 2.155344, 2.093827, 2.223030, 2.141371, 2.184169, 2.110244, 2.152241, 2.185505, 2.119367, 2.242297 |
| 5 | 2.129878, 2.128385, 2.151416, 2.251392, 2.149666, 2.247169, 2.089721, 2.190867, 2.130044, 2.090813, 2.120734, 2.099554, 2.243297 |
| 6 | 2.132134, 2.250815, 2.132296, 2.232698, 2.157598, 2.140481, 2.266264, 2.098595, 2.145364, 2.114560, 2.127867 |
| 7 | 2.136670, 2.234662, 2.108589, 2.151066, 2.110175, 2.133347 |
| 8 | 2.128457, 2.183340, 2.186525, 2.184041 |
| 9 | 2.127939, 2.197319, 2.129635, 2.173326 |
| 10 | 2.108301, 2.186494, 2.105594, 2.221682, 2.101264, 2.131635 |
| 11 | 2.117484, 2.162909, 2.164837, 2.193936, 2.061681, 2.187775 |
| 12 | 2.139404, 2.187864, 2.199021, 2.155746 |

For cold runs the first seven entries follow playbook order: liability, indemnification, termination, confidentiality, payment, data protection and IP. The remaining entries follow clause order. Original clause requests: P001-C001, P001-C002, P002-C001, P002-C002, P003-C001, P003-C002. Optimized unique requests: P001-C001, P001-C002, P002-C002, P003-C002. Warm runs contain only those clause sequences. P002-C001/P003-C001 reuse the first header vector but still receive their own matches.

Complete raw timing samples, exact score values, request HTTP statuses, provider metadata, residency snapshots and warm-ups are in backend/evaluation/reports/real-retrieval-benchmark.json. No source contract text is stored in this report artifact.

## Model-load behavior and observed overhead

Across all 102 measured embedding requests:

| Measurement | Seconds |
|---|---:|
| Mean embedding span wall time | 2.160942 |
| Median embedding span wall time | 2.146049 |
| Mean provider total_duration | 0.123528 |
| Provider total_duration range | 0.031583–0.229492 |
| Mean provider load_duration | 0.009812 |
| Provider load_duration range | 0.008280–0.013957 |

Ollama supplied total_duration and load_duration as integer nanosecond fields, converted here to seconds according to its [official embedding endpoint documentation](https://docs.ollama.com/api/embed). Raw provider values are retained unchanged in JSON. prompt_eval_count was also captured when supplied; it is an input-token count, not a billing estimate.

The model was reported resident throughout, and no large load-duration spikes appeared in these measured requests. This supports warm-model measurements, not a claim that internal setup/loading work is absent. True unloaded-model startup was not benchmarked.

Mean wall time exceeds mean provider total_duration by 2.037414 seconds per request. **Inference:** substantial elapsed time lies outside the provider's reported generation interval. The production client opens/closes a fresh HTTP client per call, making client setup/transport a strong next target. This difference is not a direct measurement of any one component: socket connection, localhost address resolution/IPv6 fallback, teardown, validation, scheduling or unreported server work were not separately instrumented. Do not attribute the entire gap to HTTP client construction or model compute without further profiling.

## Retrieval correctness

| Check | Result |
|---|---|
| Clause IDs | Identical in all measured variants/iterations |
| Duplicate clause entries | All six retained; three header clauses have their original IDs |
| Result count | 18 in every run |
| Result order | Identical clause-major order and policy rank order |
| Top-k policy IDs | Identical top three for every clause |
| Similarity scores | Maximum absolute difference 0.0 across all 12 runs |
| Comparison tolerance | 1e-6 absolute; not used to hide ordering differences |
| Differences recorded | None |

The representative outputs below are rounded for readability; unrounded values are in JSON and were used for equivalence checks.

| Clause ID | Ranked policy ID (in order) | Cosine similarity |
|---|---|---:|
| P001-C001 | POL-IP-001 | 0.523282980366 |
| P001-C001 | POL-LIAB-001 | 0.486595920221 |
| P001-C001 | POL-INDEM-001 | 0.459017468071 |
| P001-C002 | POL-LIAB-001 | 0.769574147480 |
| P001-C002 | POL-INDEM-001 | 0.511155355096 |
| P001-C002 | POL-DATA-001 | 0.508149207820 |
| P002-C001 | POL-IP-001 | 0.523282980366 |
| P002-C001 | POL-LIAB-001 | 0.486595920221 |
| P002-C001 | POL-INDEM-001 | 0.459017468071 |
| P002-C002 | POL-INDEM-001 | 0.793103881859 |
| P002-C002 | POL-IP-001 | 0.525495548425 |
| P002-C002 | POL-LIAB-001 | 0.513450599437 |
| P003-C001 | POL-IP-001 | 0.523282980366 |
| P003-C001 | POL-LIAB-001 | 0.486595920221 |
| P003-C001 | POL-INDEM-001 | 0.459017468071 |
| P003-C002 | POL-PAY-001 | 0.921870846739 |
| P003-C002 | POL-TERM-001 | 0.441100685104 |
| P003-C002 | POL-INDEM-001 | 0.373024428381 |

These retrieval scores are semantic similarities, not legal correctness or risk probabilities. Gemini and deterministic evidence verification were not invoked; their code/settings remained unchanged.

## Limitations

- One synthetic contract, one playbook, one local model/environment, three measured samples per variant/cache state. Medians are descriptive; no confidence interval, broad workload claim or p95 estimate is justified.
- The model was already warmed by preflight; cold means Python policy-cache cold, not Ollama model cold. Warm-cache preparation has a real cost excluded by design and listed explicitly.
- Background host load was uncontrolled. Cold versus warm groups were not interleaved, and three pairs cannot perfectly balance order. Local machine timings may differ elsewhere.
- Provider duration fields and residency are self-reported; no independent CPU/GPU/server profiler was used. Client/transport overhead remains an inference, not a resolved cause.
- Score equality here does not establish universal determinism across models, hardware, weights or future runtime settings. The recorded model digest and input/policy hashes identify this comparison.
- The benchmark saves aggregate/raw diagnostics incrementally and stops on errors; it does not silently retry a failed comparison or substitute results. No service failure occurred in this invocation.
- The prior 134-pass/3-live-skip regression record remains unchanged; this measurement task made no production code changes and did not rerun the full suite.

## Recommended next optimization

Investigate **HTTP connection/client reuse within one retrieval operation** next. Use separately approved synthetic embedding-only profiling to split client creation, name resolution/connect, request/server duration and teardown; explicitly test localhost connection behavior while preserving the model and payload. The roughly 2.037-second wall/provider gap suggests a larger opportunity than optimizing the small cosine/ranking loop.

After identifying the dominant component, compare a bounded shared-client implementation against current singleton clients with the same input/configuration, exact top-k/order checks and documented score tolerance. Preserve trust_env=false, timeouts and error semantics. Keep batching a separate measured candidate rather than assuming it is faster. No Gemini calls are needed for either investigation.

## Files created by this task

- backend/evaluation/real_retrieval_benchmark.py: explicit Ollama-only, synthetic comparison harness.
- backend/evaluation/reports/real-retrieval-benchmark.json: real measurements and correctness results.
- docs/AI_REAL_RETRIEVAL_BENCHMARK.md: this report.

No production implementation changes or Git push.
