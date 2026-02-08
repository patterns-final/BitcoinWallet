from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from src.core.interfaces.transaction_repository import TransactionRepositoryInterface
from src.core.models.transaction import Transaction
from src.infra.database.models import TransactionModel


class SQLTransactionRepository(TransactionRepositoryInterface):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, transaction: Transaction) -> None:
        model = self._to_db_model(transaction)
        self._session.add(model) #Service layer will handle session commits
        self._session.flush()

    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        model = (
            self._session.query(TransactionModel)
            .filter_by(id=transaction_id)
            .first()
        )
        return self._to_domain(model) if model else None

    def get_by_wallet_address(self, wallet_address: str) -> list[Transaction]:
        models = (
            self._session.query(TransactionModel)
            .filter(
                or_(
                    TransactionModel.from_wallet_address == wallet_address,
                    TransactionModel.to_wallet_address == wallet_address
                )
            )
            .order_by(desc(TransactionModel.created_at))
            .all()
        )
        return [self._to_domain(m) for m in models]

    def get_by_user_wallets(self, wallet_addresses: list[str]) -> list[Transaction]:
        if not wallet_addresses:
            return []

        models = (
            self._session.query(TransactionModel)
            .filter(
                or_(
                    TransactionModel.from_wallet_address.in_(wallet_addresses),
                    TransactionModel.to_wallet_address.in_(wallet_addresses)
                )
            )
            .order_by(desc(TransactionModel.created_at))
            .all()
        )
        return [self._to_domain(m) for m in models]

    def get_total_fees_collected(self) -> int:
        result = (
            self._session.query(func.sum(TransactionModel.fee_satoshis))
            .scalar()
        )
        return result or 0

    def count_all(self) -> int:
        return self._session.query(TransactionModel).count()

    @staticmethod
    def _to_domain(model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            from_wallet_address=model.from_wallet_address,
            to_wallet_address=model.to_wallet_address,
            amount_satoshis=model.amount_satoshis,
            fee_satoshis=model.fee_satoshis,
            is_internal_transfer=model.is_internal_transfer,
            created_at=model.created_at
        )

    @staticmethod
    def _to_db_model(transaction: Transaction) -> TransactionModel:
        return TransactionModel(
            id=transaction.id,
            from_wallet_address=transaction.from_wallet_address,
            to_wallet_address=transaction.to_wallet_address,
            amount_satoshis=transaction.amount_satoshis,
            fee_satoshis=transaction.fee_satoshis,
            is_internal_transfer=transaction.is_internal_transfer,
            created_at=transaction.created_at
        )