import asyncio
from datetime import date, timedelta

import structlog

from app.jobs.celery_app import celery_app

logger = structlog.get_logger()


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3)
def generate_all_daily_reports(self):
    """Generate and deliver daily reports for all active businesses."""
    run_async(_generate_all_daily_reports())


async def _generate_all_daily_reports():
    from app.ai.insight_engine import InsightEngine
    from app.database.session import async_session_factory
    from app.models.report import ReportDelivery, ReportStatus
    from app.repositories.business_repository import BusinessRepository
    from app.repositories.report_repository import ReportRepository
    from app.repositories.transaction_repository import TransactionRepository
    from app.services.whatsapp_service import WhatsAppService

    report_date = date.today() - timedelta(days=1)
    whatsapp = WhatsAppService()
    ai_engine = InsightEngine()

    async with async_session_factory() as db:
        business_repo = BusinessRepository(db)
        report_repo = ReportRepository(db)
        txn_repo = TransactionRepository(db)

        businesses = await business_repo.get_all_active()
        logger.info("Starting daily report generation", count=len(businesses))

        for business in businesses:
            try:
                # Calculate metrics
                revenue = await txn_repo.get_daily_revenue(business.id, report_date)
                orders_count = await txn_repo.get_daily_orders_count(business.id, report_date)
                avg_order_value = revenue / orders_count if orders_count > 0 else 0.0

                prev_date = report_date - timedelta(days=1)
                prev_revenue = await txn_repo.get_daily_revenue(business.id, prev_date)
                growth_pct = None
                if prev_revenue > 0:
                    growth_pct = ((revenue - prev_revenue) / prev_revenue) * 100

                top_products = await txn_repo.get_top_products(business.id, report_date)
                top_product = top_products[0]["name"] if top_products else None

                # Generate AI insights
                insights = await ai_engine.generate_insights(
                    business_name=business.name,
                    industry=business.industry,
                    currency=business.currency,
                    report_date=str(report_date),
                    revenue=revenue,
                    orders_count=orders_count,
                    avg_order_value=avg_order_value,
                    revenue_growth_pct=growth_pct,
                    top_products=top_products,
                    prev_revenue=prev_revenue,
                )

                # Format WhatsApp message
                owner_name = business.owner.full_name.split()[0] if business.owner else "there"
                message = whatsapp.format_daily_report(
                    owner_name=owner_name,
                    currency=business.currency,
                    revenue=revenue,
                    orders_count=orders_count,
                    orders_growth_pct=growth_pct,
                    avg_order_value=avg_order_value,
                    top_product=top_product,
                    inventory_alert=None,
                    ai_insight=insights["insight"],
                    recommendation=insights["recommendation"],
                )

                # Save report
                from app.models.report import Report

                report = Report(
                    business_id=business.id,
                    report_date=report_date,
                    status=ReportStatus.GENERATED,
                    revenue=revenue,
                    orders_count=orders_count,
                    avg_order_value=avg_order_value,
                    revenue_growth_pct=growth_pct,
                    top_product=top_product,
                    metrics_json={"top_products": top_products},
                    ai_summary=insights["summary"],
                    ai_insight=insights["insight"],
                    ai_recommendation=insights["recommendation"],
                    whatsapp_message=message,
                )
                report = await report_repo.create(report)

                # Send WhatsApp
                try:
                    result = await whatsapp.send_message(business.whatsapp_number, message)
                    msg_id = result.get("messages", [{}])[0].get("id", "")
                    delivery = ReportDelivery(
                        report_id=report.id,
                        whatsapp_number=business.whatsapp_number,
                        status="sent",
                        whatsapp_message_id=msg_id,
                    )
                    await report_repo.create_delivery(delivery)
                    report.status = "delivered"
                except Exception as e:
                    delivery = ReportDelivery(
                        report_id=report.id,
                        whatsapp_number=business.whatsapp_number,
                        status="failed",
                        error_message=str(e),
                    )
                    await report_repo.create_delivery(delivery)

                await report_repo.update(report)
                await db.commit()
                logger.info("Report generated", business=business.name)

            except Exception as e:
                logger.error("Failed to generate report", business=business.name, error=str(e))
                continue


@celery_app.task(bind=True, max_retries=3)
def resend_report(self, report_id: str):
    """Manually resend a report via WhatsApp."""
    run_async(_resend_report(report_id))


async def _resend_report(report_id: str):
    import uuid

    from app.database.session import async_session_factory
    from app.models.report import ReportDelivery
    from app.repositories.report_repository import ReportRepository
    from app.services.whatsapp_service import WhatsAppService

    async with async_session_factory() as db:
        report_repo = ReportRepository(db)
        report = await report_repo.get_by_id(uuid.UUID(report_id))
        if not report or not report.whatsapp_message:
            return

        whatsapp = WhatsAppService()
        business = report.business
        try:
            result = await whatsapp.send_message(
                business.whatsapp_number, report.whatsapp_message
            )
            msg_id = result.get("messages", [{}])[0].get("id", "")
            delivery = ReportDelivery(
                report_id=report.id,
                whatsapp_number=business.whatsapp_number,
                status="sent",
                whatsapp_message_id=msg_id,
            )
            await report_repo.create_delivery(delivery)
            await db.commit()
        except Exception as e:
            logger.error("Resend failed", report_id=report_id, error=str(e))
