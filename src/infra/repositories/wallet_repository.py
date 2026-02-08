from typing import Optional

from sqlalchemy.orm import Session

from src.core.interfaces.wallet_repository import WalletRepositoryInterface
from src.core.models.wallet import Wallet
from src.infra.models import WalletModel


class SQLAlchemyWalletRepository(WalletRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def save(self, wallet: Wallet) -> None:
        db_wallet = self.session.query(WalletModel).filter(WalletModel.id == wallet.id).first()

        if db_wallet:
            self._update_db_model(db_wallet, wallet)
        else:
            new_wallet = self._to_db_model(wallet)
            self.session.add(new_wallet)

        self.session.commit()

    def get_by_id(self, wallet_id: str) -> Optional[Wallet]:
        db_wallet = self.session.query(WalletModel).filter(WalletModel.id == wallet_id).first()
        return self._to_domain(db_wallet) if db_wallet else None

    def get_by_address(self, address: str) -> Optional[Wallet]:
        db_wallet = self.session.query(WalletModel).filter(WalletModel.address == address).first()
        return self._to_domain(db_wallet) if db_wallet else None

    def get_by_user_id(self, user_id: str) -> list[Wallet]:
        db_wallets = self.session.query(WalletModel).filter(WalletModel.user_id == user_id).all()
        return [self._to_domain(db_wallet) for db_wallet in db_wallets]

    def update(self, wallet: Wallet) -> None:
        db_wallet = self.session.query(WalletModel).filter(WalletModel.id == wallet.id).first()
        
        if not db_wallet:
            raise ValueError(f"Wallet with id {wallet.id} not found")
        
        self._update_db_model(db_wallet, wallet)
        self.session.commit()

    @staticmethod
    def _to_domain(db_wallet: WalletModel) -> Wallet:
        return Wallet(
            id=db_wallet.id,
            address=db_wallet.address,
            user_id=db_wallet.user_id,
            balance_satoshis=db_wallet.balance_satoshis
        )

    @staticmethod
    def _to_db_model(wallet: Wallet) -> WalletModel:
        return WalletModel(
            id=wallet.id,
            address=wallet.address,
            user_id=wallet.user_id,
            balance_satoshis=wallet.balance_satoshis
        )

    @staticmethod
    def _update_db_model(db_wallet: WalletModel, wallet: Wallet) -> None:
        db_wallet.address = wallet.address
        db_wallet.user_id = wallet.user_id
        db_wallet.balance_satoshis = wallet.balance_satoshis
