from src.core.interfaces.wallet_repository import WalletRepositoryInterface
from src.core.models.wallet import Wallet


class InMemoryWalletRepository(WalletRepositoryInterface):
    def __init__(self):
        self._wallets: dict[str, Wallet] = {}

    def save(self, wallet: Wallet) -> None:
        self._wallets[wallet.id] = wallet

    def get_by_id(self, id: str):
        return self._wallets.get(id)

    def get_by_address(self, address: str):
        return next(
            (w for w in self._wallets.values() if w.address == address),
            None,
        )

    def get_by_user_id(self, user_id: str):
        return [w for w in self._wallets.values() if w.user_id == user_id]

    def update(self, wallet: Wallet) -> None:
        self._wallets[wallet.id] = wallet


def test_save_and_get_by_id():
    repo = InMemoryWalletRepository()
    wallet = Wallet.create("user_123")

    repo.save(wallet)

    result = repo.get_by_id(wallet.id)
    assert result == wallet


def test_get_by_address():
    repo = InMemoryWalletRepository()
    wallet = Wallet.create("user_123")
    repo.save(wallet)

    result = repo.get_by_address(wallet.address)
    assert result == wallet


def test_get_by_user_id_returns_all_wallets():
    repo = InMemoryWalletRepository()
    wallets = [Wallet.create("user_123") for _ in range(3)]

    for wallet in wallets:
        repo.save(wallet)

    result = repo.get_by_user_id("user_123")
    assert len(result) == 3


def test_update_wallet():
    repo = InMemoryWalletRepository()
    wallet = Wallet.create("user_123")
    repo.save(wallet)

    wallet.deposit(1_000)
    repo.update(wallet)

    updated_wallet = repo.get_by_id(wallet.id)
    assert updated_wallet.balance_satoshis == wallet.balance_satoshis
