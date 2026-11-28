from functools import lru_cache
from datetime import datetime
from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    url_do_banco: str
    chave_secreta_jwt: SecretStr
    duracao_token_minutos: int = 30
    prazo_expiracao_reserva_horas: int = 48
    prazo_expiracao_apos: datetime | None = None
    local_dos_arquivos: Path = Path("./uploads")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("chave_secreta_jwt")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if len(secret) < 32 or secret.startswith("GERAR_"):
            raise ValueError(
                "CHAVE_SECRETA_JWT deve ser um segredo aleatorio de pelo menos 32 caracteres"
            )
        return value

    @field_validator("prazo_expiracao_reserva_horas")
    @classmethod
    def validate_reservation_expiration_hours(cls, value: int) -> int:
        if value < 1 or value > 720:
            raise ValueError("PRAZO_EXPIRACAO_RESERVA_HORAS deve estar entre 1 e 720")
        return value

    @field_validator("prazo_expiracao_apos")
    @classmethod
    def validate_reservation_expiration_cutover(
        cls, value: datetime | None
    ) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("PRAZO_EXPIRACAO_APOS deve incluir fuso horario")
        return value

@lru_cache
def get_settings() -> Settings:
    return Settings()
