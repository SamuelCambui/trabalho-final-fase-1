"""Schemas de autenticação e resposta do token JWT."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credenciais enviadas no endpoint de login."""

    username: str = Field(min_length=1, examples=["admin"])
    password: str = Field(min_length=1, examples=["admin"])


class TokenResponse(BaseModel):
    """Token JWT retornado após autenticação bem-sucedida."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Tempo de expiração do token em segundos.")


class UserInfoResponse(BaseModel):
    """Dados básicos do usuário autenticado."""

    username: str
    role: str
