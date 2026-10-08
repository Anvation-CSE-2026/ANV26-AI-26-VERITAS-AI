# VERITAS AI frontend API contract

Backend contract verified October 8, 2026. Exact machine-readable schemas: [frontend-openapi.json](frontend-openapi.json), exported from the installed FastAPI application. Regenerate with `python tests/export_frontend_contract.py` after API changes. Runtime Swagger: `http://127.0.0.1:8000/docs`.

## Connection and common rules

Use the backend origin directly, normally `http://127.0.0.1:8000`. These paths include `/api`. The unchanged existing Vite proxy removes `/api`, so it is not wired to these new routes. No frontend files were changed. Local hackathon service: no authentication or user isolation; browser credentials are disabled. Existing CORS allows localhost/127.0.0.1 on port 5173. Health remains `GET /health`; embedding metadata test remains `POST /api/embeddings/test`.

Send/receive UTF-8 JSON. Uploaded filenames are display metadata, not file paths. Do not send Gemini keys to the frontend or API body. Unknown request fields are rejected. Dates are ISO 8601 UTC timestamps. Clause page numbers are 1-based; text offsets are zero-based Python Unicode character offsets within the extracted page, with an exclusive end. JavaScript UTF-16 indices can differ for non-BMP text: display the provided clause/quote text directly rather than slicing with these offsets without conversion. The API does not return embedding vectors.

## POST /api/contracts/upload

Content type: `multipart/form-data`; required part `file` is a binary PDF. Let the browser/FormData set the multipart boundary. Success: **201**, body **Contract**. Upload success means extraction and source persistence succeeded; no Gemini/Ollama call happens here.

~~~http
POST /api/contracts/upload
Content-Type: multipart/form-data; boundary=...

--...
Content-Disposition: form-data; name="file"; filename="synthetic_supplier_contract.pdf"
Content-Type: application/pdf

<PDF bytes>
--...--
~~~

Preserved data: original PDF bytes in SQLite; original PyMuPDF extracted page text; clause IDs and exact page offsets. The response includes all extracted page/clauses text, so avoid logging the entire upload response. Default caps are 10 MiB, 30 pages, 60,000 characters, and 100 clauses. Scans without text and password-protected PDFs are unsupported; mixed image/blank pages produce warnings.

Upload errors: 413 configured size/page/text/clause limit; 415 non-PDF filename; 422 invalid/encrypted/textless PDF or missing multipart file; 503 local storage failure.

## POST /api/analyze

Content type: `application/json`. Request: **AnalyzeRequest**, exactly:

~~~json
{"contract_id":"<contract_id returned by upload>"}
~~~

Synchronous request: there is no accepted/queued/running job status or polling job endpoint. Success: **200**, body **Analysis**. It runs semantic retrieval, live Gemini reasoning, deterministic evidence verification, and SQLite persistence. Use a client timeout appropriate for a synchronous demonstration; the real check used 540 seconds. Each Gemini call has a configurable 90-second timeout, at most 3 calls by default and one/two-second retry waits; Ollama calls also have their own timeouts. Provider availability can make this longer than the observed successful run.

POST failure is a non-2xx HTTP response, not a successful Analysis. For Gemini or evidence failures, inspect `detail.state=failed` and `detail.analysis_id`. When `failure_recorded=true`, GET that ID to retrieve the sanitized failed attempt. Do not display failure as an empty safe contract. No synthetic finding is substituted.

Analysis status semantics:

| Status | Meaning |
| --- | --- |
| `completed` | Pipeline completed and returned accepted records; this does not mean safe, compliant, legally approved, or complete legal analysis. |
| `partial` | Records were excluded, some evidence needs review, extraction is incomplete, or instruction alerts require review. Show warnings and rejection counts. |
| `failed` | Only in **AnalysisFailure** retrieved by GET (or `detail.state` on a POST error). No findings/obligations are supplied in failed records. |

All analyses have `requires_human_review=true`. Normal analyze output origin is `live_gemini`. The model cannot choose its own verification status, approve a contract, execute instructions, or modify the PDF.

## GET /api/analysis/{analysis_id}

No request body. Success: **200** with either **Analysis** (completed/partial) or **AnalysisFailure** (failed). Branch on `status` before reading findings/obligations. Unknown ID: **404**, `{"detail":"Analysis not found."}`. Results are persisted across backend restarts. GET does not call Gemini/Ollama.

The most recent real verified record is `d1a44317-f041-436f-a15d-319ba8722a86`, contract `dbb99d52-0df2-4072-829a-26799679e627`, in default local storage. IDs are verification examples, not hard-coded application state.

## Findings, evidence, and counts

