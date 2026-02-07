from dataclasses import dataclass
from uuid import uuid4

from src.core.constants import INITIAL_BALANCE_SATOSHIS


@dataclass
class Wallet:
    id: str
    address: str
    user_id: str
    balance_satoshis: int

    @classmethod
    def create(cls, user_id: str) -> "Wallet":
        return cls(
            id=str(uuid4()),
            address=str(uuid4()),
            user_id=user_id,
            balance_satoshis=INITIAL_BALANCE_SATOSHIS,
        )

    def deposit(self, amount_satoshis: int) -> None:
        if amount_satoshis <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance_satoshis += amount_satoshis

    def withdraw(self, amount_satoshis: int) -> None:
        if amount_satoshis <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount_satoshis > self.balance_satoshis:
            raise ValueError("Insufficient balance")
        self.balance_satoshis -= amount_satoshis