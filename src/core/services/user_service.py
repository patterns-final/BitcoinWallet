from typing import Protocol, TypedDict

from src.infra.security.api_key import (
    generate_api_key,
    validate_api_key_format,
)

class User(TypedDict):
    id: int
    api_key: str


class UserRepositoryInterface(Protocol):

    def create_user(self, api_key: str) -> User:
        """axali useris sheqmna"""
        ...

    def get_user_by_api_key(self, api_key: str) -> User | None:
        """api-it povna useris"""
        ...


class UserService:

    def __init__(self, user_repository: UserRepositoryInterface) -> None:
        self._user_repository = user_repository

    def register_user(self) -> dict[str, str | int]:
        api_key = generate_api_key()
        user = self._user_repository.create_user(api_key=api_key)

        if not user:
            raise ValueError("Failed to create user")

        return {
            'api_key': api_key,
            'user_id': user['id']
        }

    def authenticate_user(self, api_key: str) -> User | None:
        if not validate_api_key_format(api_key):
            return None

        return self._user_repository.get_user_by_api_key(api_key)