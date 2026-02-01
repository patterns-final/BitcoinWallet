from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Values are loaded (in this order):
    1) environment variables
    2) .env file (if present)
    3) defaults defined here
    """
    sqlite_path: Path = Field(
        default=Path("data") / "bitcoin_wallet.db",
        validation_alias="SQLITE_PATH",
    )

    model_config = SettingsConfigDict(
        env_file=".env",  
        env_file_encoding="utf-8",
        extra="ignore",
    )
