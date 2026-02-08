from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.core.interfaces.wallet_repository import WalletRepositoryInterface
from src.core.models.wallet import Wallet

from src.core.constants import MAX_WALLETS_PER_USER


class WalletLimitExceededError(Exception):
    pass


class WalletNotFoundError(Exception):
    pass


class UnauthorizedWalletAccessError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class CreateWalletResult:
    wallet_id: str
    address: str
    balance_satoshis: int


class WalletService:
    def __init__(self, wallet_repository: WalletRepositoryInterface) -> None:
        self._wallet_repository = wallet_repository

    def create_wallet(self, user_id: str) -> CreateWalletResult:
        wallets = self._wallet_repository.get_by_user_id(user_id)
        if len(wallets) >= MAX_WALLETS_PER_USER:
            raise WalletLimitExceededError(f"User already has {MAX_WALLETS_PER_USER} wallets")

        wallet = Wallet.create(user_id=user_id)
        self._wallet_repository.save(wallet)

        return CreateWalletResult(
            wallet_id=wallet.id,
            address=wallet.address,
            balance_satoshis=wallet.balance_satoshis,
        )

    def list_wallets(self, user_id: str) -> list[Wallet]:
        return self._wallet_repository.get_by_user_id(user_id)

    def get_wallet_by_address(self, *, user_id: str, address: str) -> Wallet:
        return self._get_owned_wallet(user_id=user_id, address=address)

    def deposit(self, *, user_id: str, address: str, amount_satoshis: int) -> Wallet:
        wallet = self._get_owned_wallet(user_id=user_id, address=address)
        wallet.deposit(amount_satoshis)
        self._wallet_repository.update(wallet)
        return wallet

    def withdraw(self, *, user_id: str, address: str, amount_satoshis: int) -> Wallet:
        wallet = self._get_owned_wallet(user_id=user_id, address=address)
        wallet.withdraw(amount_satoshis)
        self._wallet_repository.update(wallet)
        return wallet

    def _get_owned_wallet(self, *, user_id: str, address: str) -> Wallet:
        wallet: Optional[Wallet] = self._wallet_repository.get_by_address(address)
        if wallet is None:
            raise WalletNotFoundError("Wallet not found")

        if wallet.user_id != user_id:
            raise UnauthorizedWalletAccessError("Unauthorized")

        return wallet
