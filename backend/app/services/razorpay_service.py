"""Razorpay Test Mode subscription integration:
checkout creation, HMAC signature verification, webhook handling, and idempotency.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException, status
import razorpay

from app.config import settings
from app.models.auth import UserRecord
from app.models.billing import (
    PLAN_CONFIGS,
    CheckoutResponse,
    PlanTier,
    SubscriptionResponse,
    SubscriptionStatus,
)
from app.services.billing import get_user_subscription
from app.services.storage import (
    get_payment_event,
    get_latest_subscription_by_user_id,
    get_subscription_by_razorpay_id,
    record_payment_event,
    save_subscription,
    update_subscription,
)


def get_razorpay_client() -> razorpay.Client:
    """Returns authenticated Razorpay client in Test/Live mode."""
    if not settings.razorpay_key_id.strip() or not settings.razorpay_key_secret.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay API credentials are not configured on the backend.",
        )
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


def get_plan_id_for_tier(plan_tier: PlanTier) -> str:
    """Returns Razorpay plan ID configured in settings for selected plan tier."""
    if plan_tier == PlanTier.STANDARD:
        plan_id = settings.razorpay_standard_plan_id.strip()
    else:
        plan_id = settings.razorpay_pro_plan_id.strip()

    # Normalize common OCR/character confusion typos (e.g. T1 -> Tl, 108 -> 1O8)
    if plan_id.startswith("plan_T1Q"):
        plan_id = "plan_TlQ" + plan_id[8:]
    if plan_tier == PlanTier.STANDARD and "108" in plan_id:
        plan_id = plan_id.replace("108", "1O8")

    if not plan_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Razorpay plan ID for '{plan_tier.value}' is not configured (check RAZORPAY_{plan_tier.value.upper()}_PLAN_ID).",
        )
    return plan_id


def create_subscription_checkout(user: UserRecord, plan_tier: PlanTier) -> CheckoutResponse:
    """Creates a recurring subscription on Razorpay in Test Mode and returns checkout parameters."""
    client = get_razorpay_client()
    plan_id = get_plan_id_for_tier(plan_tier)
    plan_cfg = PLAN_CONFIGS[plan_tier.value]

    try:
        sub = client.subscription.create({
            "plan_id": plan_id,
            "total_count": 12,  # 12 monthly billing cycles
            "quantity": 1,
            "customer_notify": 1,
            "notes": {
                "user_id": user.id,
                "email": user.email,
                "plan": plan_tier.value,
            },
        })
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create subscription on Razorpay: {str(exc)}",
        ) from None

    rzp_sub_id = sub["id"]
    now = datetime.now(timezone.utc).isoformat()

    # Prevent duplicate active subscriptions
    existing_sub = get_latest_subscription_by_user_id(user.id)
    if existing_sub and existing_sub["status"] == SubscriptionStatus.ACTIVE.value and existing_sub["plan"] == plan_tier.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account already has an active {plan_tier.value.upper()} subscription.",
        )

    # Link new Razorpay subscription as pending_payment (never mutate existing plan until verified)
    save_subscription({
        "id": str(uuid4()),
        "user_id": user.id,
        "plan": plan_tier.value,
        "status": "pending_payment",
        "trial_start": None,
        "trial_end": None,
        "current_period_start": None,
        "current_period_end": None,
        "razorpay_subscription_id": rzp_sub_id,
        "created_at": now,
        "updated_at": now,
    })

    return CheckoutResponse(
        subscription_id=rzp_sub_id,
        razorpay_key_id=settings.razorpay_key_id,
        plan=plan_tier.value,
        amount_paise=plan_cfg["price_paise"],
        currency="INR",
        name="VERITAS AI",
        description=f"VERITAS AI {plan_cfg['name']} Subscription",
    )


def verify_checkout_signature(payment_id: str, subscription_id: str, signature: str) -> bool:
    """Verifies checkout signature returned by Razorpay Checkout in constant time.
    Formula: HMAC-SHA256(payment_id + '|' + subscription_id, secret)
    """
    secret = settings.razorpay_key_secret.strip()
    if not secret:
        return False
    data = f"{payment_id}|{subscription_id}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def verify_webhook_signature(raw_body: bytes, signature_header: str) -> bool:
    """Verifies X-Razorpay-Signature against raw request bytes in constant time."""
    secret = settings.razorpay_webhook_secret.strip()
    if not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature_header, expected)


def process_payment_verification(
    user: UserRecord,
    payment_id: str,
    subscription_id: str,
    signature: str,
) -> SubscriptionResponse:
    """Validates payment signature server-side and activates the paid subscription."""
    if not verify_checkout_signature(payment_id, subscription_id, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed: invalid signature.",
        )

    # Locate local subscription associated with this Razorpay subscription ID or user
    sub = get_subscription_by_razorpay_id(subscription_id)
    if not sub:
        sub = get_latest_subscription_by_user_id(user.id)
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription record not found for this account.",
            )

    # Security check: Ensure subscription belongs to this user
    if sub["user_id"] != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: subscription does not belong to this user account.",
        )

    now = datetime.now(timezone.utc)
    period_end = now + timedelta(days=30)

    update_subscription(sub["id"], {
        "status": SubscriptionStatus.ACTIVE.value,
        "current_period_start": now.isoformat(),
        "current_period_end": period_end.isoformat(),
        "razorpay_subscription_id": subscription_id,
        "updated_at": now.isoformat(),
    })

    updated = get_user_subscription(user.id)
    assert updated is not None
    return updated


def process_webhook_event(raw_body: bytes, signature_header: str, event_data: dict) -> dict:
    """Processes incoming Razorpay webhook events with signature verification and idempotency."""
    if not verify_webhook_signature(raw_body, signature_header):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature.",
        )

    event_id = event_data.get("id") or str(uuid4())
    event_type = event_data.get("event")

    # 1. Idempotency Check: Prevent duplicate webhook processing
    existing = get_payment_event(event_id)
    if existing:
        return {
            "status": "ignored",
            "message": "Event already processed (idempotent duplicate).",
            "provider_event_id": event_id,
        }

    # 2. Extract payload entities
    payload = event_data.get("payload", {})
    sub_entity = payload.get("subscription", {}).get("entity", {})
    payment_entity = payload.get("payment", {}).get("entity", {})

    rzp_sub_id = sub_entity.get("id") or payment_entity.get("subscription_id")
    now_utc = datetime.now(timezone.utc).isoformat()

    # 3. Route specific subscription lifecycle events
    if event_type in ("subscription.authenticated", "subscription.activated", "subscription.charged"):
        if rzp_sub_id:
            sub = get_subscription_by_razorpay_id(rzp_sub_id)
            if sub:
                start_ts = sub_entity.get("current_start")
                end_ts = sub_entity.get("current_end")

                p_start = (
                    datetime.fromtimestamp(start_ts, timezone.utc).isoformat()
                    if start_ts
                    else now_utc
                )
                p_end = (
                    datetime.fromtimestamp(end_ts, timezone.utc).isoformat()
                    if end_ts
                    else (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                )

                update_subscription(sub["id"], {
                    "status": SubscriptionStatus.ACTIVE.value,
                    "current_period_start": p_start,
                    "current_period_end": p_end,
                    "updated_at": now_utc,
                })

    elif event_type == "subscription.halted":
        if rzp_sub_id:
            sub = get_subscription_by_razorpay_id(rzp_sub_id)
            if sub:
                update_subscription(sub["id"], {
                    "status": SubscriptionStatus.PAST_DUE.value,
                    "updated_at": now_utc,
                })

    elif event_type == "subscription.cancelled":
        if rzp_sub_id:
            sub = get_subscription_by_razorpay_id(rzp_sub_id)
            if sub:
                update_subscription(sub["id"], {
                    "status": SubscriptionStatus.CANCELLED.value,
                    "updated_at": now_utc,
                })

    elif event_type == "subscription.completed":
        if rzp_sub_id:
            sub = get_subscription_by_razorpay_id(rzp_sub_id)
            if sub:
                update_subscription(sub["id"], {
                    "status": SubscriptionStatus.EXPIRED.value,
                    "updated_at": now_utc,
                })

    elif event_type == "payment.failed":
        if rzp_sub_id:
            sub = get_subscription_by_razorpay_id(rzp_sub_id)
            if sub:
                update_subscription(sub["id"], {
                    "status": SubscriptionStatus.PAST_DUE.value,
                    "updated_at": now_utc,
                })

    # Record event in payment_events for idempotency
    record_payment_event(event_id, event_type or "unknown", "processed")

    return {
        "status": "processed",
        "event": event_type,
        "provider_event_id": event_id,
    }
