from abc import ABC, abstractmethod


class ApiKeyGeneratorInterface(ABC):
    @abstractmethod
    def generate_api_key(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_api_key_format(self, api_key: str) -> bool:
        raise NotImplementedError