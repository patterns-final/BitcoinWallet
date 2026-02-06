import pytest

from src.core.models.wallet import Wallet
from src.core.constants import INITIAL_BALANCE_SATOSHIS


class TestWallet:
    def test_create(self):
        user_id = "user_123"
        wallet = Wallet.create(user_id)
        assert wallet.user_id == user_id
        assert wallet.balance_satoshis == INITIAL_BALANCE_SATOSHIS
        assert wallet.id is not None
        assert wallet.address is not None

    def test_deposit_success(self):
        wallet = Wallet.create("user_123")
        initial_balance = wallet.balance_satoshis
        wallet.deposit(50_000_000)
        assert wallet.balance_satoshis == initial_balance + 50_000_000

    def test_deposit_zero_raises_error(self):
        wallet = Wallet.create("user_123")
        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            wallet.deposit(0)

    def test_deposit_negative_raises_error(self):
        wallet = Wallet.create("user_123")
        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            wallet.deposit(-1)
