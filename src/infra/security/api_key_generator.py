import secrets
import re

from src.core.interfaces.api_key_generator import ApiKeyGeneratorInterface

class ApiKeyGenerator(ApiKeyGeneratorInterface):
    EXPECTED_KEY_LENGTH = 43
    KEY_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')

    def generate_api_key(self) -> str:
        return secrets.token_urlsafe(32)

    def validate_api_key_format(self, api_key: str) -> bool:
        if not isinstance(api_key, str):
            return False

        if len(api_key) != self.EXPECTED_KEY_LENGTH:
            return False

        return bool(self.KEY_PATTERN.match(api_key))