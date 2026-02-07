from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

class WalletLimitReachedError(Exception):
    pass

@dataclass
class User:
    api_key: str
    id: Optional[str] = None
    wallet_ids: list[str] = field(default_factory=list)

    MAX_WALLETS: int = 3

    @classmethod
    def create(cls, api_key: str) -> User:
        return cls(
            id=str(uuid.uuid4()),
            api_key=api_key,
        )

    def can_create_wallet(self) -> bool:
        return len(self.wallet_ids) < self.MAX_WALLETS

    def add_wallet(self, wallet_id: str) -> None:
        if not self.can_create_wallet():
            raise WalletLimitReachedError(f"User cannot create more than {self.MAX_WALLETS} wallets")

        if wallet_id not in self.wallet_ids:
            self.wallet_ids.append(wallet_id)