"""Касательно терминологии я предпочитаю использовать use case вместо service - на мой взгляд оно
лучше отражает суть (одного) действия.  К тому же use case - термин системного анализа
"""

import logging

import sqlalchemy.exc
from fastapi import Depends

from app.dependencies.repositories import get_users_repository
from app.exceptions import Http404
from app.repositories import UsersRepository
from app.schemas import UserCreateData, UserUpdateData

LOGGER = logging.getLogger(__name__)


class GetUserUseCase:
    def __init__(
        self, users_repository: UsersRepository = Depends(get_users_repository)
    ):
        self._users_repository = users_repository

    async def get_user_or_404(self, user_id: int):
        try:
            user = await self._users_repository.get(pk_value=user_id)
        except sqlalchemy.exc.NoResultFound:
            raise Http404

        return user


class CreateUserUseCase:
    def __init__(
        self, users_repository: UsersRepository = Depends(get_users_repository)
    ):
        self._users_repository = users_repository

    async def create_user(self, create_data: UserCreateData):
        user = await self._users_repository.create(**create_data.model_dump())
        await self._users_repository.commit()
        await self._users_repository.refresh(user)

        return user


class UpdateUserUseCase:
    def __init__(
        self, users_repository: UsersRepository = Depends(get_users_repository)
    ):
        self._users_repository = users_repository

    async def update_user_or_404(self, user_id: int, update_data: UserUpdateData):
        try:
            user = await self._users_repository.get(pk_value=user_id)
        except sqlalchemy.exc.NoResultFound:
            raise Http404

        user = await self._users_repository.update(
            user, **update_data.model_dump(exclude_unset=True)
        )
        await self._users_repository.commit()
        await self._users_repository.refresh(user)

        return user


class DeleteUserUseCase:
    def __init__(
        self, users_repository: UsersRepository = Depends(get_users_repository)
    ):
        self._users_repository = users_repository

    async def delete_user_or_404(self, user_id: int):
        try:
            user = await self._users_repository.get(pk_value=user_id)
        except sqlalchemy.exc.NoResultFound:
            raise Http404

        await self._users_repository.delete(user)
        await self._users_repository.commit()
