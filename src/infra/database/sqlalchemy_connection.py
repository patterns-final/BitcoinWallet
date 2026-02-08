from typing import Generator

from sqlalchemy.orm import Session

from src.infra.database.init_db import engine


def get_sqlalchemy_session() -> Generator[Session, None, None]:
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()