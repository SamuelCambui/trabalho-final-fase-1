"""Schemas Pydantic expostos pela API."""

from src.api.schemas.customer import CustomerRequest
from src.api.schemas.login_config import LoginRequest, TokenResponse, UserInfoResponse
from src.api.schemas.responses import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
)

__all__ = [
    "CustomerRequest",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "LoginRequest",
    "ModelInfoResponse",
    "PredictionResponse",
    "TokenResponse",
    "UserInfoResponse",
]
