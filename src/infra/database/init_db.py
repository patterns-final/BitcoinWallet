from pathlib import Path

from sqlalchemy import create_engine

from src.config import settings
from src.infra.database.models import Base

engine = create_engine(settings.database_url)

def init_db():
    db_path = Path(settings.sqlite_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)