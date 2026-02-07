from abc import ABC, abstractmethod
from typing import Optional

from src.core.domain.models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    def save(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        raise NotImplementedError