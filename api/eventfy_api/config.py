from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    url_do_banco: str
    chave_secreta_jwt: SecretStr
    duracao_token_minutos: int = 30
    local_dos_arquivos: Path = Path("./uploads")
    versao_app: str = "0.2.0"
    ambiente: str = "desenvolvimento"
    nivel_log: str = "INFO"

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