Finding statuses: `compliant`, `risky`, `ambiguous`, `conflicting`, `missing`. Risk levels: `critical`, `high`, `medium`, `low`. Categories: liability, indemnification, termination, confidentiality, payment, data_protection, intellectual_property.

Evidence statuses:

| Status | Meaning / display behavior |
| --- | --- |
| `verified` | Backend verified the quote, source references, and applicable policy. It does not certify interpretation or legal compliance. |
| `needs_review` | Ambiguity, unreliable policy matching, assumptions, potential omission, or unclear deadline classification. A quote may exist with `evidence_verified=true` while interpretation needs review. |
| `unsupported` | Only rejected records in `verification_rejections`; excluded from accepted findings/obligations. Never present these as verified findings. |

For source-supported findings, render `source_facts` (quote/page/clause/references), `model_interpretation` (explanation/action/uncertainty/assumptions), and `applicable_policy_rule` (stored policy requirement) separately. Duplicate legacy top-level finding fields remain for compatibility. Historical saved analyses may have null nested source/interpretation fields; new live results populate them.

A `missing` finding is a **potential omission**, not confirmed absence: quote/page/clause/source_facts are null, `potential_omission=true`, `complete_document_review_required=true`, `absence_confirmed=false`, evidence status needs_review and evidence_verified false. Display the real policy requirement and uncertainty; do not invent a page or quote.

Count definitions (computed client-side from the response):

- Findings = `findings.length` (accepted findings only).
- Verified findings = count where `evidence_status === "verified"`.
- Quote-verified findings = count where `evidence_verified === true`; this can include needs_review findings.
- Unsupported findings = count of `verification_rejections` with `record_type === "finding"`.
- Obligations = `obligations.length`; rejected obligations are separate rejection entries.
- Failed analysis counts are **unknown/not produced**, not zero safe findings.

`unassessed_policy_ids` means no accepted finding addresses that rule; it does not prove absence or compliance. Similarity values in semantic_matches are measured cosine retrieval rankings, never compliance scores or legal evidence. No confidence probabilities are supplied.

Obligation deadlines are preserved verbatim. `deadline_type` is fixed_date/relative/ambiguous/unspecified; ambiguous numeric dates and unparseable calendar values need review. No deadline date arithmetic is performed. Responsible party/deadline may be null when not explicitly stated.

## Error response contracts

FastAPI keeps errors under a top-level `detail` property. Shapes are intentionally different; support a string, object, or validation-error array.

Simple string error example:

~~~json
{"detail":"Contract not found."}
~~~

Gemini error object (additional fields are always supplied by this route):

~~~json
{
  "detail": {
    "state": "failed",
    "message": "Gemini service is temporarily unavailable.",
    "synthetic_demo_command": "python tests/show_synthetic_demo.py",
    "analysis_id": "<failure ID or null>",
    "failure_recorded": true,
    "failed_stage": "gemini_reasoning",
    "error_category": "provider_transient",
    "gemini_attempts": 3,
    "upstream_http_status": 503
  }
}
~~~

Evidence failure object:

~~~json
{
  "detail": {
    "state": "failed",
    "message": "All generated records failed evidence verification; no analysis was saved.",
    "verification_rejections": [{"record_type":"finding","index":0,"reason":"quote_not_in_original_clause","evidence_status":"unsupported"}],
    "analysis_id": "<failure ID or null>",
    "failure_recorded": true,
    "failed_stage": "evidence_verification",
    "error_category": "unsupported_evidence"
  }
}
~~~

Evidence error wording refers to no successful result being saved; the separate sanitized **failure record** can be persisted. If storage fails, failure_recorded is false and analysis_id is null. Missing key/input preflight failures may also have no saved attempt. Retry count is `max(gemini_attempts - 1, 0)`.

Validation example (422):

~~~json
{"detail":[{"type":"missing","loc":["body","contract_id"],"msg":"Field required","input":{}}]}
~~~

Validation entries may include `input` and `ctx` in addition to the OpenAPI-listed loc/msg/type fields. Do not echo sensitive submitted input unnecessarily.

| HTTP code | Cause / category |
| --- | --- |
| 404 | Unknown contract on POST analyze, unknown analysis on GET. |
| 413 | PDF/extraction limits exceeded. |
| 415 | Unsupported upload filename. |
| 422 | Request validation, unsupported/invalid PDF, or protected credentials detected in source. |
| 429 | Gemini rate/quota limit after bounded retries; `Retry-After: 60`. |
| 502 | Gemini authentication/access/model/request rejection, invalid/empty/private model output, unsupported evidence, or invalid upstream embedding response. |
| 503 | Gemini transient 5xx after retries, connection or missing configuration, Ollama unavailable, or local storage/demo failure. |
| 504 | Gemini or Ollama timeout after applicable retry policy. |

