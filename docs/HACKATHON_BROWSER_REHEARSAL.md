# Final browser rehearsal — manual execution required

Date: 2026-10-09 (Asia/Calcutta). Branch: feature/ai-reliability.

## Verification boundary

Browser automation inventory returned no apps or browsers. **None of the 15 requested browser checks was performed. No screenshots were captured.** HTTP checks and automated tests below do not count as browser interaction or visual verification. Prior live Gemini and Razorpay smoke results are historical evidence, not new calls in this rehearsal.

Executed now: frontend build PASS; frontend lint PASS; network-blocked backend suite 144 passed, 3 live tests skipped, 0 failures/errors (147 total, 13.508 seconds); backend /health HTTP 200; frontend root HTTP 200; frontend-proxied /health HTTP 200. Existing services remain running. The Vite bundle-size warning persists; no performance redesign was attempted.

## Critical fix

An uploaded contract without a completed analysis could remain visible after logout because cleanup previously depended on the saved-analysis reference. Account changes now clear contract, analysis, error and retry state independently of session storage. Late upload/analysis responses, including persisted failures, are ignored when their initiating account is no longer current. This is a focused frontend fix; its interactive behavior still needs the manual checks below. No auth implementation or database was changed.

## Exact manual browser checks

Use Chrome or Edge at http://127.0.0.1:5173, desktop viewport 1440×900 at 100% zoom. Open DevTools Console and Network; keep credentials/tokens out of screenshots. Record PASS/FAIL and a screenshot only after actually performing each step.

| # | Action | Expected result | Actual browser status |
|---|---|---|---|
| 1 | Open the local URL and scroll through the landing page | Text/navigation/hero load; no blank error screen | NOT TESTED |
| 2 | Click Workspace, then Start Trial. Register a new synthetic demo account using your own email/password choice; activate the offered trial | Registration succeeds; Pro trial shown; credentials never hardcoded | NOT TESTED |
| 3 | Account menu → Sign Out, then Sign In with that account | Modal closes after successful login; invalid password shows understandable error | NOT TESTED |
| 4 | Open Workspace / Overview | Dashboard and backend-online indicator render; account trial/quota visible | NOT TESTED |
| 5 | Open Contract. Upload backend/evaluation/fixtures/contracts/supplier_red.pdf | Filename, three extracted pages and clauses shown; upload errors visible if rejected | NOT TESTED |
| 6 | With live call budget approved, click Analyze once; do not refresh or double-submit | Loading modal shows elapsed time and informational pipeline; no invented stage-completion claims | NOT TESTED; no new agent Gemini call authorized/executed |
| 7 | Wait for analysis response | Overview, findings and actions render from returned data; failures show error, never demo substituted as live | NOT TESTED |
| 8 | Open Risks and expand a liability/indemnity card | Severity badge and category readable; compliant findings distinguished | NOT TESTED |
| 9 | Open Evidence via a finding | Exact source quote, page/clause and applicable policy displayed; verified provenance label visible | NOT TESTED |
| 10 | Inspect a potential omission | Needs Review / Potential omission; no fake quote or page; absence/applicability require review | NOT TESTED |
| 11 | Open Action Plan | Responsible parties and explicit deadlines shown; unspecified deadline stays unspecified | NOT TESTED |
| 12 | Refresh only after successful analysis, while still logged in | Last live analysis re-fetched and restored in same tab. Extracted PDF/clauses are not restored; this is an existing API limitation | NOT TESTED |
| 13 | Sign Out after results; also test Sign Out after upload before analysis | JWT removed client-side; previous account contract/results/error cleared; Sign In available | NOT TESTED |
| 14 | Sign In again | Account/trial retrieved and workspace opens. Logout clears last-analysis reference; automatic history recovery after re-login is not provided | NOT TESTED |
| 15 | Inspect landing, modal, dashboard, Risks, Evidence and Action Plan at 1440×900 and 1280×720 | No overlapping controls or clipped essential text; tabs usable; console has no runtime exceptions | NOT TESTED |

Additional account-isolation check: sign out while upload/analysis is pending, then sign in to another synthetic account. The old response must not populate the new account's screen. Do not run an additional paid analysis just for this test without approval; use an upload to check cleanup first. Server work already submitted is not cancelled by logout. A reload/new tab can still submit another analysis: UI guard is not server-side idempotency.

## Five-minute judge workflow

Prepare and authenticate the presentation account before judging. Keep the same browser tab open after a successful approved analysis.

1. Sign In → Workspace / Overview. Show the trial/quota indicator.
2. Contract → upload supplier_red.pdf. Explain that contract and company playbook are synthetic.
3. Analyze once only when you have approved the usage cost. Show the loading state; do not refresh while processing. This rehearsal made no Gemini call.
4. Overview → Risks. Expand the liability and indemnification findings; explain response-derived severity and recommended action.
5. Evidence → show exact quote and page. Contrast with a Needs Review omission; do not call it a confirmed contractual fact.
6. Action Plan → show responsible party and deadline. Policy Comparison / Knowledge Graph are optional existing views if time permits.
7. Refresh after completion to demonstrate saved-analysis retrieval in the same authenticated tab. Avoid logout during the judge presentation because the UI does not have a saved-history picker.

## Genuine-result fallback

Use [the previously saved genuine synthetic analysis](hackathon-live-synthetic-analysis.json) if a new live analysis is unavailable. It is an exact preserved response from gemini-3.5-flash, analysis ID 314aabeb-168d-43f3-9c2c-91cc4ecc0dc3: partial status, seven findings, three verified quotations, four potential omissions and two obligations. Open the JSON in an editor or browser and show the actual findings/evidence fields. Identify it as a **previously generated synthetic Gemini result**, not a fresh analysis. No UI importer exists; do not pretend this snapshot is loaded into the app or bypass account ownership to retrieve it.

For an interactive UI backup, click Explore Demo / Load Demo Data. It is separately labeled SAMPLE ANALYSIS — DEMO DATA, hand-authored and precomputed, and must never be described as the genuine Gemini snapshot. It works with the existing offline fallback if the backend is unavailable. Keep both backup paths distinct.

## Startup and recovery

From repository root, in separate PowerShell terminals:

~~~powershell
# Only if Ollama is not already running:
ollama serve
~~~

~~~powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

~~~powershell
cd frontend
npm.cmd run dev
~~~

If login says backend unreachable, check http://127.0.0.1:8000/health and http://127.0.0.1:5173/health. Start the missing service rather than disabling authentication/CORS. If a port is occupied, use the running instance; do not start duplicates. Keep backend/.env secrets unchanged. Blank VITE_API_BASE_URL uses the development proxy. npm preview is not an API proxy replacement.

## Remaining limits and readiness

The API-backed demo was previously live-verified; build/lint/regressions and current HTTP reachability pass. **Browser rehearsal is still required before declaring the full interactive demo verified.** No desktop screenshot, click flow, refresh interaction or browser-console pass is claimed. No new Gemini/Ollama/provider/payment call occurred in this task. Payment was deliberately deferred; prior actual Razorpay Test Mode checkout initialization passed, but actual checkout payment/activation remains untested. Use the free trial for the core demonstration.

No narrative contract-summary field, downloadable PDF analysis report, saved-history picker, restored source-document view or snapshot importer exists. Do not promise these features. No backend, database, benchmark, gold, scoring, prompt/model or authentication changes; no Git push. See [the startup/demo runbook](HACKATHON_DEMO_RUNBOOK.md) for prior executed live checks and backup details.
