"""Rotas de predição de churn."""

import time

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.dependencies import get_current_user, get_predictor_service
from src.api.logging_config import logger
from src.api.metrics import (
    ERRORS_TOTAL,
    PREDICTION_LATENCY,
    PREDICTIONS_TOTAL,
    record_prediction_confidence,
)
from src.api.schemas import CustomerRequest, PredictionResponse
from src.api.services.churn_predictor import ChurnPredictorService

router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.post("", response_model=PredictionResponse)
def predict_churn(
    customer: CustomerRequest,
    request: Request,
    predictor: ChurnPredictorService = Depends(get_predictor_service),
    _current_user: dict = Depends(get_current_user),
) -> PredictionResponse:
    """Recebe os dados de um cliente e retorna a predição de churn."""

    trace_id = getattr(request.state, "trace_id", None)

    if not predictor.is_loaded:
        ERRORS_TOTAL.labels(
            endpoint="/predict", error_type="model_unavailable"
        ).inc()
        logger.error(
            "prediction_unavailable",
            extra={"trace_id": trace_id, "error": str(predictor.load_error)},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Modelo indisponível: {predictor.load_error}",
        )

    start = time.perf_counter()
    try:
        prediction, probability = predictor.predict(customer.model_dump())
    except ValueError as exc:
        ERRORS_TOTAL.labels(
            endpoint="/predict", error_type="validation_error"
        ).inc()
        # Não logamos o payload do cliente: pode conter dados
        # pessoais (LGPD/GDPR). Registramos apenas que a validação
        # falhou e por quê.
        logger.warning(
            "prediction_validation_error",
            extra={"trace_id": trace_id, "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    latency = time.perf_counter() - start

    PREDICTIONS_TOTAL.labels(
        classe=prediction, user=_current_user["username"]
    ).inc()
    PREDICTION_LATENCY.observe(latency)
    record_prediction_confidence(probability)

    logger.info(
        "prediction_completed",
        extra={
            "trace_id": trace_id,
            "user": _current_user["username"],
            "prediction": prediction,
            "probability": probability,
            "latency_ms": round(latency * 1000, 2),
        },
    )

    return PredictionResponse(
        prediction=prediction,
        probability=probability,
    )
