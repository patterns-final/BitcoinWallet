import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.core.interfaces.wallet_repository import WalletRepositoryInterface
from src.core.models.wallet import Wallet
from src.infra.models import Base, WalletModel
from src.infra.repositories.wallet_repository import SQLAlchemyWalletRepository


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
def wallet_repo(session):
    return SQLAlchemyWalletRepository(session)


@pytest.fixture
def sample_wallet():
    return Wallet.create(user_id="user-123")


def test_repository_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        WalletRepositoryInterface()


class TestSQLAlchemyWalletRepository:

    def test_save_wallet(self, wallet_repo, session, sample_wallet):
        wallet_repo.save(sample_wallet)

        saved = session.query(WalletModel).filter_by(id=sample_wallet.id).first()
        assert saved is not None
        assert saved.id == sample_wallet.id
        assert saved.address == sample_wallet.address
        assert saved.user_id == sample_wallet.user_id
        assert saved.balance_satoshis == sample_wallet.balance_satoshis

    def test_save_updates_existing_wallet(self, wallet_repo, session, sample_wallet):
        wallet_repo.save(sample_wallet)
        
        sample_wallet.balance_satoshis = 50000
        wallet_repo.save(sample_wallet)

        saved = session.query(WalletModel).filter_by(id=sample_wallet.id).first()
        assert saved.balance_satoshis == 50000

    def test_get_by_id_existing(self, wallet_repo, session, sample_wallet):
        wallet_repo.save(sample_wallet)

        result = wallet_repo.get_by_id(sample_wallet.id)

        assert result is not None
        assert result.id == sample_wallet.id
        assert result.address == sample_wallet.address
        assert result.user_id == sample_wallet.user_id
        assert result.balance_satoshis == sample_wallet.balance_satoshis

    def test_get_by_id_nonexistent(self, wallet_repo):
        result = wallet_repo.get_by_id("nonexistent-id")
        assert result is None

    def test_get_by_address_existing(self, wallet_repo, session, sample_wallet):
        wallet_repo.save(sample_wallet)

        result = wallet_repo.get_by_address(sample_wallet.address)

        assert result is not None
        assert result.id == sample_wallet.id
        assert result.address == sample_wallet.address

    def test_get_by_address_nonexistent(self, wallet_repo):
        result = wallet_repo.get_by_address("nonexistent-address")
        assert result is None

    def test_get_by_user_id_single_wallet(self, wallet_repo, session, sample_wallet):
        wallet_repo.save(sample_wallet)

        results = wallet_repo.get_by_user_id("user-123")

        assert len(results) == 1
        assert results[0].id == sample_wallet.id
        assert results[0].user_id == "user-123"

    def test_get_by_user_id_multiple_wallets(self, wallet_repo, session):
        wallet1 = Wallet.create(user_id="user-123")
        wallet2 = Wallet.create(user_id="user-123")
        wallet3 = Wallet.create(user_id="user-456")

        wallet_repo.save(wallet1)
        wallet_repo.save(wallet2)
        wallet_repo.save(wallet3)

        results = wallet_repo.get_by_user_id("user-123")

        assert len(results) == 2
        wallet_ids = {w.id for w in results}
        assert wallet1.id in wallet_ids
        assert wallet2.id in wallet_ids
        assert wallet3.id not in wallet_ids

    def test_get_by_user_id_no_wallets(self, wallet_repo):
        results = wallet_repo.get_by_user_id("nonexistent-user")
        assert results == []

    def test_update_existing_wallet(self, wallet_repo, session, sample_wallet):
        wallet_repo.save(sample_wallet)

        sample_wallet.balance_satoshis = 75000
        sample_wallet.address = "new-address-123"
        
        wallet_repo.update(sample_wallet)

        saved = session.query(WalletModel).filter_by(id=sample_wallet.id).first()
        assert saved.balance_satoshis == 75000
        assert saved.address == "new-address-123"

    def test_update_nonexistent_wallet_raises_error(self, wallet_repo, sample_wallet):
        with pytest.raises(ValueError, match="Wallet with id .* not found"):
            wallet_repo.update(sample_wallet)

    def test_to_domain_conversion(self, wallet_repo, session, sample_wallet):
        wallet_repo.save(sample_wallet)

        result = wallet_repo.get_by_id(sample_wallet.id)

        assert isinstance(result, Wallet)
        assert result.id == sample_wallet.id
        assert result.address == sample_wallet.address
        assert result.user_id == sample_wallet.user_id
        assert result.balance_satoshis == sample_wallet.balance_satoshis
