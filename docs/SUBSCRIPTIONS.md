# VERITAS AI Subscription & Plan Architecture

## 1. Overview

VERITAS AI offers two recurring subscription plans designed for enterprise legal teams and SMB contract managers:
- **Standard Plan** (INR 199/month)
- **Pro Plan** (INR 299/month)

Both plans include access to the core contract intelligence pipeline, evidence-grounded risk verification, obligation extraction, and an introductory **30-day free trial**.

---

## 2. Plan Matrix & Feature Entitlements

| Attribute / Feature | Standard Plan | Pro Plan | Enforcement Point |
|---|---|---|---|
| **Monthly Price** | INR 199 / month | INR 299 / month | Razorpay Checkout / Invoicing |
| **Introductory Trial** | 30 days (1 per account) | 30 days (1 per account) | Server-side (`trial_used` flag) |
| **Monthly Analysis Quota** | **10** analyses / month | **30** analyses / month | Server-side pre-inference check |
| **Analysis History Retention** | **5** historical records | **30** historical records | Server-side query limit (`GET /api/analysis/{id}`) |
| **Contract Analysis & Upload** | Yes | Yes | API Gateway |
| **Risk Dashboard** | Yes | Yes | API / Client View |
| **Evidence Explorer** | Yes | Yes | API / Client View |
| **Policy Comparison** | Yes | Yes | API / Client View |
| **Obligation Tracker** | Yes | Yes | API / Client View |
| **Focused Knowledge Graph** | Yes | Yes | Plan Feature Flag |
| **Category Knowledge Graph** | **No** (Pro exclusive) | **Yes** | Feature Flag (`category_knowledge_graph`) |
| **Full Network Knowledge Graph** | **No** (Pro exclusive) | **Yes** | Feature Flag (`full_network_knowledge_graph`) |
| **Priority Processing Flag** | **False** (Disabled) | **False** (Disabled) | *Explicitly disabled* (no scheduler exists) |

> **Architectural Note on Priority Processing:**
> Priority processing is hardcoded to `false` across all plans because the current backend architecture processes analysis requests synchronously per HTTP request. Claiming priority processing without a priority queue worker would be deceptive.

---

## 3. Application-Managed 30-Day Free Trial Lifecycle

### 3.1 Eligibility & Idempotency
- Every registered user account starts with `trial_used = 0`.
- Calling `POST /api/billing/trial/start` with a chosen plan (`standard` or `pro`) creates an active subscription record in the local database:
  - `status = "trialing"`
  - `trial_start = NOW()`
  - `trial_end = NOW() + 30 days`
  - `trial_used` is set to `1` on the `users` table.
- Subsequent calls to `POST /api/billing/trial/start` are rejected with HTTP 400 (`"Account has already utilized its one introductory 30-day free trial."`).

### 3.2 Trial Expiration
- Every subscription status request calculates dynamic trial validity:
  - If `NOW() > trial_end` and no active Razorpay subscription exists, the subscription status transitions to `"expired"`.
  - In the `"expired"` state, `is_active` evaluates to `false`.
  - Future calls to `POST /api/analyze` fail with HTTP 403 (`"Active subscription or trial required."`).

---

## 4. Monthly Analysis Quota Mechanics

### 4.1 Strict Server-Side Quota Enforcement
1. When a user requests contract analysis via `POST /api/analyze`, the server:
   - Verifies the user has an active trial or paid subscription (`is_active == True`).
   - Counts consumption in the current calendar billing period (`YYYY-MM`) from the `usage_records` table.
   - Compares usage against plan limits (10 for Standard, 30 for Pro).
   - If usage >= limit, rejects the request immediately with **HTTP 429 Too Many Requests**:
     ```json
     {
       "detail": {
         "state": "quota_exhausted",
         "message": "Monthly contract analysis limit reached (10/10). Upgrade to Pro or await the next monthly billing cycle.",
         "analyses_used": 10,
         "analyses_limit": 10,
         "billing_period": "2026-10"
       }
     }
     ```

### 4.2 Fair Consumption Policy (Failed Runs Never Deduct Quota)
- Quota is **checked** before calling Gemini and Ollama.
- Quota is **recorded only after** the analysis passes deterministic evidence verification, passes schema checks, and is committed to the database:
  ```python
  # In backend/app/routes/contracts.py:
  sub, billing_period = enforce_analysis_quota(current_user.id)
  result = analyze_contract(contract, user_id=current_user.id)
  record_successful_analysis_usage(current_user.id, result.analysis_id, billing_period)
  ```
- If Gemini rate-limits (HTTP 429), times out (HTTP 504), or if evidence quotes fail deterministic verification (HTTP 502), the transaction does not write to `usage_records`. The user's quota remains intact.

---

## 5. Account-Level Data Isolation

All contract assets, parsed clauses, extracted obligations, and verification analyses are isolated per user account:
- In SQLite, the `contracts`, `analyses`, and `analysis_failures` tables have an indexed `user_id` column.
- Analysis lookup queries enforce ownership:
  ```sql
  SELECT result_json FROM analyses WHERE id=? AND (user_id=? OR user_id IS NULL)
  ```
- Any attempt by User B to view, retrieve, or run analysis on User A's uploaded documents returns **HTTP 404 Not Found**.
- The public synthetic demo (`GET /api/demo/analysis`) remains globally accessible and unauthenticated without consuming account quotas.

