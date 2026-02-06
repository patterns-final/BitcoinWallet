import pytest

from src.core.interfaces.wallet_repository import WalletRepositoryInterface


def test_repository_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        WalletRepositoryInterface()
