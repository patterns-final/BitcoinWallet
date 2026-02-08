from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.core.services.user_service import UserRegistrationResult


class UserCreateRequest(BaseModel):
    pass

class UserCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    api_key: str

    @classmethod
    def from_result(cls, result: UserRegistrationResult) -> UserCreateResponse:
        return cls(
            api_key=result.api_key
        )