"""Serviço de autenticação JWT."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from src.api.config import (
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
    JWT_SECRET_KEY,
    USERS_DB,
)


class AuthService:
    """Valida credenciais e gerencia tokens JWT."""

    def authenticate(self, username: str, password: str) -> dict | None:
        """
        Verifica usuário e senha no banco local de credenciais.

        Returns:
            Dicionário com ``role`` se válido; ``None`` se inválido.
        """
        user = USERS_DB.get(username)
        if user is None or user["password"] != password:
            return None
        return {"username": username, "role": user["role"]}

    def create_access_token(self, username: str, role: str) -> tuple[str, int]:
        """
        Gera um token JWT assinado.

        Returns:
            Tupla ``(token, expires_in_seconds)``.
        """
        expires_in = JWT_EXPIRE_MINUTES * 60
        expire_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
        payload = {
            "sub": username,
            "role": role,
            "exp": expire_at,
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token, expires_in

    def decode_token(self, token: str) -> dict:
        """
        Decodifica e valida um token JWT.

        Raises:
            jwt.ExpiredSignatureError: Token expirado.
            jwt.InvalidTokenError: Token inválido ou adulterado.
        """
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
