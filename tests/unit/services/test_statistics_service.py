import pytest
from unittest.mock import Mock

from src.core.services.statistics_service import StatisticsService, PlatformStatistics
from src.core.interfaces.transaction_repository import TransactionRepositoryInterface


class TestStatisticsService:

    @pytest.fixture
    def mock_transaction_repository(self):
        return Mock(spec=TransactionRepositoryInterface)

    @pytest.fixture
    def service(self, mock_transaction_repository):
        return StatisticsService(transaction_repository=mock_transaction_repository)

    def test_get_platform_statistics_success(self, service, mock_transaction_repository):
        mock_transaction_repository.count_all.return_value = 100
        mock_transaction_repository.get_total_fees_collected.return_value = 15_000_000

        stats = service.get_platform_statistics()

        assert isinstance(stats, PlatformStatistics)
        assert stats.total_transactions == 100
        assert stats.platform_profit_satoshis == 15_000_000

    def test_get_platform_statistics_zero_transactions(self, service, mock_transaction_repository):
        mock_transaction_repository.count_all.return_value = 0
        mock_transaction_repository.get_total_fees_collected.return_value = 0

        stats = service.get_platform_statistics()

        assert stats.total_transactions == 0
        assert stats.platform_profit_satoshis == 0

    def test_get_platform_statistics_large_numbers(self, service, mock_transaction_repository):
        mock_transaction_repository.count_all.return_value = 999999
        mock_transaction_repository.get_total_fees_collected.return_value = 5_000_000_000

        stats = service.get_platform_statistics()

        assert stats.total_transactions == 999999
        assert stats.platform_profit_satoshis == 5_000_000_000

    def test_calls_repository_count_all(self, service, mock_transaction_repository):
        mock_transaction_repository.count_all.return_value = 50
        mock_transaction_repository.get_total_fees_collected.return_value = 1000

        service.get_platform_statistics()

        mock_transaction_repository.count_all.assert_called_once()

    def test_calls_repository_get_total_fees_collected(self, service, mock_transaction_repository):
        mock_transaction_repository.count_all.return_value = 50
        mock_transaction_repository.get_total_fees_collected.return_value = 1000

        service.get_platform_statistics()

        mock_transaction_repository.get_total_fees_collected.assert_called_once()

    def test_service_uses_injected_repository(self, mock_transaction_repository):
        service = StatisticsService(transaction_repository=mock_transaction_repository)

        assert service._transaction_repository is mock_transaction_repository