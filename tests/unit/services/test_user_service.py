import pytest
from unittest.mock import Mock
from src.core.use_cases.user_service import UserService, UserRegistrationResult
from src.core.domain.models import User
from src.core.domain.interfaces.api_key_generator import ApiKeyGeneratorInterface
from src.core.domain.interfaces import UserRepositoryInterface


class TestUserService:
    @pytest.fixture
    def mock_user_repository(self):
        return Mock(spec=UserRepositoryInterface)

    @pytest.fixture
    def mock_api_key_generator(self):
        return Mock(spec=ApiKeyGeneratorInterface)

    @pytest.fixture
    def user_service(self, mock_user_repository, mock_api_key_generator):
        return UserService(
            user_repository=mock_user_repository,
            api_key_generator=mock_api_key_generator
        )

    def test_register_user_success(self, user_service, mock_api_key_generator, mock_user_repository):
        expected_api_key = "test_api_key_12345"
        mock_api_key_generator.generate_api_key.return_value = expected_api_key
        result = user_service.register_user()
        assert isinstance(result, UserRegistrationResult)
        assert result.api_key == expected_api_key
        assert result.user_id is not None
        assert len(result.user_id) > 0
        mock_api_key_generator.generate_api_key.assert_called_once()
        mock_user_repository.save.assert_called_once()
        saved_user = mock_user_repository.save.call_args[0][0]
        assert isinstance(saved_user, User)
        assert saved_user.api_key == expected_api_key
        assert saved_user.id is not None

    def test_register_user_generates_unique_id(self, user_service, mock_api_key_generator, mock_user_repository):
        mock_api_key_generator.generate_api_key.return_value = "api_key"
        result1 = user_service.register_user()
        result2 = user_service.register_user()
        assert result1.user_id != result2.user_id

    def test_register_user_creates_user_with_empty_wallet_list(self, user_service, mock_api_key_generator,
                                                               mock_user_repository):
        mock_api_key_generator.generate_api_key.return_value = "api_key"
        user_service.register_user()
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.wallet_ids == []

    def test_register_user_raises_error_when_user_id_is_none(self, user_service, mock_api_key_generator,
                                                             mock_user_repository, monkeypatch):
        mock_api_key_generator.generate_api_key.return_value = "api_key"
        def mock_create(api_key: str) -> User:
            return User(api_key=api_key, id=None)
        monkeypatch.setattr(User, "create", staticmethod(mock_create))
        with pytest.raises(ValueError, match="Failed to create user"):
            user_service.register_user()
        mock_user_repository.save.assert_not_called()

    def test_register_user_repository_save_is_called_with_correct_user(self, user_service, mock_api_key_generator,
                                                                       mock_user_repository):
        expected_api_key = "test_api_key"
        mock_api_key_generator.generate_api_key.return_value = expected_api_key
        result = user_service.register_user()
        mock_user_repository.save.assert_called_once()
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.id == result.user_id
        assert saved_user.api_key == result.api_key

    def test_authenticate_user_success(self, user_service, mock_api_key_generator, mock_user_repository):
        valid_api_key = "valid_api_key_12345"
        expected_user = User(id="user_123", api_key=valid_api_key)
        mock_api_key_generator.validate_api_key_format.return_value = True
        mock_user_repository.get_user_by_api_key.return_value = expected_user
        result = user_service.authenticate_user(valid_api_key)
        assert result == expected_user
        mock_api_key_generator.validate_api_key_format.assert_called_once_with(valid_api_key)
        mock_user_repository.get_user_by_api_key.assert_called_once_with(valid_api_key)

    def test_authenticate_user_with_invalid_format_returns_none(self, user_service, mock_api_key_generator,
                                                                mock_user_repository):
        invalid_api_key = "invalid_key"
        mock_api_key_generator.validate_api_key_format.return_value = False
        result = user_service.authenticate_user(invalid_api_key)
        assert result is None
        mock_api_key_generator.validate_api_key_format.assert_called_once_with(invalid_api_key)
        mock_user_repository.get_user_by_api_key.assert_not_called()

    def test_authenticate_user_with_nonexistent_key_returns_none(self, user_service, mock_api_key_generator,
                                                                 mock_user_repository):
        nonexistent_api_key = "valid_format_but_not_found"
        mock_api_key_generator.validate_api_key_format.return_value = True
        mock_user_repository.get_user_by_api_key.return_value = None
        result = user_service.authenticate_user(nonexistent_api_key)
        assert result is None
        mock_api_key_generator.validate_api_key_format.assert_called_once_with(nonexistent_api_key)
        mock_user_repository.get_user_by_api_key.assert_called_once_with(nonexistent_api_key)

    def test_authenticate_user_validates_format_before_repository_lookup(self, user_service, mock_api_key_generator,
                                                                         mock_user_repository):
        invalid_api_key = "bad_format"
        mock_api_key_generator.validate_api_key_format.return_value = False
        user_service.authenticate_user(invalid_api_key)
        mock_user_repository.get_user_by_api_key.assert_not_called()

    def test_authenticate_user_with_empty_string(self, user_service, mock_api_key_generator, mock_user_repository):
        empty_api_key = ""
        mock_api_key_generator.validate_api_key_format.return_value = False
        result = user_service.authenticate_user(empty_api_key)
        assert result is None
        mock_api_key_generator.validate_api_key_format.assert_called_once_with(empty_api_key)

    def test_authenticate_user_with_whitespace_key(self, user_service, mock_api_key_generator, mock_user_repository):
        whitespace_key = "   "
        mock_api_key_generator.validate_api_key_format.return_value = False
        result = user_service.authenticate_user(whitespace_key)
        assert result is None

    def test_full_registration_and_authentication_flow(self, user_service, mock_api_key_generator,
                                                       mock_user_repository):
        generated_api_key = "generated_api_key_xyz"
        mock_api_key_generator.generate_api_key.return_value = generated_api_key
        mock_api_key_generator.validate_api_key_format.return_value = True
        saved_user_capture = None
        def capture_save(user):
            nonlocal saved_user_capture
            saved_user_capture = user
        mock_user_repository.save.side_effect = capture_save
        mock_user_repository.get_user_by_api_key.side_effect = lambda key: saved_user_capture if key == generated_api_key else None
        registration_result = user_service.register_user()
        authenticated_user = user_service.authenticate_user(registration_result.api_key)
        assert authenticated_user is not None
        assert authenticated_user.id == registration_result.user_id
        assert authenticated_user.api_key == registration_result.api_key

    def test_register_multiple_users_with_different_api_keys(self, user_service, mock_api_key_generator,
                                                             mock_user_repository):
        mock_api_key_generator.generate_api_key.side_effect = ["key1", "key2", "key3"]
        result1 = user_service.register_user()
        result2 = user_service.register_user()
        result3 = user_service.register_user()
        assert result1.api_key == "key1"
        assert result2.api_key == "key2"
        assert result3.api_key == "key3"
        assert len({result1.api_key, result2.api_key, result3.api_key}) == 3

    def test_service_uses_injected_dependencies(self, mock_user_repository, mock_api_key_generator):
        service = UserService(
            user_repository=mock_user_repository,
            api_key_generator=mock_api_key_generator
        )
        assert service._user_repository is mock_user_repository
        assert service._api_key_generator is mock_api_key_generator