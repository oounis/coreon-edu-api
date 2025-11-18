from app.core.logging_config import logger
from app.monitoring.metrics import metrics


def main():
    logger.info("CRON: running 5-min health probe (external scheduler)")
    metrics.inc("cron_runs_total", labels={"job": "health_probe"})


if __name__ == "__main__":
    main()
