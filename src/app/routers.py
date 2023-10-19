import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from starlette import status

from app.models import User
from app.pagination import PageNumberPagination, PaginatedResponse
from app.schemas import UserCreateData, UserSchema, UserUpdateData
from app.usecases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    UpdateUserUseCase,
)

LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("", response_model=PaginatedResponse[UserSchema])
async def list_users(paginator: PageNumberPagination = Depends()):
    stmt = select(User)

    return await paginator.get_page(stmt=stmt)


@router.get("/{user_id}", response_model=UserSchema, summary="Возвращает пользователя")
async def get_user(user_id: int, use_case: GetUserUseCase = Depends()):
    return await use_case.get_user_or_404(user_id)


@router.post(
    "",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создает пользователя",
)
async def create_user(
    create_data: UserCreateData, use_case: CreateUserUseCase = Depends()
):
    return await use_case.create_user(create_data)


@router.patch(
    "/{user_id}", response_model=UserSchema, summary="Обновление пользователя"
)
async def update_user(
    user_id: int, update_data: UserUpdateData, use_case: UpdateUserUseCase = Depends()
):
    return await use_case.update_user_or_404(user_id, update_data)


@router.delete("/{user_id}", summary="Удаляет пользователя")
async def delete_user(user_id: int, use_case: DeleteUserUseCase = Depends()):
    await use_case.delete_user_or_404(user_id)

    return "Пользователь удален"
