from uuid import uuid4

import jwt
import pytest
import psycopg
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from conftest import (
    ADMIN_EMAIL,
    ORGANIZER_EMAIL,
    PROVIDER_EMAIL,
    access_token,
    create_event,
)
from eventfy_api.config import Settings


def test_health_and_public_catalog(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}

    response = client.get("/api/servicos", params={"categoria": "alimentacao"})

    assert response.status_code == 200
    assert any(item["id_servico"] == 1001 for item in response.json())
    details = client.get("/api/servicos/1001")
    assert details.status_code == 200
    assert details.json()["arquivos"][0]["nome_original"] == "buffet-demonstracao.jpg"


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": ORGANIZER_EMAIL, "senha": "senha-incorreta"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_registration_hashes_password_limits_public_roles_and_logout_revokes_token(
    client: TestClient,
    test_settings: Settings,
) -> None:
    email = f"new.{uuid4().hex}@example.test"
    password = "SecureTestPassword123!"
    registered = client.post(
        "/api/auth/register",
        json={
            "nome": "Novo Organizador",
            "email": email.upper(),
            "senha": password,
            "tipo_usuario": "ORGANIZADOR",
        },
    )
    assert registered.status_code == 201, registered.text
    assert registered.json()["email"] == email
    assert "senha" not in registered.json()
    assert "senha_hash" not in registered.json()

    with psycopg.connect(
        test_settings.url_do_banco,
        row_factory=dict_row,
    ) as connection:
        credential = connection.execute(
            """
            SELECT senha_hash, senha_hash = crypt(%s, senha_hash) AS matches
            FROM public.usuario
            WHERE id_usuario = %s
            """,
            (password, registered.json()["id_usuario"]),
        ).fetchone()
    assert credential["senha_hash"] != password
    assert credential["senha_hash"].startswith("$2")
    assert credential["matches"] is True

    forbidden_role = client.post(
        "/api/auth/register",
        json={
            "nome": "Tentativa de Administrador",
            "email": f"admin.{uuid4().hex}@example.test",
            "senha": password,
            "tipo_usuario": "ADMINISTRADOR",
        },
    )
    assert forbidden_role.status_code == 422

    too_long_password = client.post(
        "/api/auth/register",
        json={
            "nome": "Senha muito longa",
            "email": f"long.{uuid4().hex}@example.test",
            "senha": "a" * 73,
            "tipo_usuario": "ORGANIZADOR",
        },
    )
    assert too_long_password.status_code == 422

    login = client.post(
        "/api/auth/login",
        json={"email": email, "senha": password},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    another_login = client.post(
        "/api/auth/login",
        json={"email": email, "senha": password},
    )
    assert another_login.status_code == 200

    logged_out = client.post("/api/auth/logout", headers=headers)
    assert logged_out.status_code == 204
    assert client.get("/api/eventos", headers=headers).status_code == 401
    assert client.get(
        "/api/eventos",
        headers={
            "Authorization": f"Bearer {another_login.json()['access_token']}"
        },
    ).status_code == 200


def test_inactive_user_cannot_login_or_use_an_existing_token(
    client: TestClient,
    test_settings: Settings,
) -> None:
    token = access_token(client, ORGANIZER_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        with psycopg.connect(test_settings.url_do_banco) as connection:
            connection.execute(
                "UPDATE public.usuario SET ativo = false WHERE email = %s",
                (ORGANIZER_EMAIL,),
            )

        assert client.get("/api/eventos", headers=headers).status_code == 401
        login = client.post(
            "/api/auth/login",
            json={"email": ORGANIZER_EMAIL, "senha": "EventFyDemo123!"},
        )
        assert login.status_code == 401
    finally:
        with psycopg.connect(test_settings.url_do_banco) as connection:
            connection.execute(
                "UPDATE public.usuario SET ativo = true WHERE email = %s",
                (ORGANIZER_EMAIL,),
            )


def test_authorization_enforces_roles_and_ignores_role_claim(
    client: TestClient,
    test_settings: Settings,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    admin_token = access_token(client, ADMIN_EMAIL)
    event_payload = {
        "nome": "Evento de autorizacao",
        "data_inicio": "2032-01-10T17:00:00Z",
        "data_fim": "2032-01-10T22:00:00Z",
        "local": "Palmas - TO",
    }

    assert client.post("/api/eventos", json=event_payload).status_code == 401
    assert client.post(
        "/api/eventos",
        headers={"Authorization": f"Bearer {provider_token}"},
        json=event_payload,
    ).status_code == 403
    assert client.post(
        "/api/eventos",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=event_payload,
    ).status_code == 403
    assert client.post(
        "/api/reservas/1001/analise",
        headers={"Authorization": f"Bearer {admin_token}"},
    ).status_code == 403
    assert client.post(
        "/api/reservas/1001/decisao",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"decisao": "APROVADA"},
    ).status_code == 403
    assert client.post(
        "/api/reservas/1001/confirmacao",
        headers={"Authorization": f"Bearer {admin_token}"},
    ).status_code == 403
    assert client.post(
        "/api/reservas/1001/analise",
        headers={"Authorization": f"Bearer {organizer_token}"},
    ).status_code == 403
    other_organizer = client.post(
        "/api/auth/register",
        json={
            "nome": "Outro Organizador",
            "email": f"other.{uuid4().hex}@example.test",
            "senha": "SecureTestPassword123!",
            "tipo_usuario": "ORGANIZADOR",
        },
    )
    assert other_organizer.status_code == 201
    other_login = client.post(
        "/api/auth/login",
        json={
            "email": other_organizer.json()["email"],
            "senha": "SecureTestPassword123!",
        },
    )
    assert other_login.status_code == 200
    other_token = other_login.json()["access_token"]
    assert client.get(
        "/api/reservas/1001",
        headers={"Authorization": f"Bearer {other_token}"},
    ).status_code == 403

    claims = jwt.decode(
        provider_token,
        test_settings.chave_secreta_jwt.get_secret_value(),
        algorithms=["HS256"],
    )
    claims["role"] = "ORGANIZADOR"
    forged_role_token = jwt.encode(
        claims,
        test_settings.chave_secreta_jwt.get_secret_value(),
        algorithm="HS256",
    )
    assert client.post(
        "/api/eventos",
        headers={"Authorization": f"Bearer {forged_role_token}"},
        json=event_payload,
    ).status_code == 403


def test_organizer_provider_flow_records_immutable_history(
    client: TestClient,
    service_availability: None,
    test_settings: Settings,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    event = create_event(client, organizer_token, "Fluxo completo")

    created = client.post(
        "/api/reservas",
        headers={"Authorization": f"Bearer {organizer_token}"},
        json={
            "id_evento": event["id_evento"],
            "id_servico": 1001,
            "data_inicio": "2030-06-10T18:00:00Z",
            "data_fim": "2030-06-10T21:00:00Z",
            "observacao": "Reserva para teste.",
        },
    )
    assert created.status_code == 201, created.text
    reservation_id = created.json()["id_reserva"]
    assert created.json()["status"] == "SOLICITADA"

    analyzed = client.post(
        f"/api/reservas/{reservation_id}/analise",
        headers={"Authorization": f"Bearer {provider_token}"},
    )
    assert analyzed.status_code == 200
    assert analyzed.json()["status"] == "EM_ANALISE"
    repeated_analysis = client.post(
        f"/api/reservas/{reservation_id}/analise",
        headers={"Authorization": f"Bearer {provider_token}"},
    )
    assert repeated_analysis.status_code == 409

    approved = client.post(
        f"/api/reservas/{reservation_id}/decisao",
        headers={"Authorization": f"Bearer {provider_token}"},
        json={"decisao": "APROVADA"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "APROVADA"

    confirmed = client.post(
        f"/api/reservas/{reservation_id}/confirmacao",
        headers={"Authorization": f"Bearer {organizer_token}"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "CONFIRMADA"

    history = client.get(
        f"/api/reservas/{reservation_id}/historico",
        headers={"Authorization": f"Bearer {organizer_token}"},
    )
    assert history.status_code == 200
    assert [entry["status_novo"] for entry in history.json()] == [
        "SOLICITADA",
        "EM_ANALISE",
        "APROVADA",
        "CONFIRMADA",
    ]
    assert history.json()[0]["autor_nome"] == "Organizador de Demonstracao"

    with pytest.raises(psycopg.errors.IntegrityConstraintViolation):
        with psycopg.connect(test_settings.url_do_banco) as connection:
            connection.execute(
                "DELETE FROM public.historico_reserva WHERE id_reserva = %s",
                (reservation_id,),
            )


def test_overlapping_active_reservation_returns_conflict(
    client: TestClient,
    service_availability: None,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    first_event = create_event(client, organizer_token, "Primeiro conflito", day=11)
    second_event = create_event(client, organizer_token, "Segundo conflito", day=11)
    headers = {"Authorization": f"Bearer {organizer_token}"}
    period = {
        "id_servico": 1001,
        "data_inicio": "2030-06-11T18:00:00Z",
        "data_fim": "2030-06-11T21:00:00Z",
    }

    first = client.post(
        "/api/reservas",
        headers=headers,
        json={"id_evento": first_event["id_evento"], **period},
    )
    second = client.post(
        "/api/reservas",
        headers=headers,
        json={"id_evento": second_event["id_evento"], **period},
    )

    assert first.status_code == 201, first.text
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "SCHEDULE_CONFLICT"


def test_rejection_requires_a_meaningful_reason(
    client: TestClient,
    service_availability: None,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    event = create_event(client, organizer_token, "Recusa justificada", day=12)
    headers = {"Authorization": f"Bearer {organizer_token}"}
    reservation = client.post(
        "/api/reservas",
        headers=headers,
        json={
            "id_evento": event["id_evento"],
            "id_servico": 1001,
            "data_inicio": "2030-06-12T18:00:00Z",
            "data_fim": "2030-06-12T21:00:00Z",
        },
    )
    assert reservation.status_code == 201, reservation.text
    reservation_id = reservation.json()["id_reserva"]

    analyzed = client.post(
        f"/api/reservas/{reservation_id}/analise",
        headers={"Authorization": f"Bearer {provider_token}"},
    )
    assert analyzed.status_code == 200

    rejected = client.post(
        f"/api/reservas/{reservation_id}/decisao",
        headers={"Authorization": f"Bearer {provider_token}"},
        json={"decisao": "RECUSADA", "motivo": "curto"},
    )
    assert rejected.status_code == 422
    assert rejected.json()["error"]["code"] == "VALIDATION_ERROR"


def test_admin_cannot_read_other_users_reservation(client: TestClient) -> None:
    admin_token = access_token(client, ADMIN_EMAIL)

    response = client.get(
        "/api/reservas/1001",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
