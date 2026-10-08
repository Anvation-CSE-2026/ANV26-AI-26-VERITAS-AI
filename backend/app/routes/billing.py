"""Billing routes: plans, 30-day trials, subscriptions, checkout, verification, and cancellation."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.auth import UserRecord
from app.models.billing import (
    CancelSubscriptionResponse,
    CheckoutRequest,
    CheckoutResponse,
    PlansListResponse,
    SubscriptionResponse,
    TrialStartRequest,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)
from app.services.billing import (
    cancel_user_subscription,
    get_all_plans,
    get_user_subscription,
    start_trial,
)
from app.services.razorpay_service import (
    create_subscription_checkout,
    process_payment_verification,
)
from app.services.security import get_current_user

router = APIRouter(prefix="/api/billing", tags=["Billing & Subscriptions"])


@router.get("/plans", response_model=PlansListResponse)
def list_plans() -> PlansListResponse:
    """Returns available subscription tiers, pricing, and feature permissions."""
    return PlansListResponse(plans=get_all_plans())


@router.post("/trial/start", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def activate_free_trial(
    request: TrialStartRequest,
    current_user: UserRecord = Depends(get_current_user),
) -> SubscriptionResponse:
    """Starts an introductory 30-day free trial for eligible user accounts."""
    return start_trial(current_user, request.plan)


@router.get("/subscription", response_model=SubscriptionResponse)
def read_current_subscription(
    current_user: UserRecord = Depends(get_current_user),
) -> SubscriptionResponse:
    """Returns current user's subscription, trial status, and remaining monthly quota."""
    sub = get_user_subscription(current_user.id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active or past subscription found for this account. Activate a 30-day trial or paid plan.",
        )
    return sub


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(
    request: CheckoutRequest,
    current_user: UserRecord = Depends(get_current_user),
) -> CheckoutResponse:
    """Creates a Razorpay Test Mode subscription checkout."""
    return create_subscription_checkout(current_user, request.plan)


@router.post("/verify", response_model=VerifyPaymentResponse)
def verify_payment(
    request: VerifyPaymentRequest,
    current_user: UserRecord = Depends(get_current_user),
) -> VerifyPaymentResponse:
    """Verifies checkout HMAC signature and activates the paid subscription."""
    sub = process_payment_verification(
        user=current_user,
        payment_id=request.razorpay_payment_id,
        subscription_id=request.razorpay_subscription_id,
        signature=request.razorpay_signature,
    )
    return VerifyPaymentResponse(
        success=True,
        status="active",
        message="Payment verified successfully. Subscription activated.",
        subscription=sub,
    )


@router.post("/cancel", response_model=CancelSubscriptionResponse)
def cancel_subscription(
    current_user: UserRecord = Depends(get_current_user),
) -> CancelSubscriptionResponse:
    """Cancels active subscription or trial."""
    sub = cancel_user_subscription(current_user.id)
    return CancelSubscriptionResponse(
        success=True,
        message="Subscription has been cancelled.",
        subscription=sub,
    )

