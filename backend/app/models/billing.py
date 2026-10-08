from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class PlanTier(str, Enum):
    STANDARD = "standard"
    PRO = "pro"


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"


class PlanFeatures(BaseModel):
    contract_analysis: bool = True
    risk_dashboard: bool = True
    evidence_explorer: bool = True
    policy_comparison: bool = True
    obligation_tracker: bool = True
    focused_knowledge_graph: bool = True
    category_knowledge_graph: bool = False
    full_network_knowledge_graph: bool = False
    priority_processing: bool = False


PLAN_CONFIGS: dict[str, dict[str, Any]] = {
    "standard": {
        "tier": "standard",
        "name": "Standard Plan",
        "price_inr": 199,
        "price_paise": 19900,
        "interval": "monthly",
        "trial_days": 30,
        "monthly_analyses_limit": 10,
        "analysis_history_limit": 5,
        "features": PlanFeatures(
            contract_analysis=True,
            risk_dashboard=True,
            evidence_explorer=True,
            policy_comparison=True,
            obligation_tracker=True,
            focused_knowledge_graph=True,
            category_knowledge_graph=False,
            full_network_knowledge_graph=False,
            priority_processing=False,
        ),
    },
    "pro": {
        "tier": "pro",
        "name": "Pro Plan",
        "price_inr": 299,
        "price_paise": 29900,
        "interval": "monthly",
        "trial_days": 30,
        "monthly_analyses_limit": 30,
        "analysis_history_limit": 30,
        "features": PlanFeatures(
            contract_analysis=True,
            risk_dashboard=True,
            evidence_explorer=True,
            policy_comparison=True,
            obligation_tracker=True,
            focused_knowledge_graph=True,
            category_knowledge_graph=True,
            full_network_knowledge_graph=True,
            priority_processing=False,
        ),
    },
}


class PlanDetail(BaseModel):
    tier: str
    name: str
    price_inr: int
    interval: str
    trial_days: int
    monthly_analyses_limit: int
    analysis_history_limit: int
    features: PlanFeatures
    razorpay_plan_id: str | None = None


class PlansListResponse(BaseModel):
    plans: list[PlanDetail]


class TrialStartRequest(BaseModel):
    plan: PlanTier = Field(default=PlanTier.STANDARD, description="Selected plan tier: standard or pro")


class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan: str
    status: str
    trial_start: str | None = None
    trial_end: str | None = None
    current_period_start: str | None = None
    current_period_end: str | None = None
    razorpay_subscription_id: str | None = None
    analyses_used: int
    analyses_limit: int
    analyses_remaining: int
    history_limit: int
    features: PlanFeatures
    is_active: bool
    created_at: str
    updated_at: str


class CheckoutRequest(BaseModel):
    plan: PlanTier = Field(..., description="Plan tier: standard or pro")


class CheckoutResponse(BaseModel):
    subscription_id: str
    razorpay_key_id: str
    plan: str
    amount_paise: int
    currency: str = "INR"
    name: str
    description: str


class VerifyPaymentRequest(BaseModel):
    razorpay_payment_id: str = Field(..., description="Payment ID returned by Razorpay Checkout")
    razorpay_subscription_id: str = Field(..., description="Subscription ID returned by Razorpay Checkout")
    razorpay_signature: str = Field(..., description="HMAC SHA256 signature returned by Razorpay Checkout")


class VerifyPaymentResponse(BaseModel):
    success: bool
    status: str
    message: str
    subscription: SubscriptionResponse


class CancelSubscriptionResponse(BaseModel):
    success: bool
    message: str
    subscription: SubscriptionResponse

