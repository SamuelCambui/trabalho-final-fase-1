"""Ponto de entrada da aplicação FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.api.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
)

from src.api.dependencies import get_predictor_service

from src.api.routers import (
    health_router,
    predictions_router,
    auth_router,
)

from src.api.templates.index import get_home_page


# ==========================================
# LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Carrega o modelo na inicialização."""

    predictor = get_predictor_service()

    predictor.load()

    yield


# ==========================================
# FASTAPI
# ==========================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)


# ==========================================
# INTERFACE
# ==========================================

@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def home() -> HTMLResponse:
    """Exibe a interface web."""

    return get_home_page()


# ==========================================
# ROTAS DA API
# ==========================================

app.include_router(health_router)

app.include_router(predictions_router)

app.include_router(auth_router)