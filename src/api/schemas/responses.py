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


class ErrorDetail(BaseModel):
    """Detalhe de um erro retornado pela API."""

    code: int = Field(description="Código HTTP do erro.")
    message: str = Field(description="Mensagem descritiva do erro.")
    trace_id: str | None = Field(
        default=None,
        description="Identificador da requisição, para correlacionar com os logs.",
    )


class ErrorResponse(BaseModel):
    """Envelope único de erro usado por toda a API (auth, predictions, health).

    Qualquer HTTPException ou erro de validação levantado em qualquer rota
    é convertido para este formato pelos exception handlers em ``main.py``,
    em vez de cada router montar seu próprio corpo de erro.
    """

    error: ErrorDetail
