from __future__ import annotations

from fastapi import FastAPI

from src.api.routes import user_router
from src.config import settings, Settings
from src.infra.database.init_db import init_db


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Bitcoin Wallet API")

    app.include_router(user_router)

    @app.get("/")
    def root():
        return {"message": "This is root, see /docs for swagger"}

    app.state.settings = settings

    return app

init_db()
app = create_app(settings)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )