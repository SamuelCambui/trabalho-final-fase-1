"""Schemas de resposta da API."""

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """Resultado da predição de churn para um cliente."""

    prediction: str = Field(description="Classificação: 'Yes' (churn) ou 'No'.")
    probability: float = Field(
        ge=0.0,
        le=1.0,
        description="Probabilidade estimada de churn.",
    )


class HealthResponse(BaseModel):
    """Status operacional da API e do modelo."""

    status: str
    model_loaded: bool
    model_path: str | None = None


class ModelInfoResponse(BaseModel):
    """Metadados básicos do artefato de modelo carregado."""

    model_path: str
    model_type: str
    threshold: float
