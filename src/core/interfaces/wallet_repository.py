from abc import ABC, abstractmethod
from typing import Optional

from src.core.models.wallet import Wallet


class WalletRepositoryInterface(ABC):
    @abstractmethod
    def save(self, wallet: Wallet):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Wallet]:
        raise NotImplementedError

    @abstractmethod
    def get_by_address(self, address: str) -> Optional[Wallet]:
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> list[Wallet]:
        raise NotImplementedError

    @abstractmethod
    def update(self, wallet: Wallet):
        raise NotImplementedError
