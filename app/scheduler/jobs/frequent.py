from apscheduler.schedulers.base import BaseScheduler
from app.core.logging_config import logger
from app.monitoring.metrics import metrics


def _five_min_health_job():
    logger.info("Running 5-min health probe job (in-process scheduler)")
    metrics.inc("scheduler_runs_total", labels={"job": "health_probe"})


def register_frequent_jobs(scheduler: BaseScheduler):
    scheduler.add_job(
        _five_min_health_job,
        "interval",
        minutes=5,
        id="five_min_health",
        replace_existing=True,
    )
