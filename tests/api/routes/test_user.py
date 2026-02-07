import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.api.dependencies import get_user_service
from src.core.services.user_service import UserRegistrationResult


@pytest.fixture
def client_with_mock():
    class MockUserService:
        def register_user(self):
            return UserRegistrationResult(user_id="mock-id", api_key="mock-key")

    app.dependency_overrides[get_user_service] = lambda: MockUserService()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_create_user_success(client_with_mock):
    response = client_with_mock.post("/users/")

    assert response.status_code == 201
    assert response.json() == {
        "id": "mock-id",
        "api_key": "mock-key"
    }