"""Logging estruturado sem dados pessoais e utilitarios de observabilidade."""

from __future__ import annotations

import json
import logging
import re
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

REQUEST_ID_CTX: ContextVar[str] = ContextVar("eventfy_request_id", default="-")
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_JWT_RE = re.compile(
    r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"
)
_DB_URL_CREDS_RE = re.compile(r"(postgres(?:ql)?://)([^:@/\s]+):([^@/\s]+)@")

_SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "chave_secreta_jwt",
        "cookie",
        "email",
        "nome",
        "password",
        "secret",
        "senha",
        "senha_hash",
        "set-cookie",
        "token",
        "url_do_banco",
    }
)

_EXTRA_FIELDS = (
    "event",
    "method",
    "path",
    "status_code",
    "duration_ms",
    "alert",
    "error_code",
    "error_type",
)


def sanitize_text(value: str) -> str:
    """Remove e-mails, tokens Bearer/JWT e credenciais em URLs de banco."""
    cleaned = _DB_URL_CREDS_RE.sub(r"\1[REDACTED]@", value)
    cleaned = _BEARER_RE.sub("Bearer [REDACTED]", cleaned)
    cleaned = _JWT_RE.sub("[REDACTED_JWT]", cleaned)
    cleaned = _EMAIL_RE.sub("[REDACTED_EMAIL]", cleaned)
    return cleaned


def normalize_request_id(header_value: str | None, fallback: str) -> str:
    """Aceita X-Request-ID seguro ou gera identificador novo."""
    if header_value and REQUEST_ID_PATTERN.match(header_value):
        return header_value
    return fallback


class StructuredJsonFormatter(logging.Formatter):
    """Formata registros de log como JSON estruturado livre de dados pessoais."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "component": record.name,
            "level": record.levelname,
            "request_id": getattr(record, "request_id", None) or REQUEST_ID_CTX.get(),
            "message": sanitize_text(record.getMessage()),
        }
        for field in _EXTRA_FIELDS:
            if field in _SENSITIVE_KEYS:
                continue
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = (
                    sanitize_text(value) if isinstance(value, str) else value
                )
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level_name: str = "INFO") -> logging.Logger:
    """Configura o logger raiz da aplicacao EventFy de forma idempotente."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger = logging.getLogger("eventfy")
    logger.setLevel(level)
    if not any(
        isinstance(handler.formatter, StructuredJsonFormatter)
        for handler in logger.handlers
    ):
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
    return logger


def log_critical_alert(
    logger: logging.Logger,
    *,
    event: str,
    message: str,
    error_type: str | None = None,
    error_code: str | None = None,
) -> None:
    """Registra evento critico verificavel com marcador explicito de alerta."""
    logger.critical(
        sanitize_text(message),
        extra={
            "event": event,
            "alert": True,
            "error_type": error_type,
            "error_code": error_code,
        },
    )
