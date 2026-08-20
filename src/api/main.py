"""Ponto de entrada da aplicação FastAPI."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from src.api.config import API_DESCRIPTION, API_TITLE, API_VERSION
from src.api.dependencies import get_predictor_service
from src.api.routers import health_router, predictions_router, auth_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Carrega o modelo na inicialização e libera recursos no shutdown."""
    predictor = get_predictor_service()
    predictor.load()
    yield


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(predictions_router)
app.include_router(auth_router)
