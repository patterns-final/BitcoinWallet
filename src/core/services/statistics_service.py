from dataclasses import dataclass

from src.core.interfaces.transaction_repository import TransactionRepositoryInterface


@dataclass
class PlatformStatistics:
    total_transactions: int
    platform_profit_satoshis: int


class StatisticsService:
    def __init__(self, transaction_repository: TransactionRepositoryInterface):
        self._transaction_repository = transaction_repository

    def get_platform_statistics(self) -> PlatformStatistics:
        return PlatformStatistics(
            total_transactions=self._transaction_repository.count_all(),
            platform_profit_satoshis=self._transaction_repository.get_total_fees_collected()
        )