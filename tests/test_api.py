import pytest
import psycopg
from fastapi.testclient import TestClient

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
