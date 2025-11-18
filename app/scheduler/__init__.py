from apscheduler.schedulers.background import BackgroundScheduler
from app.core.logging_config import logger
from app.monitoring.metrics import metrics
from app.scheduler.jobs.daily import register_daily_jobs
from app.scheduler.jobs.frequent import register_frequent_jobs

scheduler = BackgroundScheduler(timezone="UTC")

register_daily_jobs(scheduler)
register_frequent_jobs(scheduler)

scheduler.start()
logger.info("In-process scheduler started")
