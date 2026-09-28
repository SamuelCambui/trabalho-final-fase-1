"""Ponto de entrada da aplicação FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
)
from src.api.dependencies import get_predictor_service
from src.api.logging_config import logger
from src.api.metrics import MODEL_LOADED
from src.api.middleware import LoggingMiddleware
from src.api.routers import (
    auth_router,
    health_router,
    predictions_router,
)
from src.api.schemas import ErrorDetail, ErrorResponse
from src.api.templates.index import get_home_page

# ==========================================
# LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Carrega o modelo na inicialização."""

    predictor = get_predictor_service()

    predictor.load()

    if predictor.is_loaded:
        logger.info(
            "model_loaded",
            extra={"model_type": predictor.get_model_type()},
        )
        MODEL_LOADED.set(1)
    else:
        logger.error(
            "model_load_failed",
            extra={"error": str(predictor.load_error)},
        )
        MODEL_LOADED.set(0)

    yield

    logger.info("api_shutdown")


# ==========================================
# FASTAPI
# ==========================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

# Instrumentação automática do Prometheus: adiciona métricas HTTP
# padrão (contagem de requisições, latência por rota, etc.) e expõe
# tudo — as automáticas e as customizadas de src/api/metrics.py — no
# endpoint /metrics, no formato que o Prometheus sabe coletar.
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# ==========================================
# EXCEPTION HANDLERS
# ==========================================
# Formato único de erro para toda a API: qualquer HTTPException levantada
# em qualquer router (auth.py, predictions.py, health.py, dependencies.py)
# ou erro de validação do Pydantic passa por aqui e sai no mesmo formato
# {"error": {"code", "message", "trace_id"}}, em vez de cada rota montar
# seu próprio corpo de erro.


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Converte toda HTTPException (401, 403, 422, 503 etc.) no envelope único."""

    trace_id = getattr(request.state, "trace_id", None)

    body = ErrorResponse(
        error=ErrorDetail(
            code=exc.status_code,
            message=str(exc.detail),
            trace_id=trace_id,
        )
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(),
        headers=getattr(exc, "headers", None) or {},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Converte erros de validação do Pydantic (422) no mesmo envelope."""

    trace_id = getattr(request.state, "trace_id", None)

    message = "; ".join(
        f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
        for err in exc.errors()
    )

    body = ErrorResponse(
        error=ErrorDetail(
            code=422,
            message=message,
            trace_id=trace_id,
        )
    )

    return JSONResponse(status_code=422, content=body.model_dump())


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
