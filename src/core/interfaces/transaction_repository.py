from abc import ABC, abstractmethod
from typing import Optional

from src.core.models.transaction import Transaction

class TransactionRepositoryInterface(ABC):
    @abstractmethod
    def save(self, transaction: Transaction) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        raise NotImplementedError

    @abstractmethod
    def get_by_wallet_address(self, wallet_address: str) ->  list[Transaction]:
        raise NotImplementedError

    @abstractmethod
    def get_by_user_wallets(self, wallet_addresses: list[str]) -> list[Transaction]:
        raise NotImplementedError

    @abstractmethod
    def get_total_fees_collected(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def count_all(self) -> int:
        raise NotImplementedError