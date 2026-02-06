from fastapi import APIRouter, Depends

from src.api.dependencies import get_user_service
from src.api.schemas.user import UserCreateResponse, UserCreateRequest
from src.core.services.user_service import UserService

router = APIRouter(prefix="/users")

@router.post("/", response_model=UserCreateResponse, status_code=201)
def create_user(user_service: UserService = Depends(get_user_service)):
    user = user_service.register_user()
    return UserCreateResponse.from_result(user)
