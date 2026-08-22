"""Dependências compartilhadas das rotas da API."""

import jwt

from fastapi import Cookie, Depends, HTTPException, status

from src.api.config import (
    MODEL_PATH,
    PREDICTION_THRESHOLD,
    PROBABILITY_DECIMALS,
)

from src.api.services.auth_service import AuthService
from src.api.services.churn_predictor import ChurnPredictorService


predictor_service = ChurnPredictorService(
    model_path=MODEL_PATH,
    threshold=PREDICTION_THRESHOLD,
    probability_decimals=PROBABILITY_DECIMALS,
)

auth_service = AuthService()


def get_predictor_service() -> ChurnPredictorService:
    """Retorna a instância singleton do serviço de predição."""

    return predictor_service


def get_auth_service() -> AuthService:
    """Retorna a instância singleton do serviço de autenticação."""

    return auth_service


def get_current_user(
    access_token: str | None = Cookie(
        default=None,
    ),
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    """Valida o JWT armazenado no cookie."""

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:

        payload = auth.decode_token(
            access_token
        )

    except jwt.ExpiredSignatureError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        ) from exc

    except jwt.InvalidTokenError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        ) from exc

    username = payload.get("sub")
    role = payload.get("role")

    if not username or not role:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    return {
        "username": username,
        "role": role,
    }