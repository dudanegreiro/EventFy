from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import psycopg
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from eventfy_api.config import Settings, get_settings
from eventfy_api.database import get_connection
from eventfy_api.errors import ApiError

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(user_id: int, role: str, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "iat": now,
            "exp": now + timedelta(minutes=settings.duracao_token_minutos),
        },
        settings.chave_secreta_jwt.get_secret_value(),
        algorithm="HS256",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    unauthorized = ApiError(
        401,
        "UNAUTHENTICATED",
        "E necessario autenticar-se para acessar este recurso.",
        {"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.chave_secreta_jwt.get_secret_value(),
            algorithms=["HS256"],
        )
        user_id = int(claims["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized from None

    user = connection.execute(
        """
        SELECT id_usuario, nome, email, tipo_usuario
        FROM public.usuario
        WHERE id_usuario = %s AND ativo
        """,
        (user_id,),
    ).fetchone()
    if user is None:
        raise unauthorized
    return user


def require_role(*roles: str):
    def dependency(
        user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        if user["tipo_usuario"] not in roles:
            raise ApiError(
                403,
                "FORBIDDEN",
                "Seu perfil nao tem permissao para esta operacao.",
            )
        return user

    return dependency
