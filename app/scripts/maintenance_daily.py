from app.core.logging_config import logger
from app.monitoring.metrics import metrics


def main():
    logger.info("CRON: running daily maintenance (external scheduler)")
    metrics.inc("cron_runs_total", labels={"job": "daily_maintenance"})


if __name__ == "__main__":
    main()
