"""Razorpay webhook endpoint with raw body signature verification and idempotency."""
import json
from fastapi import APIRouter, Header, HTTPException, Request, status

from app.services.razorpay_service import process_webhook_event

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
) -> dict:
    """Receives and securely processes Razorpay lifecycle webhooks.
    Signature is verified against the raw request body.
    """
    if not x_razorpay_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Razorpay-Signature header.",
        )

    raw_body = await request.body()
    try:
        event_data = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload.",
        ) from None

    return process_webhook_event(
        raw_body=raw_body,
        signature_header=x_razorpay_signature,
        event_data=event_data,
    )

