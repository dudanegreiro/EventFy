from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
import psycopg
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from eventfy_api.config import Settings, get_settings
from eventfy_api.database import get_connection
from eventfy_api.errors import ApiError

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    user_id: int,
    role: str,
    token_id: UUID,
    settings: Settings,
) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "jti": str(token_id),
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
            options={"require": ["sub", "jti", "iat", "exp"]},
        )
        user_id = int(claims["sub"])
        token_id = UUID(claims["jti"])
    except (InvalidTokenError, KeyError, TypeError, ValueError, AttributeError):
        raise unauthorized from None

    user = connection.execute(
        """
        SELECT u.id_usuario, u.nome, u.email, u.tipo_usuario
        FROM public.usuario AS u
        JOIN public.sessao_autenticacao AS s
          ON s.id_usuario = u.id_usuario
        WHERE u.id_usuario = %s
          AND u.ativo
          AND s.token_id = %s
          AND s.expira_em > now()
          AND s.revogada_em IS NULL
        """,
        (user_id, token_id),
    ).fetchone()
    if user is None:
        raise unauthorized
    return {**user, "_token_id": token_id}


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
