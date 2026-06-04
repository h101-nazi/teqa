from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "teqa",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Cairo",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "generate-daily-reports": {
        "task": "app.jobs.tasks.generate_all_daily_reports",
        "schedule": crontab(hour=8, minute=0),  # 8:00 AM Cairo time
    },
}
