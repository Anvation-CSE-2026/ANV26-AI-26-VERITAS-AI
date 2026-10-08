# Repeatable five-minute VERITAS AI demonstration

Run from the workspace root. No frontend changes are required.

## Before the five-minute presentation

1. Keep the precomputed snapshot at backend/app/resources/demo_analysis.json. It is already built and independently verified: seven findings, three obligations. Do not rebuild on stage. The synthetic contract is tests/fixtures/synthetic_supplier_contract.pdf and the synthetic company playbook is embedded in the snapshot and available at backend/app/resources/sample_playbook.json.
2. Start the backend (works even if Gemini/Ollama are down):

~~~powershell
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
~~~

3. In another terminal run the offline summary:

~~~powershell
.\backend\.venv\Scripts\python.exe tests/show_synthetic_demo.py
~~~

4. Optional preflight for fresh live generation: start Ollama, configure backend/.env, then run:

~~~powershell
.\backend\.venv\Scripts\python.exe tests/verify_ai_http.py --model gemini-3.5-flash --keep-storage --report docs/live-e2e-result.json --apply-model-on-success
~~~

This sends only the synthetic contract/playbook to real providers. It leaves a retrievable SQLite record and updates model settings only after full generation, evidence checks, saved result retrieval, and restart verification succeed. Run it before the timed presentation. Never print the API key or dump the entire upload response.

## Minute 0–1: explain the boundaries and show readiness

Say: “This is an evidence-grounded review assistant, not a contract approver. Today’s inputs are synthetic. We distinguish actual live model results from offline demo data.” Show GET /health in Swagger or run:

~~~powershell
Invoke-RestMethod http://127.0.0.1:8000/health
$demo = Invoke-RestMethod http://127.0.0.1:8000/api/demo/analysis
$demo | Select-Object label, output_origin, live_ai_used
~~~

Always display **SAMPLE ANALYSIS — DEMO DATA**. Offline demo is hand-authored/precomputed; never describe it as a live Gemini result.

## Minute 1–2: show synthetic source traceability

Show the two-page synthetic PDF and the seven-category synthetic policy. Explain original page text and clause offsets are preserved; quotation verification does not validate legal interpretation. Show one finding only:

~~~powershell
$demo.analysis.findings[0] | Select-Object finding_status, risk_level, evidence_status, clause_id, page_number, evidence_quote
$demo.analysis.findings[0].applicable_policy_rule | Select-Object policy_id, rule
~~~

This is a necessary single evidence quote, not a console dump of the complete document.

## Minute 2–3: show verified risks and explicit obligations

Show that this snapshot has seven verified findings and three obligations; expose uncertainty and review flags rather than treating similarity as compliance. Show the reporting obligation:

~~~powershell
$demo.analysis | Select-Object status, output_origin, requires_human_review
$demo.analysis.obligations[-1] | Select-Object responsible_party, deadline, deadline_type, clause_id, page_number, evidence_status
~~~

Point out the relative deadline stays “by the fifth day of each month”; no invented calendar date is computed.

## Minute 3–4: show actual saved live evidence if available

The successful live verification stored contract dbb99d52-0df2-4072-829a-26799679e627 and analysis d1a44317-f041-436f-a15d-319ba8722a86 in default SQLite. Retrieve without calling providers:

~~~powershell
$live = Invoke-RestMethod http://127.0.0.1:8000/api/analysis/d1a44317-f041-436f-a15d-319ba8722a86
$live | Select-Object analysis_id, status, output_origin, gemini_model, gemini_response_model, gemini_attempts
[pscustomobject]@{ Findings = $live.findings.Count; Verified = @($live.findings | Where-Object evidence_status -eq verified).Count; Obligations = $live.obligations.Count }
~~~

Say this is a **previously generated live result**, not a fresh on-stage model call. It has seven verified findings and five obligations. If the local DB was moved/deleted or a new STORAGE_PATH is used, skip this step and explicitly stay in the labeled synthetic demo. A future run gets new IDs; use docs/live-e2e-result.json rather than hard-coding them in product UI.

## Minute 4–5: show failure honesty and persistence

Explain 429/transient errors retry up to three times by default, authentication errors are not retried, and failed attempts are separately recorded with status failed and no AI findings. Show the API contract documentation and measured live summary at docs/live-e2e-result.json. GET retrieves persisted records after a restart without Gemini/Ollama.

If Gemini is unavailable, say: “Live generation is unavailable. We are now explicitly showing SAMPLE ANALYSIS — DEMO DATA.” Use the offline endpoint or CLI, never silently replace an API error with the snapshot. Do not deliberately break credentials or spend stage time waiting through retries.

## Offline-only fallback

If even the backend cannot be started, the precomputed JSON file and CLI remain available:

~~~powershell
.\backend\.venv\Scripts\python.exe tests/show_synthetic_demo.py
~~~

Add --full only when intentionally displaying selected demo evidence, not for unnecessary complete-document logging. No network or keys are needed for snapshot verification/display. It contains synthetic inputs only.
