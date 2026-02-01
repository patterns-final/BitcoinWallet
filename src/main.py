from __future__ import annotations

from fastapi import FastAPI

from src.config import Settings
from src.infra.database.migrate import run_migrations


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Bitcoin Wallet API")

    app.state.settings = settings

    @app.on_event("startup")
    def _startup() -> None:
        run_migrations(db_path=settings.sqlite_path)

    return app


app = create_app(Settings())
