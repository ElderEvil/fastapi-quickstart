from typing import Literal

from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    App settings with database configuration.
    Supports environment variables and .env files.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ENVIRONMENT: Literal["development", "production"] = "development"

    ASYNC_DATABASE_URI: PostgresDsn | str = ""
    DB_TYPE: Literal["sqlite", "postgres"] = "sqlite"
    DB_NAME: str = "app.db"
    DB_USER: str = "user"
    DB_PASSWORD: str = "changeme"
    DB_HOST: str = "localhost"

    DB_POOL_SIZE: int = 83
    WEB_CONCURRENCY: int = 9
    MAX_OVERFLOW: int = 64

    @field_validator("ASYNC_DATABASE_URI", mode="after")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        """
        Automatically builds the async Postgres connection string if ASYNC_DATABASE_URI is not set.
        """
        if v is None and info.data.get("DB_TYPE") == "postgres":
            return str(
                PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=info.data["DB_USER"],
                    password=info.data["DB_PASSWORD"],
                    host=info.data["DB_HOST"],
                    path=f"/{info.data['DB_NAME']}",  # Postgres path must start with '/'
                )
            )
        return v or f"sqlite+aiosqlite:///{info.data['DB_NAME']}"

    @property
    def pool_size(self) -> int:
        """
        Dynamically calculates pool size based on concurrency settings.
        """
        return max(self.DB_POOL_SIZE // self.WEB_CONCURRENCY, 5)


settings = Settings()
