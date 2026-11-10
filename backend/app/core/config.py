from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ReqLens AI"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "reqlens"
    allow_in_memory_db: bool = True
    jwt_secret: str = "development-only-change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    openai_api_key: str | None = None
    tavily_api_key: str | None = None
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    cors_origins: list[str] | str = Field(default=["http://localhost:5173"])
    max_upload_mb: int = 15
    ai_enabled: bool = True
    upload_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def openai_ready(self) -> bool:
        return self.ai_enabled and bool(self.openai_api_key)

    @property
    def can_use_in_memory_db(self) -> bool:
        return self.environment == "development" and self.allow_in_memory_db


@lru_cache
def get_settings() -> Settings:
    return Settings()

