from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BYTES_PER_KIB = 1024
KIB_PER_MIB = 1024


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    chat_api_base_url: str | None = Field(default=None, alias="CHAT_API_BASE_URL")

    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_service_role_key: str | None = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    max_upload_size_mib: int = Field(default=2, alias="MAX_UPLOAD_SIZE_MIB", ge=1)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mib * KIB_PER_MIB * BYTES_PER_KIB


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()


# Backward-compatible alias while we migrate call sites.
get_settings = get_app_settings
