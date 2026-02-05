from dataclasses import dataclass

from src.core.interfaces.api_key_generator import ApiKeyGeneratorInterface
from src.core.interfaces.user_repository import UserRepositoryInterface
from src.core.models.user import User

@dataclass
class UserRegistrationResult:
    user_id: str
    api_key: str


class UserService:

    def __init__(
            self,
            user_repository: UserRepositoryInterface,
            api_key_generator: ApiKeyGeneratorInterface
    ) -> None:
        self._user_repository = user_repository
        self._api_key_generator = api_key_generator

    def register_user(self) -> UserRegistrationResult:
        api_key = self._api_key_generator.generate_api_key()
        user = User.create(api_key=api_key)

        if user.id is None:
            raise ValueError("Failed to create user")

        self._user_repository.save(user)

        return UserRegistrationResult(
            user_id=user.id,
            api_key=api_key
        )

    def authenticate_user(self, api_key: str) -> User | None:
        if not self._api_key_generator.validate_api_key_format(api_key):
            return None

        return self._user_repository.get_user_by_api_key(api_key)