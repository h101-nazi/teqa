import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.session import get_db
from app.jobs.tasks import resend_report
from app.models.business import Business
from app.models.user import User
from app.schemas.report import DashboardOverview, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{business_id}", response_model=list[ReportResponse])
async def list_reports(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Business).where(
            Business.id == uuid.UUID(business_id),
            Business.owner_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    service = ReportService(db)
    reports = await service.get_reports(uuid.UUID(business_id))
    return reports


@router.post("/{business_id}/generate", response_model=ReportResponse)
async def generate_report(
    business_id: str,
    report_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Business).where(
            Business.id == uuid.UUID(business_id),
            Business.owner_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    if report_date is None:
        from datetime import timedelta

        report_date = date.today() - timedelta(days=1)

    service = ReportService(db)
    report = await service.generate_daily_report(uuid.UUID(business_id), report_date)
    return report


@router.post("/{report_id}/resend", status_code=status.HTTP_202_ACCEPTED)
async def resend_report_endpoint(
    report_id: str,
    current_user: User = Depends(get_current_user),
):
    resend_report.delay(report_id)
    return {"message": "Report resend queued"}


@router.get("/{business_id}/dashboard", response_model=DashboardOverview)
async def get_dashboard(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import timedelta

    from sqlalchemy import func

    from app.models.integration import Integration
    from app.models.report import ReportDelivery
    from app.models.subscription import Subscription
    from app.repositories.transaction_repository import TransactionRepository

    result = await db.execute(
        select(Business).where(
            Business.id == uuid.UUID(business_id),
            Business.owner_id == current_user.id,
        )
    )
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    txn_repo = TransactionRepository(db)
    today = date.today()
    yesterday = today - timedelta(days=1)

    revenue = await txn_repo.get_daily_revenue(business.id, yesterday)
    orders = await txn_repo.get_daily_orders_count(business.id, yesterday)
    avg_order = revenue / orders if orders > 0 else 0.0
    prev_revenue = await txn_repo.get_daily_revenue(business.id, yesterday - timedelta(days=1))
    growth = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else None

    delivered_result = await db.execute(
        select(func.count(ReportDelivery.id)).where(
            ReportDelivery.status == "delivered",
        )
    )
    reports_delivered = int(delivered_result.scalar_one())

    integrations_result = await db.execute(
        select(func.count(Integration.id)).where(
            Integration.business_id == business.id,
            Integration.status == "connected",
        )
    )
    active_integrations = int(integrations_result.scalar_one())

    sub_result = await db.execute(
        select(Subscription).where(Subscription.business_id == business.id)
    )
    sub = sub_result.scalar_one_or_none()

    return DashboardOverview(
        total_revenue_today=revenue,
        total_orders_today=orders,
        avg_order_value=avg_order,
        revenue_growth_pct=growth,
        reports_delivered=reports_delivered,
        active_integrations=active_integrations,
        subscription_plan=sub.plan if sub else None,
        subscription_status=sub.status if sub else None,
    )
