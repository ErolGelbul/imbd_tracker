from logging import getLogger

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.base import BaseHTTPMiddleware

from api.settings import settings_instance, Settings


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, test_option: bool = False):
        super().__init__(app)
        self._test_option = test_option

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Custom"] = "Example"
        return response

class PrometheusMiddleware:
    def __init__(self, app: FastAPI):
        logger = getLogger("api.PrometheusMiddleware")
        settings: Settings = settings_instance()
        if settings.enable_metrics:
            logger.info("metrics enabled")
            Instrumentator().instrument(app).expose(app)
        else:
            logger.info("metrics disabled")