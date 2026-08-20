"""Rotas de predição de churn."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user, get_predictor_service
from src.api.schemas import CustomerRequest, PredictionResponse
from src.api.services.churn_predictor import ChurnPredictorService

router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.post("", response_model=PredictionResponse)
def predict_churn(
    customer: CustomerRequest,
    predictor: ChurnPredictorService = Depends(get_predictor_service),
    _current_user: dict = Depends(get_current_user),
) -> PredictionResponse:
    """Recebe os dados de um cliente e retorna a predição de churn."""
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Modelo indisponível: {predictor.load_error}",
        )

    try:
        prediction, probability = predictor.predict(customer.model_dump())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return PredictionResponse(
        prediction=prediction,
        probability=probability,
    )
