# VERITAS AI Billing & Auth API Contract

Complete API contract for Authentication, Subscriptions, Razorpay Test Mode integration, and Webhooks.

---

## 1. Authentication Endpoints

### 1.1 Register User
- **Method & Path:** `POST /api/auth/register`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }
  ```
- **Responses:**
  - `201 Created`:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "user": {
        "id": "usr_9b1deb4d3b7d4fb7",
        "email": "user@example.com",
        "trial_used": false,
        "created_at": "2026-10-08T11:00:00Z"
      }
    }
    ```
  - `409 Conflict`: `{"detail": "An account with this email address already exists."}`
  - `422 Unprocessable Entity`: Password must be at least 8 characters.

---

### 1.2 Login User
- **Method & Path:** `POST /api/auth/login`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }
  ```
- **Responses:**
  - `200 OK`: Same as register response.
  - `401 Unauthorized`: `{"detail": "Invalid email or password."}`

---

### 1.3 Current User Info
- **Method & Path:** `GET /api/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Responses:**
  - `200 OK`: Returns user profile.
  - `401 Unauthorized`: Missing or invalid JWT token.

---

### 1.4 Logout User
- **Method & Path:** `POST /api/auth/logout`
- **Headers:** `Authorization: Bearer <token>`
- **Responses:**
  - `200 OK`: `{"success": true, "message": "Successfully logged out."}`

---

## 2. Subscription & Billing Endpoints

### 2.1 List Available Plans
- **Method & Path:** `GET /api/billing/plans`
- **Auth Required:** No
- **Responses:**
  - `200 OK`:
    ```json
    {
      "plans": [
        {
          "tier": "standard",
          "name": "Standard Plan",
          "price_inr": 199,
          "interval": "monthly",
          "trial_days": 30,
          "monthly_analyses_limit": 10,
          "analysis_history_limit": 5,
          "features": {
            "contract_analysis": true,
            "risk_dashboard": true,
            "evidence_explorer": true,
            "policy_comparison": true,
            "obligation_tracker": true,
            "focused_knowledge_graph": true,
            "category_knowledge_graph": false,
            "full_network_knowledge_graph": false,
            "priority_processing": false
          },
          "razorpay_plan_id": "plan_standard_monthly_inr199"
        },
        {
          "tier": "pro",
          "name": "Pro Plan",
          "price_inr": 299,
          "interval": "monthly",
          "trial_days": 30,
          "monthly_analyses_limit": 30,
          "analysis_history_limit": 30,
          "features": {
            "contract_analysis": true,
            "risk_dashboard": true,
            "evidence_explorer": true,
            "policy_comparison": true,
            "obligation_tracker": true,
            "focused_knowledge_graph": true,
            "category_knowledge_graph": true,
            "full_network_knowledge_graph": true,
            "priority_processing": false
          },
          "razorpay_plan_id": "plan_pro_monthly_inr299"
        }
      ]
    }
    ```

---

### 2.2 Start 30-Day Free Trial
- **Method & Path:** `POST /api/billing/trial/start`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "plan": "pro"
  }
  ```
- **Responses:**
  - `201 Created`:
    ```json
    {
      "id": "sub_841753909efd4ba2",
      "user_id": "usr_9b1deb4d3b7d4fb7",
      "plan": "pro",
      "status": "trialing",
      "trial_start": "2026-10-08T11:00:00Z",
      "trial_end": "2026-11-07T11:00:00Z",
      "current_period_start": null,
      "current_period_end": null,
      "razorpay_subscription_id": null,
      "analyses_used": 0,
      "analyses_limit": 30,
      "analyses_remaining": 30,
      "history_limit": 30,
      "features": { ... },
      "is_active": true,
      "created_at": "2026-10-08T11:00:00Z",
      "updated_at": "2026-10-08T11:00:00Z"
    }
    ```
  - `400 Bad Request`: `{"detail": "Account has already utilized its one introductory 30-day free trial."}`

---

### 2.3 Get Current Subscription Status
- **Method & Path:** `GET /api/billing/subscription`
- **Headers:** `Authorization: Bearer <token>`
- **Responses:**
  - `200 OK`: Returns current `SubscriptionResponse` (same as 2.2).

---

### 2.4 Create Checkout for Paid Subscription
- **Method & Path:** `POST /api/billing/checkout`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "plan": "pro"
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "subscription_id": "sub_N3x0...",
      "razorpay_key_id": "rzp_test_...",
      "plan": "pro",
      "amount_paise": 29900,
      "currency": "INR",
      "name": "VERITAS AI",
      "description": "VERITAS AI Pro Plan Subscription"
    }
    ```
  - `503 Service Unavailable`: Razorpay credentials or Plan ID unconfigured.

---

### 2.5 Verify Checkout Payment
- **Method & Path:** `POST /api/billing/verify`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "razorpay_payment_id": "pay_O4y1...",
    "razorpay_subscription_id": "sub_N3x0...",
    "razorpay_signature": "hmac_signature_hex"
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "success": true,
      "status": "active",
      "message": "Payment verified and subscription activated.",
      "subscription": { ... }
    }
    ```
  - `400 Bad Request`: `{"detail": "Payment verification failed: invalid signature."}`

---

### 2.6 Cancel Subscription
- **Method & Path:** `POST /api/billing/cancel`
- **Headers:** `Authorization: Bearer <token>`
- **Responses:**
  - `200 OK`:
    ```json
    {
      "success": true,
      "message": "Subscription has been cancelled.",
      "subscription": { ... }
    }
    ```

---

## 3. Webhook Endpoint

### 3.1 Razorpay Webhook Receiver
- **Method & Path:** `POST /api/webhooks/razorpay`
- **Headers:** `X-Razorpay-Signature: <hmac_hex>`
- **Request Body:** Raw Razorpay webhook JSON.
- **Responses:**
  - `200 OK`: `{"status": "processed", "event": "subscription.charged", "provider_event_id": "evt_..."}`
  - `200 OK` (Duplicate): `{"status": "ignored", "message": "Event already processed (idempotent duplicate).", "provider_event_id": "evt_..."}`
  - `400 Bad Request`: `{"detail": "Invalid webhook signature."}` or `{"detail": "Missing X-Razorpay-Signature header."}`

