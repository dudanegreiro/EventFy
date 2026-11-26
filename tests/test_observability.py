import json
import logging

import psycopg
import pytest
from fastapi.testclient import TestClient

from conftest import DEMO_PASSWORD, ORGANIZER_EMAIL
from eventfy_api.config import Settings
from eventfy_api.observability import (
    StructuredJsonFormatter,
    normalize_request_id,
    sanitize_text,
)


def test_sanitize_text_redacts_pii_and_credentials() -> None:
    raw = (
        "Falha para maria.silva@example.com usando "
        "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.assinatura123 "
        "em postgresql://eventfy_dev:SuperSenha99@db.internal:5432/eventfy"
    )
    cleaned = sanitize_text(raw)

    assert "maria.silva@example.com" not in cleaned
    assert "SuperSenha99" not in cleaned
    assert "eyJhbGciOiJIUzI1NiJ9" not in cleaned
    assert "[REDACTED_EMAIL]" in cleaned
    assert "Bearer [REDACTED]" in cleaned
    assert "postgresql://[REDACTED]@db.internal:5432/eventfy" in cleaned


def test_structured_formatter_includes_required_fields_without_pii() -> None:
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="eventfy.http",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="Erro ao autenticar usuario.real@example.com",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-demo-001"
    record.event = "auth_failure"
    record.alert = True

    parsed = json.loads(formatter.format(record))

    assert parsed["timestamp"]
    assert parsed["component"] == "eventfy.http"
    assert parsed["level"] == "ERROR"
    assert parsed["request_id"] == "req-demo-001"
    assert parsed["alert"] is True
    assert "usuario.real@example.com" not in parsed["message"]


def test_normalize_request_id_rejects_unsafe_values() -> None:
    assert normalize_request_id("req-123_abc.45", "fallback") == "req-123_abc.45"
    assert normalize_request_id("bad\nheader", "fallback") == "fallback"
    assert normalize_request_id(None, "fallback") == "fallback"


def test_health_returns_status_version_and_request_id(
    client: TestClient,
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(test_settings, "versao_app", "1.0.0")
    monkeypatch.setattr(test_settings, "ambiente", "producao")

    response = client.get("/api/health", headers={"X-Request-ID": "demo-health-1"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "demo-health-1"
    assert response.json() == {
        "status": "ok",
        "version": "1.0.0",
        "environment": "producao",
        "database": "ok",
    }


def test_health_degrades_with_critical_alert_when_database_fails(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fail_connect(*_args, **_kwargs):
        raise psycopg.OperationalError(
            "connection failed to postgresql://user:SenhaSecreta@127.0.0.1:5432/db"
        )

    monkeypatch.setattr(psycopg, "connect", fail_connect)

    with caplog.at_level(logging.INFO, logger="eventfy"):
        response = client.get("/api/health", headers={"X-Request-ID": "health-down-1"})

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "unavailable"
    assert body["version"]

    formatter = StructuredJsonFormatter()
    formatted = [json.loads(formatter.format(rec)) for rec in caplog.records]
    alerts = [entry for entry in formatted if entry.get("alert") is True]
    assert alerts
    assert any(entry["level"] == "CRITICAL" for entry in alerts)
    assert all("SenhaSecreta" not in json.dumps(entry) for entry in formatted)


def test_login_logs_never_expose_email_password_or_token(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="eventfy"):
        response = client.post(
            "/api/auth/login",
            json={"email": ORGANIZER_EMAIL, "senha": DEMO_PASSWORD},
            headers={"X-Request-ID": "login-safe-1"},
        )

    assert response.status_code == 200
    token = response.json()["access_token"]

    formatter = StructuredJsonFormatter()
    serialized = "\n".join(formatter.format(rec) for rec in caplog.records)

    assert "login-safe-1" in serialized
    assert "/api/auth/login" in serialized
    assert ORGANIZER_EMAIL not in serialized
    assert DEMO_PASSWORD not in serialized
    assert token not in serialized
