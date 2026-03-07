# backend/app/main.py

import time
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .instrumentation import limiter
from .domains import routes as domain_routes
from .ssl import routes as ssl_routes
from .users import routes as user_routes
from .dashboard import router as dashboard_router
from .auth_endpoints import router as auth_router
from .monitoring.routes import router as monitoring_router
from .backups.routes import router as backup_router
from .performance.routes import router as performance_router
from .config import settings
from .radar.routes import router as radar_router

from .metrics import performance_metrics

settings.validate_security_settings()

BASE_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}
CSP_HEADER = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'; "
    "object-src 'none'; "
    "form-action 'self'"
)
DOCS_PREFIXES = ("/docs", "/redoc", "/openapi.json")

app = FastAPI(title="Domain & SSL Manager API")
instrumentor = Instrumentator()
instrumentor.instrument(app).expose(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Uložíme metriku (iba pre /api endpointy)
    if request.url.path.startswith("/api"):
        performance_metrics.append({
            "path": str(request.url.path),
            "method": request.method,
            "latency": process_time,
            "status": response.status_code,
            "timestamp": time.time()
        })
        # Keep only last 100
        if len(performance_metrics) > 100:
            performance_metrics.pop(0)

    for header, value in BASE_SECURITY_HEADERS.items():
        response.headers.setdefault(header, value)

    if settings.ENV.lower() == "production":
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains; preload",
        )

    if not request.url.path.startswith(DOCS_PREFIXES):
        response.headers.setdefault("Content-Security-Policy", CSP_HEADER)

    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS.split(",")
)

app.include_router(domain_routes.router, prefix="/api")
app.include_router(ssl_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(monitoring_router, prefix="/api")
app.include_router(backup_router, prefix="/api")
app.include_router(performance_router, prefix="/api")
app.include_router(radar_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}

@app.get("/")
def root():
    return {
        "message": "API Centrum - Domain & SSL Manager",
        "version": "1.0.0",
        "documentation": "/docs",
        "neon_auth_trial": "active" if settings.ENV == "development" else "check_status"
    }