Authentication upstream 401/403 maps to frontend HTTP 502 with error_category authentication and is **not retried**. Transient 429/500/502/503/504 and transport errors are bounded. Request/auth/model/schema errors are not retried. Raw SDK errors, keys, and full source text are never included in backend Gemini error messages.

Gemini failure stages include input_validation, gemini_reasoning, structured_output_validation. Orchestrator failure stages include policy_retrieval, evidence_verification, sqlite_persistence. Error categories include missing_configuration, protected_credentials, authentication, model_unavailable, rate_limit, provider_transient, request_rejected, timeout, connection, empty_output, invalid_structured_output, gemini_failure, unsupported_evidence, embedding_timeout, embedding_connection, policy_retrieval, storage. They are diagnostic strings, not finding categories.

## Graph data structures

**No graph layer is implemented.** No `graph`, `nodes`, `edges`, or `graph_edges` fields are returned or accepted. Gemini-generated graph fields are rejected. The frontend must not assume a graph response or invent entities/edges. Existing documented relationships are PolicyMatch(clause_id, policy_id, similarity), findings linking real clause IDs to real policy IDs, and obligations referencing real clauses. These are source relationships, not a separate graph API schema. A future graph contract requires a separately implemented schema and deterministic endpoint-entity validation.

## Explicit offline demo endpoint

`GET /api/demo/analysis` returns **200 DemoArtifact**. It does not call Gemini/Ollama or use SQLite. Payload contains a fixed synthetic contract, synthetic playbook, and precomputed hand-authored analysis. Every read independently rechecks the saved finding/obligation evidence. Invalid/tampered snapshot: **503** string detail. No fallback from normal analyze occurs. Normal analyze rejects extra mode/demo flags.

Always display `label = "SAMPLE ANALYSIS — DEMO DATA"`, `output_origin=synthetic_demo`, `live_ai_used=false`. Demo analysis has gemini_model and embedding_model `not_used`, zero Gemini attempts, and no semantic_matches; do not claim these came from live AI. It has fixed synthetic IDs, seven findings, and three obligations. Demo IDs are only available through the demo endpoint, not the SQLite GET analysis route.

## Exact schema field tables

Required means it is listed in the exported OpenAPI required array. Defaulted fields are still returned by the backend because response defaults are serialized. All record schemas forbid unexpected properties. Arrays can be empty; nullable fields are represented as null, not invented values. The schema artifact is authoritative for machine integration.

### AnalyzeRequest

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `contract_id` | string | yes | minLength=1; maxLength=100 |

### Contract

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `contract_id` | string | yes |  |
| `filename` | string | yes |  |
| `pages` | array<PageText> | yes |  |
| `clauses` | array<Clause> | yes |  |
| `warnings` | array<string> | yes |  |

### PageText

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `page_number` | integer | yes | minimum=1 |
| `text` | string | yes |  |

### Clause

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `clause_id` | string | yes |  |
| `page_number` | integer | yes | minimum=1 |
| `text` | string | yes |  |
| `start_offset` | integer | yes | minimum=0 |
| `end_offset` | integer | yes | minimum=1 |

### Analysis

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `gemini_attempts` | integer | no | minimum=0; default 0 |
| `gemini_response_model` | string \| null | no |  |
| `processing_seconds` | number | no | minimum=0; default 0 |
| `output_origin` | "live_gemini" \| "synthetic_demo" | no | default "live_gemini" |
| `requires_human_review` | boolean | no | default true |
| `document_instruction_alerts` | array<InstructionAlert> | no |  |
| `analysis_id` | string | yes |  |
| `contract_id` | string | yes |  |
| `created_at` | string (date-time) | yes |  |
| `status` | "completed" \| "partial" | yes |  |
| `gemini_model` | string | yes |  |
| `embedding_model` | string | yes |  |
| `playbook_id` | string | yes |  |
| `playbook_version` | string | yes |  |
| `findings` | array<VerifiedFinding> | yes |  |
| `obligations` | array<VerifiedObligation> | yes |  |
| `semantic_matches` | array<PolicyMatch> | yes |  |
| `unassessed_policy_ids` | array<string> | yes |  |
| `verification_rejections` | array<RejectedRecord> | yes |  |
| `warnings` | array<string> | yes |  |

