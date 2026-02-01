import secrets
import re


def generate_api_key() -> str:
    return secrets.token_urlsafe(32)

def validate_api_key_format(api_key: str) -> bool:
    if not isinstance(api_key, str):
        return False

    if len(api_key) != 43:
        return False

    return bool(re.match(r'^[A-Za-z0-9_-]+$', api_key))