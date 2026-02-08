from __future__ import annotations

from dataclasses import replace
from typing import Optional

import pytest

from src.core.models.wallet import Wallet
from src.core.services.wallet_service import (
    UnauthorizedWalletAccessError,
    WalletLimitExceededError,
    WalletNotFoundError,
    WalletService,
)
from src.core.interfaces.wallet_repository import WalletRepositoryInterface


class InMemoryWalletRepository(WalletRepositoryInterface):
    def __init__(self) -> None:
        self._by_id: dict[str, Wallet] = {}
        self._by_address: dict[str, Wallet] = {}

    def save(self, wallet: Wallet) -> None:
        self._by_id[wallet.id] = wallet
        self._by_address[wallet.address] = wallet

    def get_by_id(self, id: str) -> Optional[Wallet]:
        return self._by_id.get(id)

    def get_by_address(self, address: str) -> Optional[Wallet]:
        return self._by_address.get(address)

    def get_by_user_id(self, user_id: str) -> list[Wallet]:
        return [w for w in self._by_id.values() if w.user_id == user_id]

    def update(self, wallet: Wallet) -> None:
        if wallet.id not in self._by_id:
            raise KeyError("Wallet does not exist")
        self._by_id[wallet.id] = wallet
        self._by_address[wallet.address] = wallet


def make_service() -> tuple[WalletService, InMemoryWalletRepository]:
    repo = InMemoryWalletRepository()
    return WalletService(repo), repo


def test_create_wallet_success() -> None:
    service, repo = make_service()

    res = service.create_wallet("user-1")
    assert res.wallet_id
    assert res.address
    assert res.balance_satoshis > 0

    wallets = repo.get_by_user_id("user-1")
    assert len(wallets) == 1
    assert wallets[0].address == res.address


def test_create_wallet_max_3_enforced() -> None:
    service, _ = make_service()

    service.create_wallet("user-1")
    service.create_wallet("user-1")
    service.create_wallet("user-1")

    with pytest.raises(WalletLimitExceededError):
        service.create_wallet("user-1")


def test_get_wallet_by_address_requires_ownership() -> None:
    service, repo = make_service()

    w = Wallet.create("user-1")
    repo.save(w)

    with pytest.raises(UnauthorizedWalletAccessError):
        service.get_wallet_by_address(user_id="user-2", address=w.address)


def test_get_wallet_by_address_not_found() -> None:
    service, _ = make_service()

    with pytest.raises(WalletNotFoundError):
        service.get_wallet_by_address(user_id="user-1", address="does-not-exist")


def test_deposit_updates_balance_and_persists() -> None:
    service, repo = make_service()

    w = Wallet.create("user-1")
    w.balance_satoshis = 100
    repo.save(w)

    updated = service.deposit(user_id="user-1", address=w.address, amount_satoshis=50)
    assert updated.balance_satoshis == 150

    persisted = repo.get_by_address(w.address)
    assert persisted is not None
    assert persisted.balance_satoshis == 150


def test_deposit_rejects_non_positive_amount() -> None:
    service, repo = make_service()

    w = Wallet.create("user-1")
    w.balance_satoshis = 100
    repo.save(w)

    with pytest.raises(ValueError):
        service.deposit(user_id="user-1", address=w.address, amount_satoshis=0)

    with pytest.raises(ValueError):
        service.deposit(user_id="user-1", address=w.address, amount_satoshis=-1)


def test_withdraw_updates_balance_and_persists() -> None:
    service, repo = make_service()

    w = Wallet.create("user-1")
    w.balance_satoshis = 200
    repo.save(w)

    updated = service.withdraw(user_id="user-1", address=w.address, amount_satoshis=50)
    assert updated.balance_satoshis == 150

    persisted = repo.get_by_address(w.address)
    assert persisted is not None
    assert persisted.balance_satoshis == 150


def test_withdraw_rejects_insufficient_balance() -> None:
    service, repo = make_service()

    w = Wallet.create("user-1")
    w.balance_satoshis = 10
    repo.save(w)

    with pytest.raises(ValueError):
        service.withdraw(user_id="user-1", address=w.address, amount_satoshis=11)


def test_withdraw_rejects_non_positive_amount() -> None:
    service, repo = make_service()

    w = Wallet.create("user-1")
    w.balance_satoshis = 10
    repo.save(w)

    with pytest.raises(ValueError):
        service.withdraw(user_id="user-1", address=w.address, amount_satoshis=0)

    with pytest.raises(ValueError):
        service.withdraw(user_id="user-1", address=w.address, amount_satoshis=-5)
