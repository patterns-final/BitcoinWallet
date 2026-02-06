import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
import requests

from src.core.services.exchange_rate_service import ExchangeRateService
from src.core.interfaces.exchange_rate import ExchangeRateError


class TestExchangeRateService:

    @pytest.fixture
    def service(self):
        return ExchangeRateService()

    @pytest.fixture
    def mock_api_response(self):
        mock_resp = Mock()
        mock_resp.json.return_value = {
            'data': {
                'currency': 'BTC',
                'rates': {
                    'USD': '45000.50'
                }
            }
        }
        mock_resp.raise_for_status = Mock()
        return mock_resp

    @patch('requests.get')
    def test_get_btc_to_usd_rate_success(self, mock_get, service, mock_api_response):
        mock_get.return_value = mock_api_response
        rate = service.get_btc_to_usd_rate()

        assert rate == Decimal('45000.50')
        assert isinstance(rate, Decimal)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_get_btc_to_usd_rate_uses_correct_url(self, mock_get, service, mock_api_response):
        mock_get.return_value = mock_api_response
        service.get_btc_to_usd_rate()

        call_args = mock_get.call_args
        assert "coinbase" in call_args[0][0]
        assert "BTC" in call_args[0][0]
        assert call_args[1]['timeout'] == 5

    @patch('requests.get')
    def test_api_timeout_raises_error(self, mock_get, service):
        mock_get.side_effect = requests.Timeout("Timeout")

        with pytest.raises(ExchangeRateError):
            service.get_btc_to_usd_rate()

    @patch('requests.get')
    def test_api_http_error_raises_error(self, mock_get, service):
        mock_get.side_effect = requests.HTTPError("500 Error")

        with pytest.raises(ExchangeRateError):
            service.get_btc_to_usd_rate()

    @patch('requests.get')
    def test_invalid_json_raises_error(self, mock_get, service):
        mock_resp = Mock()
        mock_resp.json.return_value = {'invalid': 'format'}
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        with pytest.raises(ExchangeRateError):
            service.get_btc_to_usd_rate()

    @patch('requests.get')
    def test_satoshis_to_usd_correct_conversion(self, mock_get, service, mock_api_response):
        mock_get.return_value = mock_api_response
        usd = service.satoshis_to_usd(100_000_000)

        assert usd == Decimal('45000.50')

    @patch('requests.get')
    def test_satoshis_to_usd_fractional_btc(self, mock_get, service, mock_api_response):
        mock_get.return_value = mock_api_response
        usd = service.satoshis_to_usd(50_000_000)

        assert usd == Decimal('22500.25')

    @patch('requests.get')
    def test_satoshis_to_usd_zero(self, mock_get, service, mock_api_response):
        mock_get.return_value = mock_api_response
        assert service.satoshis_to_usd(0) == Decimal('0')

    def test_satoshis_to_usd_negative_raises_error(self, service):
        with pytest.raises(ValueError, match="cannot be negative"):
            service.satoshis_to_usd(-1000)

    @patch('requests.get')
    def test_btc_to_usd_correct_conversion(self, mock_get, service, mock_api_response):
        mock_get.return_value = mock_api_response
        usd = service.btc_to_usd(Decimal('1.0'))

        assert usd == Decimal('45000.50')

    @patch('requests.get')
    def test_btc_to_usd_fractional_amounts(self, mock_get, service, mock_api_response):
        mock_get.return_value = mock_api_response
        usd = service.btc_to_usd(Decimal('0.5'))

        assert usd == Decimal('22500.25')

    @patch('requests.get')
    def test_btc_to_usd_zero(self, mock_get, service, mock_api_response):
        mock_get.return_value = mock_api_response
        assert service.btc_to_usd(Decimal('0')) == Decimal('0')

    def test_btc_to_usd_negative_raises_error(self, service):
        with pytest.raises(ValueError, match="cannot be negative"):
            service.btc_to_usd(Decimal('-1.0'))

    @patch('requests.get')
    def test_decimal_precision_maintained(self, mock_get, service):
        mock_resp = Mock()
        mock_resp.json.return_value = {
            'data': {
                'currency': 'BTC',
                'rates': {
                    'USD': '45000.123456'
                }
            }
        }
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        rate = service.get_btc_to_usd_rate()
        assert rate == Decimal('45000.123456')