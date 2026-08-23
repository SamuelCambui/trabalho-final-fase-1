"""Rotas de autenticação JWT."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.api.dependencies import get_auth_service, get_current_user
from src.api.schemas.login_config import (
    LoginRequest,
    TokenResponse,
    UserInfoResponse,
)
from src.api.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Autentica o usuário e armazena o JWT em cookie HttpOnly."""

    user = auth_service.authenticate(
        credentials.username,
        credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, expires_in = (
        auth_service.create_access_token(
            user["username"],
            user["role"],
        )
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=expires_in,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
    )


@router.post("/logout")
def logout(response: Response) -> dict:
    """Remove o cookie de autenticação."""

    response.delete_cookie(
        key="access_token",
    )

    return {
        "message": "Logout realizado com sucesso."
    }


@router.get(
    "/me",
    response_model=UserInfoResponse,
)
def get_me(
    current_user: dict = Depends(get_current_user),
) -> UserInfoResponse:
    """Retorna os dados do usuário autenticado."""

    return UserInfoResponse(
        username=current_user["username"],
        role=current_user["role"],
    )