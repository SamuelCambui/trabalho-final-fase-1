"""Rotas de health check e metadados do modelo."""

from fastapi import APIRouter, Depends

from src.api.config import MODEL_PATH, PREDICTION_THRESHOLD
from src.api.dependencies import get_predictor_service
from src.api.schemas import HealthResponse, ModelInfoResponse
from src.api.services.churn_predictor import ChurnPredictorService

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(
    predictor: ChurnPredictorService = Depends(get_predictor_service),
) -> HealthResponse:
    """Verifica se a API e o modelo estão operacionais."""
    return HealthResponse(
        status="ok" if predictor.is_loaded else "degraded",
        model_loaded=predictor.is_loaded,
        model_path=str(MODEL_PATH) if predictor.is_loaded else None,
    )


@router.get("/model/info", response_model=ModelInfoResponse)
def model_info(
    predictor: ChurnPredictorService = Depends(get_predictor_service),
) -> ModelInfoResponse:
    """Expõe informações básicas do artefato de modelo em uso."""
    return ModelInfoResponse(
        model_path=str(MODEL_PATH),
        model_type=predictor.get_model_type(),
        threshold=PREDICTION_THRESHOLD,
    )
