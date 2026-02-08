from typing import Optional, cast

from sqlalchemy.orm import Session

from src.core.interfaces.user_repository import UserRepositoryInterface
from src.core.models.user import User
from src.infra.models import UserModel


class SQLAlchemyUserRepository(UserRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> None:
        db_user = self.session.query(UserModel).filter(UserModel.id == user.id).first()

        if db_user:    # Already exists, update it
            self._update_db_model(db_user, user)
        else:
            new_user = self._to_db_model(user)
            self.session.add(new_user)

    def get_by_id(self, user_id: str) -> Optional[User]:
        db_user = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_domain(db_user) if db_user else None

    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        db_user = self.session.query(UserModel).filter(UserModel.api_key == api_key).first()
        return self._to_domain(db_user) if db_user else None


    @staticmethod
    def _to_domain(db_user: UserModel) -> User:
        return User(
            id=db_user.id,
            api_key=db_user.api_key,
            wallet_ids=[wallet.address for wallet in db_user.wallets]
        )

    @staticmethod
    def _to_db_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            api_key=user.api_key
        )

    @staticmethod
    def _update_db_model(db_user: UserModel, user: User) -> None:
        db_user.api_key = user.api_key
