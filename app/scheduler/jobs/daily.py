from apscheduler.schedulers.base import BaseScheduler
from app.core.logging_config import logger
from app.monitoring.metrics import metrics


def _daily_maintenance_job():
    logger.info("Running daily maintenance job (in-process scheduler)")
    metrics.inc("scheduler_runs_total", labels={"job": "daily_maintenance"})


def register_daily_jobs(scheduler: BaseScheduler):
    scheduler.add_job(
        _daily_maintenance_job,
        "cron",
        hour=1,
        minute=0,
        id="daily_maintenance",
        replace_existing=True,
    )
