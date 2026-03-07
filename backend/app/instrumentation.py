# backend/app/instrumentation.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import Limiter
from slowapi.util import get_remote_address
from .config import settings

# Inicializácia Sentry
import os
if settings.ENV != "testing":
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if dsn and "your-sentry-dsn" not in dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=1.0,
            environment=settings.ENV
        )

# Inicializácia Limiter (Rate Limiting)
limiter = Limiter(key_func=get_remote_address)
