import uuid

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.database.session import get_db
from app.models.business import Business
from app.models.subscription import PlanType, Subscription, SubscriptionStatus
from app.models.user import User

router = APIRouter(prefix="/billing", tags=["Billing"])

PLAN_PRICES = {
    PlanType.STARTER: {"price": 499, "price_id": settings.STRIPE_STARTER_PRICE_ID},
    PlanType.GROWTH: {"price": 999, "price_id": settings.STRIPE_GROWTH_PRICE_ID},
    PlanType.PRO: {"price": 2499, "price_id": settings.STRIPE_PRO_PRICE_ID},
}


@router.post("/{business_id}/subscribe")
async def create_subscription(
    business_id: str,
    plan: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Billing not configured")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    result = await db.execute(
        select(Business).where(
            Business.id == uuid.UUID(business_id),
            Business.owner_id == current_user.id,
        )
    )
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    if plan not in PLAN_PRICES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan")

    plan_info = PLAN_PRICES[plan]

    # Create or get Stripe customer
    sub_result = await db.execute(
        select(Subscription).where(Subscription.business_id == business.id)
    )
    subscription = sub_result.scalar_one_or_none()

    if subscription and subscription.stripe_customer_id:
        customer_id = subscription.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=business.name,
            metadata={"business_id": str(business.id)},
        )
        customer_id = customer.id

    # Create checkout session
    checkout = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": plan_info["price_id"], "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.CORS_ORIGINS[0]}/dashboard?subscription=success",
        cancel_url=f"{settings.CORS_ORIGINS[0]}/billing?subscription=canceled",
        metadata={"business_id": str(business.id), "plan": plan},
    )

    # Save/update subscription record
    if not subscription:
        subscription = Subscription(
            business_id=business.id,
            stripe_customer_id=customer_id,
            plan=plan,
            status=SubscriptionStatus.INACTIVE,
            monthly_price=plan_info["price"],
        )
        db.add(subscription)
    else:
        subscription.stripe_customer_id = customer_id
        subscription.plan = plan
        subscription.monthly_price = plan_info["price"]

    await db.flush()

    return {"checkout_url": checkout.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        business_id = session["metadata"]["business_id"]
        plan = session["metadata"]["plan"]

        sub_result = await db.execute(
            select(Subscription).where(Subscription.business_id == uuid.UUID(business_id))
        )
        subscription = sub_result.scalar_one_or_none()
        if subscription:
            subscription.stripe_subscription_id = session.get("subscription")
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.plan = plan

    elif event["type"] == "customer.subscription.deleted":
        sub_data = event["data"]["object"]
        sub_result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == sub_data["id"]
            )
        )
        subscription = sub_result.scalar_one_or_none()
        if subscription:
            subscription.status = SubscriptionStatus.CANCELED

    return {"status": "ok"}


@router.get("/{business_id}/subscription")
async def get_subscription(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Subscription).where(Subscription.business_id == uuid.UUID(business_id))
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return {"plan": None, "status": "inactive", "monthly_price": 0}
    return {
        "plan": sub.plan,
        "status": sub.status,
        "monthly_price": sub.monthly_price,
        "current_period_end": str(sub.current_period_end) if sub.current_period_end else None,
    }
