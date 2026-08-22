"""Ponto de entrada da aplicação FastAPI."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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


# ==========================================
# TEMPLATES HTML
# ==========================================

templates = Jinja2Templates(
    directory="src/api/templates"
)


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
# ROTA DA INTERFACE
# ==========================================

@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


# ==========================================
# ROTAS DA API
# ==========================================

app.include_router(health_router)

app.include_router(predictions_router)

app.include_router(auth_router)