import pytest
from datetime import datetime, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.core.models.transaction import Transaction
from src.infra.database.models import Base, TransactionModel
from src.infra.repositories.transaction_repository import SQLTransactionRepository


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    session = Session(in_memory_db)
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def transaction_repo(session):
    return SQLTransactionRepository(session)


@pytest.fixture
def sample_transaction():
    return Transaction.create(
        from_wallet_address="wallet-123",
        to_wallet_address="wallet-456",
        amount_satoshis=10000,
        is_internal_transfer=False
    )


class TestTransactionRepository:

    def test_save_transaction(self, transaction_repo, session, sample_transaction):
        transaction_repo.save(sample_transaction)
        session.commit()

        saved = session.query(TransactionModel).filter_by(id=sample_transaction.id).first()
        assert saved is not None
        assert saved.from_wallet_address == "wallet-123"
        assert saved.to_wallet_address == "wallet-456"
        assert saved.amount_satoshis == 10000
        assert saved.fee_satoshis == 150

    def test_get_by_id_existing(self, transaction_repo, session, sample_transaction):
        transaction_repo.save(sample_transaction)
        session.commit()

        result = transaction_repo.get_by_id(sample_transaction.id)

        assert result is not None
        assert result.id == sample_transaction.id
        assert result.from_wallet_address == "wallet-123"
        assert result.amount_satoshis == 10000

    def test_get_by_id_nonexistent(self, transaction_repo):
        result = transaction_repo.get_by_id("nonexistent-id")
        assert result is None

    def test_get_by_wallet_address_as_sender(self, transaction_repo, session, sample_transaction):
        transaction_repo.save(sample_transaction)
        session.commit()

        results = transaction_repo.get_by_wallet_address("wallet-123")

        assert len(results) == 1
        assert results[0].from_wallet_address == "wallet-123"

    def test_get_by_wallet_address_as_receiver(self, transaction_repo, session, sample_transaction):
        transaction_repo.save(sample_transaction)
        session.commit()

        results = transaction_repo.get_by_wallet_address("wallet-456")

        assert len(results) == 1
        assert results[0].to_wallet_address == "wallet-456"

    def test_get_by_wallet_address_multiple_transactions(self, transaction_repo, session):
        tx1 = Transaction.create("wallet-123", "wallet-456", 1000, False)
        tx2 = Transaction.create("wallet-789", "wallet-123", 2000, False)
        tx3 = Transaction.create("wallet-123", "wallet-999", 3000, False)

        transaction_repo.save(tx1)
        transaction_repo.save(tx2)
        transaction_repo.save(tx3)
        session.commit()

        results = transaction_repo.get_by_wallet_address("wallet-123")

        assert len(results) == 3
        assert results[0].amount_satoshis == 3000

    def test_get_by_wallet_address_no_transactions(self, transaction_repo):
        results = transaction_repo.get_by_wallet_address("nonexistent-wallet")
        assert results == []

    def test_get_by_user_wallets_empty_list(self, transaction_repo):
        results = transaction_repo.get_by_user_wallets([])
        assert results == []

    def test_get_by_user_wallets_single_wallet(self, transaction_repo, session, sample_transaction):
        transaction_repo.save(sample_transaction)
        session.commit()

        results = transaction_repo.get_by_user_wallets(["wallet-123"])

        assert len(results) == 1
        assert results[0].from_wallet_address == "wallet-123"

    def test_get_by_user_wallets_multiple_wallets(self, transaction_repo, session):
        tx1 = Transaction.create("wallet-1", "wallet-external", 1000, False)
        tx2 = Transaction.create("wallet-2", "wallet-1", 2000, True)
        tx3 = Transaction.create("wallet-external", "wallet-2", 3000, False)
        tx4 = Transaction.create("wallet-other", "wallet-other2", 4000, False)

        transaction_repo.save(tx1)
        transaction_repo.save(tx2)
        transaction_repo.save(tx3)
        transaction_repo.save(tx4)
        session.commit()

        results = transaction_repo.get_by_user_wallets(["wallet-1", "wallet-2"])

        assert len(results) == 3
        wallet_addresses = {tx.from_wallet_address for tx in results} | {tx.to_wallet_address for tx in results}
        assert "wallet-1" in wallet_addresses
        assert "wallet-2" in wallet_addresses
        assert "wallet-other" not in wallet_addresses

    def test_get_total_fees_collected_no_transactions(self, transaction_repo):
        total_fees = transaction_repo.get_total_fees_collected()
        assert total_fees == 0

    def test_get_total_fees_collected_with_transactions(self, transaction_repo, session):
        tx1 = Transaction.create("wallet-1", "wallet-2", 10000, False)
        tx2 = Transaction.create("wallet-2", "wallet-3", 20000, False)
        tx3 = Transaction.create("wallet-1", "wallet-2", 5000, True)

        transaction_repo.save(tx1)
        transaction_repo.save(tx2)
        transaction_repo.save(tx3)
        session.commit()

        total_fees = transaction_repo.get_total_fees_collected()
        assert total_fees == 450

    def test_get_total_fees_collected_only_internal(self, transaction_repo, session):
        tx1 = Transaction.create("wallet-1", "wallet-2", 10000, True)
        tx2 = Transaction.create("wallet-2", "wallet-1", 5000, True)

        transaction_repo.save(tx1)
        transaction_repo.save(tx2)
        session.commit()

        total_fees = transaction_repo.get_total_fees_collected()
        assert total_fees == 0

    def test_count_all_empty(self, transaction_repo):
        count = transaction_repo.count_all()
        assert count == 0

    def test_count_all_with_transactions(self, transaction_repo, session):
        tx1 = Transaction.create("wallet-1", "wallet-2", 1000, False)
        tx2 = Transaction.create("wallet-2", "wallet-3", 2000, False)
        tx3 = Transaction.create("wallet-3", "wallet-1", 3000, False)

        transaction_repo.save(tx1)
        transaction_repo.save(tx2)
        transaction_repo.save(tx3)
        session.commit()

        count = transaction_repo.count_all()
        assert count == 3

    def test_internal_transfer_has_no_fee(self, transaction_repo, session):
        tx = Transaction.create(
            from_wallet_address="wallet-1",
            to_wallet_address="wallet-2",
            amount_satoshis=50000,
            is_internal_transfer=True
        )

        transaction_repo.save(tx)
        session.commit()
        result = transaction_repo.get_by_id(tx.id)

        assert result.is_internal_transfer is True
        assert result.fee_satoshis == 0

    def test_external_transfer_has_fee(self, transaction_repo, session):
        tx = Transaction.create(
            from_wallet_address="wallet-1",
            to_wallet_address="wallet-2",
            amount_satoshis=100000,
            is_internal_transfer=False
        )

        transaction_repo.save(tx)
        session.commit()
        result = transaction_repo.get_by_id(tx.id)

        assert result.is_internal_transfer is False
        assert result.fee_satoshis == 1500

    def test_transaction_ordering_newest_first(self, transaction_repo, session):
        import time
        tx1 = Transaction.create("wallet-1", "wallet-2", 1000, False)
        time.sleep(0.01)
        tx2 = Transaction.create("wallet-1", "wallet-2", 2000, False)
        time.sleep(0.01)
        tx3 = Transaction.create("wallet-1", "wallet-2", 3000, False)

        transaction_repo.save(tx1)
        transaction_repo.save(tx2)
        transaction_repo.save(tx3)
        session.commit()

        results = transaction_repo.get_by_wallet_address("wallet-1")

        assert len(results) == 3
        assert results[0].amount_satoshis == 3000
        assert results[1].amount_satoshis == 2000
        assert results[2].amount_satoshis == 1000