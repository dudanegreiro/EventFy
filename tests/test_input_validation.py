from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from eventfy_api.schemas import EventCreate, ReservationCreate, ServiceCreate


def test_event_accepts_sql_looking_text_as_literal_data() -> None:
    payload = EventCreate(
        nome="x' OR 1=1 --",
        descricao="texto de teste",
        local="Palmas",
        data_inicio=datetime(2030, 1, 1, tzinfo=timezone.utc),
        data_fim=datetime(2030, 1, 2, tzinfo=timezone.utc),
    )

    assert payload.nome == "x' OR 1=1 --"


@pytest.mark.parametrize(
    "model,payload",
    [
        (
            EventCreate,
            {
                "nome": "evento",
                "local": "Palmas",
                "descricao": "x" * 4001,
                "data_inicio": "2030-01-01T00:00:00Z",
                "data_fim": "2030-01-02T00:00:00Z",
            },
        ),
        (
            ReservationCreate,
            {
                "id_evento": 1,
                "id_servico": 1,
                "observacao": "x" * 2001,
                "data_inicio": "2030-01-01T00:00:00Z",
                "data_fim": "2030-01-02T00:00:00Z",
            },
        ),
        (
            ServiceCreate,
            {
                "nome": "serviço",
                "categoria": "festa",
                "descricao": "x" * 4001,
                "preco": 1,
                "localizacao": "Palmas",
            },
        ),
    ],
)
def test_oversized_user_text_is_rejected(model, payload) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)
