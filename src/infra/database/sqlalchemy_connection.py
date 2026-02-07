from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.config import settings


engine = create_engine(settings.database_url)

def get_sqlalchemy_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()