from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.services.user_service import UserService
from src.infra.database.sqlalchemy_connection import get_sqlalchemy_session
from src.infra.repositories.user_repository import SQLAlchemyUserRepository
from src.infra.security.api_key_generator import ApiKeyGenerator


def get_user_service(session: Session = Depends(get_sqlalchemy_session)) -> UserService:
    user_repository = SQLAlchemyUserRepository(session)
    api_key_generator = ApiKeyGenerator()
    return UserService(user_repository, api_key_generator)