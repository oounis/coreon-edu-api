from fastapi import APIRouter, Response
from app.monitoring.metrics import metrics

router = APIRouter()

@router.get("/metrics")
def metrics_text():
    # text/plain for Prometheus scrapes
    body = metrics.dump_prometheus()
    return Response(content=body, media_type="text/plain")
