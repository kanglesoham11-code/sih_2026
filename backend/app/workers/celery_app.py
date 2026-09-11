"""
Celery Application Configuration
PRD Section 21 - Background Task Processing
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


# Initialize Celery app
celery_app = Celery(
    "orca",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.tasks",
        "app.workers.scheduled_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.workers.tasks.refresh_source_task": {"queue": "refresh"},
        "app.workers.tasks.ingest_data_task": {"queue": "ingest"},
        "app.workers.tasks.process_forecast_task": {"queue": "forecast"},
        "app.workers.scheduled_tasks.*": {"queue": "scheduled"},
    },
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_extended=True,
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Task execution limits
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Scheduled tasks configuration
celery_app.conf.beat_schedule = {
    # Refresh high-priority sources every 15 minutes
    "refresh-critical-sources": {
        "task": "app.workers.scheduled_tasks.refresh_critical_sources",
        "schedule": crontab(minute="*/15"),
    },
    
    # Refresh medium-priority sources every hour
    "refresh-medium-sources": {
        "task": "app.workers.scheduled_tasks.refresh_medium_sources",
        "schedule": crontab(minute="0"),
    },
    
    # Generate PFZ forecasts daily at 00:00 UTC
    "generate-pfz-forecasts": {
        "task": "app.workers.scheduled_tasks.generate_pfz_forecasts",
        "schedule": crontab(hour="0", minute="0"),
    },
    
    # Health check all sources every 5 minutes
    "health-check-sources": {
        "task": "app.workers.scheduled_tasks.health_check_all_sources",
        "schedule": crontab(minute="*/5"),
    },
    
    # Clean up old data every day at 02:00 UTC
    "cleanup-old-data": {
        "task": "app.workers.scheduled_tasks.cleanup_old_data",
        "schedule": crontab(hour="2", minute="0"),
    },
    
    # Archive raw provenance data weekly
    "archive-provenance": {
        "task": "app.workers.scheduled_tasks.archive_provenance_data",
        "schedule": crontab(hour="3", minute="0", day_of_week="0"),
    },
}


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f"Request: {self.request!r}")
