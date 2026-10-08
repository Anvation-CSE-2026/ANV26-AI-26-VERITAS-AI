"""Billing and subscription logic: plans, application-managed 30-day free trials,
status calculations, and server-side monthly analysis quota enforcement.
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException, status

from app.config import settings
from app.models.auth import UserRecord
from app.models.billing import (
    PLAN_CONFIGS,
    PlanDetail,
    PlanFeatures,
    PlanTier,
    SubscriptionResponse,
    SubscriptionStatus,
)
from app.services.storage import (
    count_analyses_in_period,
    get_latest_subscription_by_user_id,
    record_analysis_usage,
    save_subscription,
    set_user_trial_used,
    update_subscription,
)


def get_current_billing_period(period_start: str | None = None) -> str:
    """Computes standard billing period string (e.g. '2026-10' or date-based key)."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m")


def get_all_plans() -> list[PlanDetail]:
    """Returns available plans with current pricing and feature permissions."""
    plans = []
    for tier, cfg in PLAN_CONFIGS.items():
        rzp_id = (
            settings.razorpay_standard_plan_id
            if tier == "standard"
            else settings.razorpay_pro_plan_id
        )
        plans.append(
            PlanDetail(
                tier=cfg["tier"],
                name=cfg["name"],
                price_inr=cfg["price_inr"],
                interval=cfg["interval"],
                trial_days=cfg["trial_days"],
                monthly_analyses_limit=cfg["monthly_analyses_limit"],
                analysis_history_limit=cfg["analysis_history_limit"],
                features=cfg["features"],
                razorpay_plan_id=rzp_id if rzp_id else None,
            )
        )
    return plans


def get_plan_config(plan_tier: str) -> dict:
    clean = plan_tier.lower()
    if clean not in PLAN_CONFIGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown plan tier: '{plan_tier}'. Available plans: standard, pro.",
        )
    return PLAN_CONFIGS[clean]


def start_trial(user: UserRecord, plan_tier: PlanTier) -> SubscriptionResponse:
    """Activates introductory 30-day free trial for eligible user accounts."""
    if user.trial_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account has already utilized its one introductory 30-day free trial.",
        )

    # Check if user already has an active subscription
    current_sub = get_latest_subscription_by_user_id(user.id)
    if current_sub and current_sub["status"] in (SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already has an active subscription or trial ({current_sub['status']}).",
        )

    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=30)
    sub_id = str(uuid4())

    sub_data = {
        "id": sub_id,
        "user_id": user.id,
        "plan": plan_tier.value,
        "status": SubscriptionStatus.TRIALING.value,
        "trial_start": now.isoformat(),
        "trial_end": trial_end.isoformat(),
        "current_period_start": now.isoformat(),
        "current_period_end": trial_end.isoformat(),
        "razorpay_subscription_id": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    save_subscription(sub_data)
    set_user_trial_used(user.id)

    return get_user_subscription(user.id)


def get_user_subscription(user_id: str) -> SubscriptionResponse | None:
    """Retrieves current subscription, enforces server-side expiration, and computes quota usage."""
    raw_sub = get_latest_subscription_by_user_id(user_id)
    if not raw_sub:
        return None

    now = datetime.now(timezone.utc)
    current_status = raw_sub["status"]

    # 1. Enforce trial expiration server-side
    if current_status == SubscriptionStatus.TRIALING.value:
        if raw_sub.get("trial_end"):
            try:
                t_end = datetime.fromisoformat(raw_sub["trial_end"])
                if t_end.tzinfo is None:
                    t_end = t_end.replace(tzinfo=timezone.utc)
                if now >= t_end:
                    # Trial expired
                    current_status = SubscriptionStatus.EXPIRED.value
                    update_subscription(
                        raw_sub["id"],
                        {"status": current_status, "updated_at": now.isoformat()},
                    )
                    raw_sub["status"] = current_status
            except (ValueError, TypeError):
                pass

    # 2. Enforce paid subscription period expiration server-side
    elif current_status == SubscriptionStatus.ACTIVE.value:
        if raw_sub.get("current_period_end"):
            try:
                p_end = datetime.fromisoformat(raw_sub["current_period_end"])
                if p_end.tzinfo is None:
                    p_end = p_end.replace(tzinfo=timezone.utc)
                if now >= p_end and not raw_sub.get("razorpay_subscription_id"):
                    current_status = SubscriptionStatus.EXPIRED.value
                    update_subscription(
                        raw_sub["id"],
                        {"status": current_status, "updated_at": now.isoformat()},
                    )
                    raw_sub["status"] = current_status
            except (ValueError, TypeError):
                pass

    plan_cfg = get_plan_config(raw_sub["plan"])
    period = get_current_billing_period(raw_sub.get("current_period_start"))
    used_count = count_analyses_in_period(user_id, period)
    limit = plan_cfg["monthly_analyses_limit"]
    remaining = max(0, limit - used_count)
    is_active = current_status in (
        SubscriptionStatus.TRIALING.value,
        SubscriptionStatus.ACTIVE.value,
    )

    return SubscriptionResponse(
        id=raw_sub["id"],
        user_id=raw_sub["user_id"],
        plan=raw_sub["plan"],
        status=current_status,
        trial_start=raw_sub.get("trial_start"),
        trial_end=raw_sub.get("trial_end"),
        current_period_start=raw_sub.get("current_period_start"),
        current_period_end=raw_sub.get("current_period_end"),
        razorpay_subscription_id=raw_sub.get("razorpay_subscription_id"),
        analyses_used=used_count,
        analyses_limit=limit,
        analyses_remaining=remaining,
        history_limit=plan_cfg["analysis_history_limit"],
        features=plan_cfg["features"],
        is_active=is_active,
        created_at=raw_sub["created_at"],
        updated_at=raw_sub["updated_at"],
    )


def enforce_analysis_quota(user_id: str) -> tuple[SubscriptionResponse, str]:
    """Server-side check executed BEFORE AI inference begins.
    Validates active subscription/trial and verifies monthly quota is not exhausted.
    """
    sub = get_user_subscription(user_id)
    if not sub or not sub.is_active:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "state": "payment_required",
                "message": (
                    "An active paid subscription or 30-day free trial is required to perform contract analysis."
                    if not sub
                    else f"Your subscription status is '{sub.status}'. Please activate or renew your subscription to continue."
                ),
                "upgrade_required": True,
                "current_status": sub.status if sub else "none",
            },
        )

    if sub.analyses_remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "state": "quota_exhausted",
                "message": (
                    f"Monthly contract analysis limit reached ({sub.analyses_used}/{sub.analyses_limit}). "
                    f"Upgrade to Pro or await the next monthly billing cycle."
                ),
                "analyses_used": sub.analyses_used,
                "analyses_limit": sub.analyses_limit,
                "billing_period": get_current_billing_period(),
            },
        )

    return sub, get_current_billing_period()


def record_successful_analysis_usage(user_id: str, analysis_id: str, period: str) -> None:
    """Records consumed analysis quota after successful verification and persistence."""
    record_analysis_usage(user_id, analysis_id, period)


def cancel_user_subscription(user_id: str) -> SubscriptionResponse:
    """Cancels active subscription or trial."""
    sub = get_user_subscription(user_id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription record found for this account.",
        )
    if sub.status == SubscriptionStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription is already cancelled.",
        )

    now = datetime.now(timezone.utc).isoformat()
    update_subscription(
        sub.id,
        {
            "status": SubscriptionStatus.CANCELLED.value,
            "updated_at": now,
        },
    )

    updated = get_user_subscription(user_id)
    assert updated is not None
    return updated

