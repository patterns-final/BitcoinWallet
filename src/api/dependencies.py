from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.services.user_service import UserService
from src.infra.database.sqlalchemy_connection import get_sqlalchemy_session
from src.infra.database.sqlalchemy_uow import SQLAlchemyUnitOfWork
from src.infra.repositories.user_repository import SQLAlchemyUserRepository
from src.infra.security.api_key_generator import ApiKeyGenerator


def get_user_service(session: Session = Depends(get_sqlalchemy_session)) -> UserService:
    user_repository = SQLAlchemyUserRepository(session)
    unit_of_work = SQLAlchemyUnitOfWork(session)
    api_key_generator = ApiKeyGenerator()
    return UserService(
        uow=unit_of_work,
        user_repository=user_repository,
        api_key_generator=api_key_generator
    )