from __future__ import annotations

from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    Application configuration.

    Values are loaded (in this order):
    1) environment variables
    2) .env file (if present)
    3) defaults defined here
    """
    sqlite_path: Path = Field(
        default=ROOT_DIR / "data" / "bitcoin_wallet.db",
        validation_alias="SQLITE_PATH",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.sqlite_path}"

    MIGRATIONS_PATH: str = str(ROOT_DIR / "src" / "migrations")

    ADMIN_API_KEY: str = "admin-api-key"   # declared in .env file

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()