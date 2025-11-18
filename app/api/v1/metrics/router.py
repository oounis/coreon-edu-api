from fastapi import APIRouter
from app.monitoring.metrics import metrics

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/debug")
def get_metrics_debug():
    """
    Debug endpoint to view in-memory metrics snapshot.
    Not for production public exposure.
    """
    return metrics.snapshot()
