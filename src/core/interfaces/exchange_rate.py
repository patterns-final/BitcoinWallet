from abc import ABC, abstractmethod
from decimal import Decimal

class ExchangeRateInterface(ABC):
    @abstractmethod
    def get_btc_to_usd_rate(self) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def satoshis_to_usd(self, satoshis: int) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def btc_to_usd(self, btc: Decimal) -> Decimal:
        raise NotImplementedError
