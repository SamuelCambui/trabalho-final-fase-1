"""Routers HTTP da API."""

from src.api.routers.health import router as health_router
from src.api.routers.predictions import router as predictions_router
from src.api.routers.auth import router as auth_router

__all__ = ["health_router", "predictions_router", "auth_router"]
