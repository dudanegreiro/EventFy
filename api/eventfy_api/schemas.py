from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def require_timezone(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("A data e hora devem incluir o fuso horario.")
    return value


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    senha: str = Field(min_length=1, max_length=200)

    @field_validator("email")
    @classmethod
    def validate_email_shape(cls, value: str) -> str:
        normalized = value.strip()
        if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
            raise ValueError("Informe um e-mail valido.")
        return normalized


class UserRegistrationRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    senha: str = Field(min_length=12, max_length=72)
    tipo_usuario: Literal["ORGANIZADOR", "PRESTADOR"]

    @field_validator("nome")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("O nome nao pode ficar vazio.")
        return normalized

    @field_validator("senha")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("A senha deve ter no maximo 72 bytes em UTF-8.")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
            raise ValueError("Informe um e-mail valido.")
        return normalized


class UserResponse(BaseModel):
    id_usuario: int
    nome: str
    email: str
    tipo_usuario: Literal["ORGANIZADOR", "PRESTADOR", "ADMINISTRADOR"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class PeriodModel(BaseModel):
    data_inicio: datetime
    data_fim: datetime

    @field_validator("data_inicio", "data_fim")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        return require_timezone(value)

    @model_validator(mode="after")
    def validate_period(self) -> "PeriodModel":
        if self.data_fim <= self.data_inicio:
            raise ValueError("data_fim deve ser posterior a data_inicio.")
        return self


class EventCreate(PeriodModel):
    nome: str = Field(min_length=1, max_length=160)
    descricao: str | None = None
    local: str = Field(min_length=1, max_length=200)

    @field_validator("nome", "local")
    @classmethod
    def validate_nonblank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("O campo nao pode ficar vazio.")
        return normalized


class ReservationCreate(PeriodModel):
    id_evento: int = Field(gt=0)
    id_servico: int = Field(gt=0)
    observacao: str | None = None


class ReservationDecision(BaseModel):
    decisao: Literal["APROVADA", "RECUSADA"]
    motivo: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_rejection_reason(self) -> "ReservationDecision":
        if self.decisao == "RECUSADA" and len((self.motivo or "").strip()) < 10:
            raise ValueError(
                "A justificativa de recusa deve ter pelo menos 10 caracteres."
            )
        return self


class ReservationCancellation(BaseModel):
    motivo: str = Field(min_length=1, max_length=2000)

    @field_validator("motivo")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("A justificativa do cancelamento e obrigatoria.")
        return normalized


class PublicService(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_servico: int
    nome: str
    categoria: str
    descricao: str | None
    preco: Decimal
    id_prestador: int
    localizacao: str | None = None
    ativo: bool = True
    arquivos: list["ServiceFile"] = Field(default_factory=list)
    disponibilidades: list["AvailablePeriod"] = Field(default_factory=list)


class ServiceCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=160)
    categoria: str = Field(min_length=1, max_length=80)
    descricao: str | None = None
    preco: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    localizacao: str = Field(min_length=1, max_length=200)

    @field_validator("nome", "categoria", "localizacao")
    @classmethod
    def validate_service_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("O campo nao pode ficar vazio.")
        return normalized


class ServiceUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=160)
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    descricao: str | None = None
    preco: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    localizacao: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("nome", "categoria", "localizacao")
    @classmethod
    def validate_service_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("O campo nao pode ficar vazio.")
        return normalized

    @model_validator(mode="after")
    def validate_changes(self) -> "ServiceUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualizar.")
        for field in ("nome", "categoria", "preco", "localizacao"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"O campo {field} nao pode ser nulo.")
        return self


class AvailabilityCreate(PeriodModel):
    tipo: Literal["DISPONIVEL", "BLOQUEIO_MANUAL"]
    motivo: str | None = Field(default=None, max_length=500)


class ServiceFile(BaseModel):
    id_arquivo: int
    nome_original: str
    url: str
    tipo_mime: str
    tamanho: int


class AvailablePeriod(BaseModel):
    data_inicio: datetime
    data_fim: datetime


class EventResponse(BaseModel):
    id_evento: int
    id_organizador: int | None = None
    nome: str
    descricao: str | None
    data_inicio: datetime
    data_fim: datetime
    local: str
    criado_em: datetime | None = None


class ReservationResponse(BaseModel):
    id_reserva: int
    id_evento: int
    id_servico: int
    id_solicitante: int
    status: Literal[
        "SOLICITADA",
        "EM_ANALISE",
        "APROVADA",
        "CONFIRMADA",
        "RECUSADA",
        "CANCELADA",
        "EXPIRADA",
        "FINALIZADA",
    ]
    data_inicio: datetime
    data_fim: datetime
    observacao: str | None = None
    motivo_recusa: str | None = None
    criado_em: datetime


class TransitionResponse(BaseModel):
    id_reserva: int
    status: Literal["EM_ANALISE", "CONFIRMADA"]


class CancellationResponse(BaseModel):
    id_reserva: int
    status: Literal["CANCELADA"]
    motivo: str


class ExpirationResponse(BaseModel):
    quantidade: int
    reservas_expiradas: list[int]


class DecisionResponse(BaseModel):
    id_reserva: int
    status: Literal["APROVADA", "RECUSADA"]
    motivo: str | None = None


class ReservationHistoryEntry(BaseModel):
    id_historico: int
    id_reserva: int
    id_usuario: int | None
    status_anterior: str | None
    status_novo: str
    data_hora: datetime
    observacao: str | None
    motivo: str | None
    autor_nome: str
    autor_perfil: str | None
