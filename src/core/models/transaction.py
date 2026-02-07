from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional
from decimal import Decimal

@dataclass
class Transaction:
    from_wallet_address: str
    to_wallet_address: str
    amount_satoshis: int
    fee_satoshis: int
    is_internal_transfer: bool = False
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    FEE_RATE = Decimal("0.015")

    @classmethod
    def create(
        cls,
        from_wallet_address: str,
        to_wallet_address: str,
        amount_satoshis: int,
        is_internal_transfer: bool = False,
    )->Transaction:

        if amount_satoshis <= 0:
            raise ValueError("Transaction amount must be positive")

        if not from_wallet_address or not to_wallet_address:
            raise ValueError("Wallet addresses cannot be empty")

        if from_wallet_address == to_wallet_address:
            raise ValueError("Cannot transfer to the same wallet")

        if is_internal_transfer:
            fee_satoshis = 0
        else:
            fee_decimal = Decimal(amount_satoshis) * cls.FEE_RATE
            fee_satoshis = round(fee_decimal)

        return cls(
            id=str(uuid.uuid4()),
            from_wallet_address=from_wallet_address,
            to_wallet_address=to_wallet_address,
            amount_satoshis=amount_satoshis,
            fee_satoshis=fee_satoshis,
            is_internal_transfer=is_internal_transfer,
            created_at=datetime.now(UTC)
        )

    def get_total_deducted(self) -> int:
        return self.amount_satoshis

    def get_recipient_amount(self) -> int:
        return self.amount_satoshis - self.fee_satoshis

    def is_same_wallet_transfer(self) -> bool:
        return self.from_wallet_address == self.to_wallet_address