### VerifiedFinding

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `finding_status` | "compliant" \| "risky" \| "ambiguous" \| "conflicting" \| "missing" | no | default "risky" |
| `policy_requirement` | string \| null | no |  |
| `referenced_parties` | array<string> | no | maxItems=20 |
| `referenced_dates` | array<string> | no | maxItems=20 |
| `policy_match_reliable` | boolean | no | default true |
| `uncertainty` | string \| null | no |  |
| `unsupported_assumptions` | array<string> | no | maxItems=20 |
| `risk_level` | "low" \| "medium" \| "high" \| "critical" | yes |  |
| `clause_category` | "liability" \| "indemnification" \| "termination" \| "confidentiality" \| "payment" \| "data_protection" \| "intellectual_property" | yes |  |
| `explanation` | string | yes | minLength=1; maxLength=2000 |
| `evidence_quote` | string \| null | no |  |
| `page_number` | integer \| null | no |  |
| `clause_id` | string \| null | no |  |
| `policy_id` | string | yes |  |
| `recommended_action` | string | yes | minLength=1; maxLength=2000 |
| `applicable_policy_rule` | PolicyRule | yes |  |
| `evidence_verified` | boolean | no | default true |
| `evidence_status` | "verified" \| "unsupported" \| "needs_review" | no | default "verified" |
| `source_facts` | SourceFacts \| null | no |  |
| `model_interpretation` | ModelInterpretation \| null | no |  |
| `potential_omission` | boolean | no | default false |
| `complete_document_review_required` | boolean | no | default false |
| `absence_confirmed` | boolean | no | default false |

### SourceFacts

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `clause_id` | string | yes |  |
| `page_number` | integer | yes |  |
| `evidence_quote` | string | yes |  |
| `referenced_parties` | array<string> | yes |  |
| `referenced_dates` | array<string> | yes |  |

### ModelInterpretation

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `finding_status` | "compliant" \| "risky" \| "ambiguous" \| "conflicting" \| "missing" | yes |  |
| `explanation` | string | yes |  |
| `recommended_action` | string | yes |  |
| `uncertainty` | string \| null | yes |  |
| `unsupported_assumptions` | array<string> | yes |  |

### PolicyRule

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `policy_id` | string | yes |  |
| `category` | "liability" \| "indemnification" \| "termination" \| "confidentiality" \| "payment" \| "data_protection" \| "intellectual_property" | yes |  |
| `rule` | string | yes |  |
| `recommended_action` | string | yes |  |

### VerifiedObligation

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `description` | string | yes | minLength=1; maxLength=2000 |
| `evidence_quote` | string | yes | minLength=1; maxLength=2000 |
| `page_number` | integer | yes | minimum=1 |
| `clause_id` | string | yes |  |
| `responsible_party` | string \| null | yes |  |
| `deadline` | string \| null | yes |  |
| `evidence_verified` | boolean | no | default true |
| `evidence_status` | "verified" \| "unsupported" \| "needs_review" | no | default "verified" |
| `deadline_type` | "fixed_date" \| "relative" \| "ambiguous" \| "unspecified" | no | default "unspecified" |

### PolicyMatch

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `clause_id` | string | yes |  |
| `policy_id` | string | yes |  |
| `similarity` | number | yes | minimum=-1; maximum=1 |

### RejectedRecord

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `record_type` | "finding" \| "obligation" | yes |  |
| `index` | integer | yes |  |
| `reason` | string | yes |  |
| `evidence_status` | string | no | default "unsupported" |

### InstructionAlert

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `source_type` | "clause" \| "policy" | yes |  |
| `source_id` | string | yes |  |
| `reason` | string | yes |  |

### AnalysisFailure

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `analysis_id` | string | yes |  |
| `contract_id` | string | yes |  |
| `created_at` | string (date-time) | yes |  |
| `status` | string | no | default "failed" |
| `output_origin` | string | no | default "live_gemini" |
| `failed_stage` | string | yes |  |
| `error_category` | string | yes |  |
| `message` | string | yes |  |
| `http_status` | integer | yes |  |
| `upstream_http_status` | integer \| null | no |  |
| `gemini_model` | string | yes |  |
| `gemini_attempts` | integer | yes | minimum=0 |
| `retries_occurred` | boolean | yes |  |
| `processing_seconds` | number | yes | minimum=0 |
| `verification_rejections` | array<RejectedRecord> | no |  |

### DemoArtifact

| Field | Type | Required | Constraints / default |
| --- | --- | --- | --- |
| `label` | string | yes |  |
| `output_origin` | string | yes |  |
| `live_ai_used` | boolean | yes |  |
| `description` | string | yes |  |
| `contract` | Contract | yes |  |
| `playbook` | Playbook | yes |  |
| `analysis` | Analysis | yes |  |

Legacy records can have default zero gemini_attempts/processing_seconds, meaning metrics were not recorded. New live results record actual attempt count and analysis elapsed time; processing_seconds excludes upload/retrieval/restart validation and is measured before final SQLite commit. The E2E report total_processing_seconds includes the complete verification run from upload through retrieval, restart validation, and cleanup.
