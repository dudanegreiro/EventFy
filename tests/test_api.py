from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from time import perf_counter
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


def test_service_management_catalog_filters_and_file_lifecycle(
    client: TestClient,
    test_settings: Settings,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(test_settings, "local_dos_arquivos", tmp_path)
    provider_token = access_token(client, PROVIDER_EMAIL)
    headers = {"Authorization": f"Bearer {provider_token}"}
    created = client.post(
        "/api/servicos",
        headers=headers,
        json={
            "nome": "Fotografia de Eventos",
            "categoria": "Fotografia",
            "descricao": "Cobertura profissional para eventos.",
            "preco": "1200.00",
            "localizacao": "Palmas - TO",
        },
    )
    assert created.status_code == 201, created.text
    service_id = created.json()["id_servico"]

    other_provider_email = f"provider.{uuid4().hex}@example.test"
    other_provider = client.post(
        "/api/auth/register",
        json={
            "nome": "Outro Prestador",
            "email": other_provider_email,
            "senha": "SecureTestPassword123!",
            "tipo_usuario": "PRESTADOR",
        },
    )
    assert other_provider.status_code == 201
    other_provider_login = client.post(
        "/api/auth/login",
        json={
            "email": other_provider_email,
            "senha": "SecureTestPassword123!",
        },
    )
    assert other_provider_login.status_code == 200
    not_owner = client.patch(
        f"/api/servicos/{service_id}",
        headers={
            "Authorization": f"Bearer {other_provider_login.json()['access_token']}"
        },
        json={"nome": "Tentativa de outro titular"},
    )
    assert not_owner.status_code == 403

    updated = client.patch(
        f"/api/servicos/{service_id}",
        headers=headers,
        json={"descricao": "Cobertura fotografica completa."},
    )
    assert updated.status_code == 200
    assert updated.json()["descricao"] == "Cobertura fotografica completa."

    availability = client.post(
        f"/api/servicos/{service_id}/disponibilidades",
        headers=headers,
        json={
            "data_inicio": "2035-01-01T00:00:00Z",
            "data_fim": "2036-01-01T00:00:00Z",
            "tipo": "DISPONIVEL",
        },
    )
    assert availability.status_code == 201, availability.text
    own_periods = client.get(
        f"/api/servicos/{service_id}/disponibilidades",
        headers=headers,
    )
    assert own_periods.status_code == 200
    assert len(own_periods.json()) == 1

    filtered = client.get(
        "/api/servicos",
        params={
            "termo": "fotografia",
            "categoria": "Fotografia",
            "preco_minimo": 1000,
            "preco_maximo": 1500,
            "localizacao": "palmas",
            "data_inicio": "2035-05-01T12:00:00Z",
            "data_fim": "2035-05-01T18:00:00Z",
        },
    )
    assert filtered.status_code == 200
    assert [item["id_servico"] for item in filtered.json()] == [service_id]
    invalid_range = client.get(
        "/api/servicos",
        params={"preco_minimo": 2000, "preco_maximo": 1000},
    )
    assert invalid_range.status_code == 422
    incomplete_period = client.get(
        "/api/servicos",
        params={"data_inicio": "2035-05-01T12:00:00Z"},
    )
    assert incomplete_period.status_code == 422

    blocked = client.post(
        f"/api/servicos/{service_id}/disponibilidades",
        headers=headers,
        json={
            "data_inicio": "2035-05-01T14:00:00Z",
            "data_fim": "2035-05-01T15:00:00Z",
            "tipo": "BLOQUEIO_MANUAL",
            "motivo": "Indisponibilidade de demonstracao.",
        },
    )
    assert blocked.status_code == 201
    unavailable = client.get(
        "/api/servicos",
        params={
            "data_inicio": "2035-05-01T12:00:00Z",
            "data_fim": "2035-05-01T18:00:00Z",
        },
    )
    assert service_id not in {item["id_servico"] for item in unavailable.json()}

    upload = client.post(
        f"/api/servicos/{service_id}/arquivos",
        headers=headers,
        files={"file": ("portfolio.pdf", b"%PDF-1.7\nportfolio", "application/pdf")},
    )
    assert upload.status_code == 201, upload.text
    file_url = upload.json()["url"]
    assert client.get(file_url).content == b"%PDF-1.7\nportfolio"

    removed = client.delete(
        f"/api/servicos/{service_id}/arquivos/{upload.json()['id_arquivo']}",
        headers=headers,
    )
    assert removed.status_code == 204
    assert client.get(file_url).status_code == 404

    deactivated = client.delete(f"/api/servicos/{service_id}", headers=headers)
    assert deactivated.status_code == 204
    assert client.get(f"/api/servicos/{service_id}").status_code == 404
    assert service_id not in {
        item["id_servico"] for item in client.get("/api/servicos").json()
    }


def test_service_edits_respect_ownership_and_active_reservations(
    client: TestClient,
) -> None:
    provider_token = access_token(client, PROVIDER_EMAIL)
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    service_url = "/api/servicos/1001"

    descriptive_edit = client.patch(
        service_url,
        headers={"Authorization": f"Bearer {provider_token}"},
        json={"nome": "Buffet de demonstracao atualizado"},
    )
    assert descriptive_edit.status_code == 200

    price_edit = client.patch(
        service_url,
        headers={"Authorization": f"Bearer {provider_token}"},
        json={"preco": 3000},
    )
    assert price_edit.status_code == 409

    deactivate = client.delete(
        service_url,
        headers={"Authorization": f"Bearer {provider_token}"},
    )
    assert deactivate.status_code == 409

    availability_edit = client.post(
        f"{service_url}/disponibilidades",
        headers={"Authorization": f"Bearer {provider_token}"},
        json={
            "data_inicio": "2035-01-01T00:00:00Z",
            "data_fim": "2036-01-01T00:00:00Z",
            "tipo": "DISPONIVEL",
        },
    )
    assert availability_edit.status_code == 409

    attachment_edit = client.delete(
        f"{service_url}/arquivos/1001",
        headers={"Authorization": f"Bearer {provider_token}"},
    )
    assert attachment_edit.status_code == 409

    denied = client.patch(
        service_url,
        headers={"Authorization": f"Bearer {organizer_token}"},
        json={"nome": "Alteracao indevida"},
    )
    assert denied.status_code == 403


def test_catalog_returns_200_services_within_rnf03(
    client: TestClient,
    test_settings: Settings,
) -> None:
    with psycopg.connect(test_settings.url_do_banco) as connection:
        connection.execute(
            """
            INSERT INTO public.servico (
                id_prestador, nome, categoria, descricao, preco, localizacao
            )
            SELECT 1002, 'Servico de carga ' || n, 'Carga', 'Teste de desempenho',
                   100 + n, 'Palmas - TO'
            FROM generate_series(1, 200) AS n
            """
        )

    durations = []
    for _ in range(3):
        started = perf_counter()
        response = client.get(
            "/api/servicos",
            params={"categoria": "Carga", "limit": 100},
        )
        durations.append(perf_counter() - started)
        assert response.status_code == 200
        assert len(response.json()) == 100

    second_page = client.get(
        "/api/servicos",
        params={"categoria": "Carga", "limit": 100, "offset": 100},
    )
    assert second_page.status_code == 200
    assert len(second_page.json()) == 100
    assert max(durations) < 3.0


def test_file_upload_rejects_mime_mismatch_and_oversized_content(
    client: TestClient,
    test_settings: Settings,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(test_settings, "local_dos_arquivos", tmp_path)
    provider_token = access_token(client, PROVIDER_EMAIL)
    headers = {"Authorization": f"Bearer {provider_token}"}
    service = client.post(
        "/api/servicos",
        headers=headers,
        json={
            "nome": "Servico para anexos invalidos",
            "categoria": "Teste",
            "preco": "50",
            "localizacao": "Palmas - TO",
        },
    )
    assert service.status_code == 201
    service_id = service.json()["id_servico"]

    wrong_mime = client.post(
        f"/api/servicos/{service_id}/arquivos",
        headers=headers,
        files={"file": ("imagem.png", b"%PDF-1.7\n", "image/png")},
    )
    assert wrong_mime.status_code == 415

    oversized = client.post(
        f"/api/servicos/{service_id}/arquivos",
        headers=headers,
        files={
            "file": (
                "grande.pdf",
                b"%PDF-1.7\n" + b"x" * 10_000_000,
                "application/pdf",
            )
        },
    )
    assert oversized.status_code == 413
    assert list(tmp_path.iterdir()) == []


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
    assert (
        client.get(
            "/api/eventos",
            headers={"Authorization": f"Bearer {another_login.json()['access_token']}"},
        ).status_code
        == 200
    )


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
    assert (
        client.post(
            "/api/eventos",
            headers={"Authorization": f"Bearer {provider_token}"},
            json=event_payload,
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/eventos",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=event_payload,
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/reservas/1001/analise",
            headers={"Authorization": f"Bearer {admin_token}"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/reservas/1001/decisao",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"decisao": "APROVADA"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/reservas/1001/confirmacao",
            headers={"Authorization": f"Bearer {admin_token}"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/reservas/1001/analise",
            headers={"Authorization": f"Bearer {organizer_token}"},
        ).status_code
        == 403
    )
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
    assert (
        client.get(
            "/api/reservas/1001",
            headers={"Authorization": f"Bearer {other_token}"},
        ).status_code
        == 403
    )

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
    assert (
        client.post(
            "/api/eventos",
            headers={"Authorization": f"Bearer {forged_role_token}"},
            json=event_payload,
        ).status_code
        == 403
    )


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


def test_organizer_cancels_approved_reservation_and_releases_schedule(
    client: TestClient,
    service_availability: None,
    test_settings: Settings,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    event = create_event(client, organizer_token, "Cancelamento aprovado", day=13)
    headers = {"Authorization": f"Bearer {organizer_token}"}
    created = client.post(
        "/api/reservas",
        headers=headers,
        json={
            "id_evento": event["id_evento"],
            "id_servico": 1001,
            "data_inicio": "2030-06-13T18:00:00Z",
            "data_fim": "2030-06-13T21:00:00Z",
        },
    )
    assert created.status_code == 201, created.text
    reservation_id = created.json()["id_reserva"]
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    requested_cancel = client.post(
        f"/api/reservas/{reservation_id}/cancelamento",
        headers=provider_headers,
        json={"motivo": "Prestador sem permissao."},
    )
    assert requested_cancel.status_code == 409
    assert (
        client.post(
            f"/api/reservas/{reservation_id}/analise",
            headers=provider_headers,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/reservas/{reservation_id}/decisao",
            headers=provider_headers,
            json={"decisao": "APROVADA"},
        ).status_code
        == 200
    )

    forbidden_cancel = client.post(
        f"/api/reservas/{reservation_id}/cancelamento",
        headers=provider_headers,
        json={"motivo": "Nao posso cancelar antes da confirmacao."},
    )
    assert forbidden_cancel.status_code == 409
    missing_reason = client.post(
        f"/api/reservas/{reservation_id}/cancelamento",
        headers=headers,
        json={},
    )
    assert missing_reason.status_code == 422
    short_reason = client.post(
        f"/api/reservas/{reservation_id}/cancelamento",
        headers=headers,
        json={"motivo": "Curto"},
    )
    assert short_reason.status_code == 422
    invalid_reason = client.post(
        f"/api/reservas/{reservation_id}/cancelamento",
        headers=headers,
        json={"motivo": "  "},
    )
    assert invalid_reason.status_code == 422

    cancelled = client.post(
        f"/api/reservas/{reservation_id}/cancelamento",
        headers=headers,
        json={"motivo": "O evento foi adiado pelo organizador."},
    )
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "CANCELADA"
    with psycopg.connect(
        test_settings.url_do_banco, row_factory=dict_row
    ) as connection:
        block = connection.execute(
            """
            SELECT ativo
            FROM public.disponibilidade_servico
            WHERE id_reserva = %s
            """,
            (reservation_id,),
        ).fetchone()
        history = connection.execute(
            """
            SELECT status_anterior, status_novo, motivo
            FROM public.historico_reserva
            WHERE id_reserva = %s
            ORDER BY id_historico DESC
            LIMIT 1
            """,
            (reservation_id,),
        ).fetchone()
    assert block["ativo"] is False
    assert history == {
        "status_anterior": "APROVADA",
        "status_novo": "CANCELADA",
        "motivo": "O evento foi adiado pelo organizador.",
    }


def test_confirmed_reservation_can_be_cancelled_by_provider(
    client: TestClient,
    service_availability: None,
    test_settings: Settings,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    organizer_headers = {"Authorization": f"Bearer {organizer_token}"}
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    event = create_event(client, organizer_token, "Cancelamento confirmado", day=14)
    created = client.post(
        "/api/reservas",
        headers=organizer_headers,
        json={
            "id_evento": event["id_evento"],
            "id_servico": 1001,
            "data_inicio": "2030-06-14T18:00:00Z",
            "data_fim": "2030-06-14T21:00:00Z",
        },
    )
    assert created.status_code == 201, created.text
    reservation_id = created.json()["id_reserva"]
    assert (
        client.post(
            f"/api/reservas/{reservation_id}/analise",
            headers=provider_headers,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/reservas/{reservation_id}/decisao",
            headers=provider_headers,
            json={"decisao": "APROVADA"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/reservas/{reservation_id}/confirmacao",
            headers=organizer_headers,
        ).status_code
        == 200
    )

    cancelled = client.post(
        f"/api/reservas/{reservation_id}/cancelamento",
        headers=provider_headers,
        json={"motivo": "O prestador teve uma emergencia."},
    )

    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "CANCELADA"
    with psycopg.connect(
        test_settings.url_do_banco, row_factory=dict_row
    ) as connection:
        schedule_block = connection.execute(
            """
            SELECT ativo
            FROM public.disponibilidade_servico
            WHERE id_reserva = %s
            """,
            (reservation_id,),
        ).fetchone()
        history = connection.execute(
            """
            SELECT h.status_anterior, h.status_novo, h.motivo, u.email
            FROM public.historico_reserva AS h
            JOIN public.usuario AS u ON u.id_usuario = h.id_usuario
            WHERE h.id_reserva = %s
            ORDER BY h.id_historico DESC
            LIMIT 1
            """,
            (reservation_id,),
        ).fetchone()

    assert schedule_block == {"ativo": False}
    assert history == {
        "status_anterior": "CONFIRMADA",
        "status_novo": "CANCELADA",
        "motivo": "O prestador teve uma emergencia.",
        "email": PROVIDER_EMAIL,
    }


def test_cancellation_after_event_start_is_rejected(
    client: TestClient,
    service_availability: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    organizer_headers = {"Authorization": f"Bearer {organizer_token}"}
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    event = create_event(client, organizer_token, "Cancelamento fora do prazo", day=15)
    created = client.post(
        "/api/reservas",
        headers=organizer_headers,
        json={
            "id_evento": event["id_evento"],
            "id_servico": 1001,
            "data_inicio": "2030-06-15T18:00:00Z",
            "data_fim": "2030-06-15T21:00:00Z",
        },
    )
    assert created.status_code == 201, created.text
    reservation_id = created.json()["id_reserva"]
    assert client.post(
        f"/api/reservas/{reservation_id}/analise",
        headers=provider_headers,
    ).status_code == 200
    assert client.post(
        f"/api/reservas/{reservation_id}/decisao",
        headers=provider_headers,
        json={"decisao": "APROVADA"},
    ).status_code == 200
    assert client.post(
        f"/api/reservas/{reservation_id}/confirmacao",
        headers=organizer_headers,
    ).status_code == 200

    real_datetime = datetime

    class AfterEventDateTime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return real_datetime.now(tz) + timedelta(days=2000)

    monkeypatch.setattr("eventfy_api.main.datetime", AfterEventDateTime)
    cancelled = client.post(
        f"/api/reservas/{reservation_id}/cancelamento",
        headers=organizer_headers,
        json={"motivo": "Cancelamento depois do inicio do evento."},
    )

    assert cancelled.status_code == 409
    assert cancelled.json()["error"]["code"] == "CANCELLATION_WINDOW_CLOSED"


def test_expiration_job_expires_each_unanswered_stage(
    client: TestClient,
    service_availability: None,
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    organizer_headers = {"Authorization": f"Bearer {organizer_token}"}
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    reservation_ids = []

    for day, final_stage in ((17, "SOLICITADA"), (18, "EM_ANALISE"), (19, "APROVADA")):
        event = create_event(client, organizer_token, f"Expiracao {day}", day=day)
        created = client.post(
            "/api/reservas",
            headers=organizer_headers,
            json={
                "id_evento": event["id_evento"],
                "id_servico": 1001,
                "data_inicio": f"2030-06-{day:02d}T18:00:00Z",
                "data_fim": f"2030-06-{day:02d}T21:00:00Z",
            },
        )
        assert created.status_code == 201, created.text
        reservation_id = created.json()["id_reserva"]
        reservation_ids.append(reservation_id)
        if final_stage in {"EM_ANALISE", "APROVADA"}:
            assert (
                client.post(
                    f"/api/reservas/{reservation_id}/analise",
                    headers=provider_headers,
                ).status_code
                == 200
            )
        if final_stage == "APROVADA":
            assert (
                client.post(
                    f"/api/reservas/{reservation_id}/decisao",
                    headers=provider_headers,
                    json={"decisao": "APROVADA"},
                ).status_code
                == 200
            )

    admin_headers = {"Authorization": f"Bearer {access_token(client, ADMIN_EMAIL)}"}
    real_datetime = datetime

    class FutureDateTime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return real_datetime.now(tz) + timedelta(hours=49)

    monkeypatch.setattr("eventfy_api.main.datetime", FutureDateTime)
    lazy_expired = client.get(
        f"/api/reservas/{reservation_ids[0]}",
        headers=organizer_headers,
    )
    assert lazy_expired.status_code == 200
    assert lazy_expired.json()["status"] == "EXPIRADA"
    unauthorized = client.post("/api/jobs/reservas/expiracoes")
    assert unauthorized.status_code == 401
    expired = client.post(
        "/api/jobs/reservas/expiracoes",
        headers=admin_headers,
    )

    assert expired.status_code == 200, expired.text
    assert expired.json()["quantidade"] == len(expired.json()["reservas_expiradas"])
    assert set(reservation_ids[1:]).issubset(expired.json()["reservas_expiradas"])
    for reservation_id in reservation_ids:
        reservation = client.get(
            f"/api/reservas/{reservation_id}",
            headers=organizer_headers,
        )
        assert reservation.status_code == 200
        assert reservation.json()["status"] == "EXPIRADA"
        history = client.get(
            f"/api/reservas/{reservation_id}/historico",
            headers=organizer_headers,
        )
        assert history.status_code == 200
        assert history.json()[-1]["status_novo"] == "EXPIRADA"
        assert history.json()[-1]["id_usuario"] is None
    with psycopg.connect(
        test_settings.url_do_banco, row_factory=dict_row
    ) as connection:
        schedule_block = connection.execute(
            """
            SELECT ativo
            FROM public.disponibilidade_servico
            WHERE id_reserva = %s
            """,
            (reservation_ids[-1],),
        ).fetchone()
    assert schedule_block["ativo"] is False


def test_concurrent_confirmation_records_only_one_transition(
    client: TestClient,
    service_availability: None,
    test_settings: Settings,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    organizer_headers = {"Authorization": f"Bearer {organizer_token}"}
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    event = create_event(client, organizer_token, "Confirmacao concorrente", day=23)
    created = client.post(
        "/api/reservas",
        headers=organizer_headers,
        json={
            "id_evento": event["id_evento"],
            "id_servico": 1001,
            "data_inicio": "2030-06-23T18:00:00Z",
            "data_fim": "2030-06-23T21:00:00Z",
        },
    )
    assert created.status_code == 201, created.text
    reservation_id = created.json()["id_reserva"]
    assert (
        client.post(
            f"/api/reservas/{reservation_id}/analise",
            headers=provider_headers,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/reservas/{reservation_id}/decisao",
            headers=provider_headers,
            json={"decisao": "APROVADA"},
        ).status_code
        == 200
    )

    barrier = Barrier(2)

    def confirm() -> int:
        barrier.wait()
        response = client.post(
            f"/api/reservas/{reservation_id}/confirmacao",
            headers=organizer_headers,
        )
        return response.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(lambda _: confirm(), range(2)))

    assert sorted(statuses) == [200, 409]
    with psycopg.connect(test_settings.url_do_banco) as connection:
        confirmed_transitions = connection.execute(
            """
            SELECT count(*)
            FROM public.historico_reserva
            WHERE id_reserva = %s AND status_novo = 'CONFIRMADA'
            """,
            (reservation_id,),
        ).fetchone()[0]
    assert confirmed_transitions == 1


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


def test_reservation_queue_and_detail_align_expiration_before_job(
    client: TestClient,
    service_availability: None,
    test_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    organizer_token = access_token(client, ORGANIZER_EMAIL)
    provider_token = access_token(client, PROVIDER_EMAIL)
    organizer_headers = {"Authorization": f"Bearer {organizer_token}"}
    provider_headers = {"Authorization": f"Bearer {provider_token}"}

    requested_event = create_event(
        client, organizer_token, "Fila vencida solicitada", day=24
    )
    requested = client.post(
        "/api/reservas",
        headers=organizer_headers,
        json={
            "id_evento": requested_event["id_evento"],
            "id_servico": 1001,
            "data_inicio": "2030-06-24T18:00:00Z",
            "data_fim": "2030-06-24T21:00:00Z",
        },
    )
    assert requested.status_code == 201, requested.text
    requested_id = requested.json()["id_reserva"]

    approved_event = create_event(
        client, organizer_token, "Fila vencida aprovada", day=25
    )
    approved = client.post(
        "/api/reservas",
        headers=organizer_headers,
        json={
            "id_evento": approved_event["id_evento"],
            "id_servico": 1001,
            "data_inicio": "2030-06-25T18:00:00Z",
            "data_fim": "2030-06-25T21:00:00Z",
        },
    )
    assert approved.status_code == 201, approved.text
    approved_id = approved.json()["id_reserva"]
    assert (
        client.post(
            f"/api/reservas/{approved_id}/analise",
            headers=provider_headers,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/reservas/{approved_id}/decisao",
            headers=provider_headers,
            json={"decisao": "APROVADA"},
        ).status_code
        == 200
    )

    real_datetime = datetime

    class FutureDateTime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return real_datetime.now(tz) + timedelta(hours=49)

    monkeypatch.setattr("eventfy_api.main.datetime", FutureDateTime)

    provider_queue = client.get("/api/reservas", headers=provider_headers)
    assert provider_queue.status_code == 200, provider_queue.text
    provider_statuses = {
        item["id_reserva"]: item["status"] for item in provider_queue.json()
    }
    assert provider_statuses[requested_id] == "EXPIRADA"
    assert provider_statuses[approved_id] == "EXPIRADA"

    organizer_queue = client.get("/api/reservas", headers=organizer_headers)
    assert organizer_queue.status_code == 200, organizer_queue.text
    organizer_statuses = {
        item["id_reserva"]: item["status"] for item in organizer_queue.json()
    }
    assert organizer_statuses[requested_id] == "EXPIRADA"
    assert organizer_statuses[approved_id] == "EXPIRADA"

    for reservation_id in (requested_id, approved_id):
        detail = client.get(
            f"/api/reservas/{reservation_id}",
            headers=provider_headers,
        )
        assert detail.status_code == 200
        assert detail.json()["status"] == "EXPIRADA"

    blocked_analysis = client.post(
        f"/api/reservas/{requested_id}/analise",
        headers=provider_headers,
    )
    assert blocked_analysis.status_code == 409
    assert blocked_analysis.json()["error"]["code"] == "RESERVATION_EXPIRED"

    blocked_confirmation = client.post(
        f"/api/reservas/{approved_id}/confirmacao",
        headers=organizer_headers,
    )
    assert blocked_confirmation.status_code == 409
    assert blocked_confirmation.json()["error"]["code"] == "RESERVATION_EXPIRED"

    admin_headers = {"Authorization": f"Bearer {access_token(client, ADMIN_EMAIL)}"}
    job_response = client.post(
        "/api/jobs/reservas/expiracoes",
        headers=admin_headers,
    )
    assert job_response.status_code == 200
    assert requested_id not in job_response.json()["reservas_expiradas"]
    assert approved_id not in job_response.json()["reservas_expiradas"]

    with psycopg.connect(
        test_settings.url_do_banco, row_factory=dict_row
    ) as connection:
        schedule_block = connection.execute(
            """
            SELECT ativo
            FROM public.disponibilidade_servico
            WHERE id_reserva = %s
            """,
            (approved_id,),
        ).fetchone()
        expired_counts = connection.execute(
            """
            SELECT id_reserva, count(*) AS total
            FROM public.historico_reserva
            WHERE id_reserva = ANY(%s) AND status_novo = 'EXPIRADA'
            GROUP BY id_reserva
            """,
            ([requested_id, approved_id],),
        ).fetchall()
    assert schedule_block["ativo"] is False
    assert {row["id_reserva"]: row["total"] for row in expired_counts} == {
        requested_id: 1,
        approved_id: 1,
    }
