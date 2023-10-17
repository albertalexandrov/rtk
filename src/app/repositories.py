from typing import Any

import sqlalchemy.exc
from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class Repository:
    """Базовый репозиторий.

    Предполагается, что репозитории как слой доступа к хранилищам данных будут только выполнять запросы к ним,
    а если для запроса требуются данные, то данные подготавливаются снаружи.  В целом все, что хоть отдаленно
    напоминает бизнес-логику, предлагается выполнять снаружи, тк это не является обязанностью репозитория

    """

    model = None

    def __init__(self, session: AsyncSession):
        if self.model is None:
            raise ValueError(f'Не определен атрибут {self.__class__.__name__}.model')

        self._session = session

    async def create(self, **create_data):
        """Создание объекта.

        Args:
            create_data: данные, из которых должен быть создан объект

        """

        instance = self.model(**create_data)
        self._session.add(instance)

        return instance

    async def get(self, *whereclause: BinaryExpression, pk_value: Any = None):
        """Возвращает единственный объект.

        Args:
            whereclause: условия фильтрации
            pk_value: значение первичного ключа, если нужно получить объект по первичному ключу

        """

        if pk_value is not None:
            instance = await self._session.get(self.model, pk_value)

            if instance is None:
                raise sqlalchemy.exc.NoResultFound

            return instance

        stmt = select(self.model)

        if whereclause:
            stmt = stmt.where(*whereclause)

        result = await self._session.scalars(stmt)

        return result.one()

    async def update(self, instance, **update_data):
        """Обновление объекта.

        Args:
            instance: объект для обновления
            update_data: данные для обновления

        """

        for field, value in update_data.items():
            setattr(instance, field, value)

        self._session.add(instance)

        return instance

    async def delete(self, instance: object):
        """Удаляет объект.

        Args:
            instance: объект, который необходимо удалить

        """

        await self._session.delete(instance)

    async def commit(self):
        await self._session.commit()

    async def refresh(self, instance):
        await self._session.refresh(instance)


class UsersRepository(Repository):
    """Репозиторий для работы с пользователями."""

    model = User
