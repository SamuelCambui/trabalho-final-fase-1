"""Rotas legadas — não montadas por ``main.py``.

Mantidas apenas por compatibilidade. Preferir ``src.api.routers``.
"""

from fastapi import APIRouter, HTTPException

from src.api.config import MODEL_PATH, PREDICTION_THRESHOLD, PROBABILITY_DECIMALS
from src.api.schemas import CustomerRequest, PredictionResponse
from src.api.services.churn_predictor import ChurnPredictorService

router = APIRouter()

_predictor = ChurnPredictorService(
    model_path=MODEL_PATH,
    threshold=PREDICTION_THRESHOLD,
    probability_decimals=PROBABILITY_DECIMALS,
)
_predictor.load()


@router.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerRequest) -> PredictionResponse:
    if not _predictor.is_loaded:
        raise HTTPException(
            status_code=500,
            detail=f"Modelo não carregado: {_predictor.load_error}",
        )

    try:
        prediction, probability = _predictor.predict(customer.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictionResponse(prediction=prediction, probability=probability)
