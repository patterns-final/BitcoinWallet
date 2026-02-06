import requests
from decimal import Decimal
from datetime import datetime, timedelta


from src.core.interfaces.exchange_rate import ExchangeRateInterface

class ExchangeRateService(ExchangeRateInterface):
    SATOSHIS_PER_BTC = 100_000_000
    CACHE_DURATION_SECONDS = 60
    API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    def __init__(self):
        self._cached_rate: Decimal | None = None
        self._cache_timestamp: datetime | None = None

    def get_btc_to_usd_rate(self) -> Decimal:

        if self._is_cache_valid():
            return self._cached_rate

        response = requests.get(self.API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        rate = Decimal(str(data['bitcoin']['usd']))

        self._cached_rate = rate
        self._cache_timestamp = datetime.now()

        return rate

    def satoshis_to_usd(self, satoshis: int) -> Decimal:
        btc = Decimal(satoshis) / Decimal(self.SATOSHIS_PER_BTC)
        return self.btc_to_usd(btc)

    def btc_to_usd(self, btc: Decimal) -> Decimal:
        rate = self.get_btc_to_usd_rate()
        return btc * rate

    def _is_cache_valid(self)-> bool:
        if self._cached_rate is None or self._cache_timestamp is None:
            return False

        elapsed = datetime.now() - self._cache_timestamp
        return elapsed.total_seconds() < self.CACHE_DURATION_SECONDS


