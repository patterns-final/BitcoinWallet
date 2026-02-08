from src.api.schemas.user import UserCreateResponse
from src.core.services.user_service import UserRegistrationResult

def test_user_create_response_from_result():
    result = UserRegistrationResult(
        user_id="test-uuid-123",
        api_key="sk_test_key"
    )

    response = UserCreateResponse.from_result(result)

    assert response.api_key == "sk_test_key"
    assert isinstance(response, UserCreateResponse)