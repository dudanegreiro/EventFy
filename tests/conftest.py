import os
import re
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from eventfy_api.config import Settings, get_settings
from eventfy_api.main import app

ORGANIZER_EMAIL = "organizador.demo@eventfy.local"
PROVIDER_EMAIL = "prestador.demo@eventfy.local"
ADMIN_EMAIL = "admin.demo@eventfy.local"
DEMO_PASSWORD = "EventFyDemo123!"


def reset_test_database(database_url: str) -> None:
    migration_directory = Path(__file__).resolve().parents[1] / "db" / "migrations"
    migration_files = []
    for migration_file in migration_directory.glob("V*__*.sql"):
        match = re.match(r"^V(\d+)__.+\.sql$", migration_file.name)
        if match:
            migration_files.append((int(match.group(1)), migration_file))

    migration_files.sort(key=lambda item: item[0])
    if not migration_files:
        raise RuntimeError(
            "Nenhuma migracao encontrada para preparar o banco de testes."
        )

    with psycopg.connect(database_url) as connection:
        connection.execute("DROP SCHEMA public CASCADE")
        connection.execute("CREATE SCHEMA public")
        for _, migration_file in migration_files:
            connection.execute(migration_file.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def test_settings() -> Iterator[Settings]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Defina TEST_DATABASE_URL para executar os testes de integracao.")
    reset_test_database(database_url)
    try:
        yield Settings(
            url_do_banco=database_url,
            chave_secreta_jwt=SecretStr("test-only-secret-key-with-at-least-32-chars"),
        )
    finally:
        reset_test_database(database_url)


@pytest.fixture()
def client(test_settings: Settings) -> Iterator[TestClient]:
    app.dependency_overrides[get_settings] = lambda: test_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def service_availability(test_settings: Settings) -> None:
    with psycopg.connect(test_settings.url_do_banco) as connection:
        connection.execute(
            """
            INSERT INTO public.disponibilidade_servico (
                id_servico, data_inicio, data_fim, tipo, motivo
            )
            VALUES (
                1001,
                '2030-01-01 00:00:00+00',
                '2031-01-01 00:00:00+00',
                'DISPONIVEL',
                'Janela reservada para testes de integracao.'
            )
            """
        )


def access_token(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/auth/login",
        json={"email": email, "senha": DEMO_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def create_event(client: TestClient, token: str, name: str, day: int = 10) -> dict:
    response = client.post(
        "/api/eventos",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": name,
            "descricao": "Evento de teste.",
            "data_inicio": f"2030-06-{day:02d}T17:00:00Z",
            "data_fim": f"2030-06-{day:02d}T23:00:00Z",
            "local": "Palmas - TO",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()
