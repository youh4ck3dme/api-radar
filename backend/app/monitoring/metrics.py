# backend/app/monitoring/metrics.py

from prometheus_fastapi_instrumentator import Instrumentator

instrumentor = Instrumentator()

def instrument(app):
    """Instrument the FastAPI app with Prometheus metrics and expose the /metrics endpoint."""
    instrumentor.instrument(app).expose(app)
