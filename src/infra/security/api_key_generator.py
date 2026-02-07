import secrets
import re
import math

from src.core.domain.interfaces.api_key_generator import ApiKeyGeneratorInterface

class ApiKeyGenerator(ApiKeyGeneratorInterface):
    TOKEN_BYTES = 32

    EXPECTED_KEY_LENGTH = math.ceil(TOKEN_BYTES * 4 / 3)
    KEY_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')

    def generate_api_key(self) -> str:
        return secrets.token_urlsafe(self.TOKEN_BYTES)

    def validate_api_key_format(self, api_key: str) -> bool:
        if not isinstance(api_key, str):
            return False

        if len(api_key) != self.EXPECTED_KEY_LENGTH:
            return False

        return bool(self.KEY_PATTERN.match(api_key))