import requests
from decimal import Decimal

from src.core.domain.interfaces.exchange_rate import ExchangeRateInterface, ExchangeRateError


class ExchangeRateService(ExchangeRateInterface):
    SATOSHIS_PER_BTC = 100_000_000
    API_URL = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"

    def get_btc_to_usd_rate(self) -> Decimal:
        try:
            response = requests.get(self.API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            rate = Decimal(str(data['data']['rates']['USD']))
            return rate

        except (requests.RequestException, KeyError, ValueError, TypeError) as e:
            raise ExchangeRateError(f"Failed to fetch BTC rate: {str(e)}")

    def satoshis_to_usd(self, satoshis: int) -> Decimal:
        if satoshis < 0:
            raise ValueError("Satoshis cannot be negative")

        btc = Decimal(satoshis) / Decimal(self.SATOSHIS_PER_BTC)
        return self.btc_to_usd(btc)

    def btc_to_usd(self, btc: Decimal) -> Decimal:
        if btc < 0:
            raise ValueError("BTC amount cannot be negative")

        rate = self.get_btc_to_usd_rate()
        return btc * rate