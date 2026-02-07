import pytest
from datetime import datetime, timezone

from src.core.models.transaction import Transaction


class TestTransactionCreate:

    def test_create_valid_internal_transaction(self):
        transaction = Transaction.create(
            from_wallet_address="wallet_abc",
            to_wallet_address="wallet_xyz",
            amount_satoshis=50000000,
            is_internal_transfer=True
        )

        assert transaction.id is not None
        assert transaction.from_wallet_address == "wallet_abc"
        assert transaction.to_wallet_address == "wallet_xyz"
        assert transaction.amount_satoshis == 50000000
        assert transaction.fee_satoshis == 0
        assert transaction.is_internal_transfer is True
        assert transaction.created_at is not None
        assert isinstance(transaction.created_at, datetime)

    def test_create_valid_external_transaction(self):
        transaction = Transaction.create(
            from_wallet_address="wallet_abc",
            to_wallet_address="wallet_xyz",
            amount_satoshis=100000,
            is_internal_transfer=False
        )

        assert transaction.id is not None
        assert transaction.from_wallet_address == "wallet_abc"
        assert transaction.to_wallet_address == "wallet_xyz"
        assert transaction.amount_satoshis == 100000
        assert transaction.fee_satoshis == 1500
        assert transaction.is_internal_transfer is False
        assert transaction.created_at is not None
        assert isinstance(transaction.created_at, datetime)

    def test_create_generates_unique_ids(self):
        transaction1 = Transaction.create(
            from_wallet_address="wallet_1",
            to_wallet_address="wallet_2",
            amount_satoshis=1000,
            is_internal_transfer=False
        )

        transaction2 = Transaction.create(
            from_wallet_address="wallet_1",
            to_wallet_address="wallet_2",
            amount_satoshis=1000,
            is_internal_transfer=False
        )

        assert transaction1.id != transaction2.id

    def test_create_internal_transfer_has_zero_fee(self):
        transaction = Transaction.create(
            from_wallet_address="wallet_abc",
            to_wallet_address="wallet_xyz",
            amount_satoshis=100000,
            is_internal_transfer=True
        )

        assert transaction.fee_satoshis == 0

    def test_create_external_transfer_calculates_fee(self):
        transaction = Transaction.create(
            from_wallet_address="wallet_abc",
            to_wallet_address="wallet_xyz",
            amount_satoshis=100000,
            is_internal_transfer=False
        )

        assert transaction.fee_satoshis == 1500

    def test_create_with_zero_amount_raises_error(self):
        with pytest.raises(ValueError, match="amount must be positive"):
            Transaction.create(
                from_wallet_address="wallet_abc",
                to_wallet_address="wallet_xyz",
                amount_satoshis=0,
                is_internal_transfer=False
            )

    def test_create_with_negative_amount_raises_error(self):
        with pytest.raises(ValueError, match="amount must be positive"):
            Transaction.create(
                from_wallet_address="wallet_abc",
                to_wallet_address="wallet_xyz",
                amount_satoshis=-1000,
                is_internal_transfer=False
            )

    def test_create_with_empty_from_address_raises_error(self):
        with pytest.raises(ValueError, match="Wallet addresses cannot be empty"):
            Transaction.create(
                from_wallet_address="",
                to_wallet_address="wallet_xyz",
                amount_satoshis=1000,
                is_internal_transfer=False
            )

    def test_create_with_empty_to_address_raises_error(self):
        with pytest.raises(ValueError, match="Wallet addresses cannot be empty"):
            Transaction.create(
                from_wallet_address="wallet_abc",
                to_wallet_address="",
                amount_satoshis=1000,
                is_internal_transfer=False
            )

    def test_create_with_same_wallet_addresses_raises_error(self):
        with pytest.raises(ValueError, match="Cannot transfer to the same wallet"):
            Transaction.create(
                from_wallet_address="wallet_abc",
                to_wallet_address="wallet_abc",
                amount_satoshis=1000,
                is_internal_transfer=False
            )


class TestTransactionMethods:

    def test_get_total_deducted_external_transfer(self):
        transaction = Transaction.create(
            from_wallet_address="wallet_abc",
            to_wallet_address="wallet_xyz",
            amount_satoshis=100000,
            is_internal_transfer=False
        )
        assert transaction.get_total_deducted() == 100000

    def test_get_total_deducted_internal_transfer(self):
        transaction = Transaction.create(
            from_wallet_address="wallet_abc",
            to_wallet_address="wallet_xyz",
            amount_satoshis=100000,
            is_internal_transfer=True
        )
        assert transaction.get_total_deducted() == 100000

    def test_get_recipient_amount_external_transfer(self):
        transaction = Transaction.create(
            from_wallet_address="wallet_abc",
            to_wallet_address="wallet_xyz",
            amount_satoshis=100000,
            is_internal_transfer=False
        )
        assert transaction.get_recipient_amount() == 98500

    def test_get_recipient_amount_internal_transfer(self):
        transaction = Transaction.create(
            from_wallet_address="wallet_abc",
            to_wallet_address="wallet_xyz",
            amount_satoshis=100000,
            is_internal_transfer=True
        )
        assert transaction.get_recipient_amount() == 100000