from typing import Generic, TypeVar

from fastapi import Depends, Query
from pydantic import AnyUrl, BaseModel, Field
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.dependencies.database import get_session

M = TypeVar("M")


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description="Общее количество записей", example=22)
    next: AnyUrl | None = Field(
        description="Ссылка на следующую страницу",
        example="http://localhost:8000/users?page=3&page_size=10",
    )
    previous: AnyUrl | None = Field(
        description="Ссылка на предыдущую страницу",
        example="http://localhost:8000/users?page=1&page_size=10",
    )
    results: list[M] = Field(description="Результат")


class PageNumberPagination:
    """Пагинатор.

    Notes:
        Библиотека https://github.com/uriyyo/fastapi-pagination мне не понравилась из-за
        странной инициализации
        Здесь обходимся без репозиториев, тк по моему мнению репозиторий не должен работать
        с фильтрами fastapi_filter.Filter
        Предлагается рассматривать пагинатор как частный случай пользовательского кейса (use case)

    """

    max_results = 100

    def __init__(
        self,
        request: Request,
        page: int = Query(1, gt=0),
        page_size: int = Query(10, gt=0),
        session: AsyncSession = Depends(get_session),
    ):
        self._request = request
        self._session = session
        self._page = page
        self._page_size = (
            page_size if page_size <= self.max_results else self.max_results
        )

    async def get_page(self, stmt: Select) -> PaginatedResponse:
        """Возвращает результат пагинации в соответствии с фильтрами.

        Args:
            stmt: sql-запрос

        """

        count = await self._get_count(stmt)

        return PaginatedResponse(
            count=count,
            next=self._get_next_page(count),
            previous=self._get_previous_page(count),
            results=await self._get_results(stmt),
        )

    async def _get_count(self, stmt: Select) -> int:
        """Возвращает общее количество элементов.

        Args:
            stmt: sql-запрос

        """

        count = await self._session.scalar(
            select(func.count()).select_from(stmt.subquery())
        )

        return count

    def _get_next_page(self, count: int) -> str:
        """Возвращает ссылку на следующую страницу.

        Args:
            count: общее количество элементов

        """

        total_pages = self._get_total_pages(count)

        if self._page >= total_pages:
            return

        url = self._request.url.include_query_params(page=self._page + 1)

        return str(url)

    def _get_previous_page(self, count: int) -> str:
        """Возвращает ссылку на предыдущую страницу.

        Args:
            count: общее количество элементов

        """

        total_pages = self._get_total_pages(count)

        if not (1 < self._page <= total_pages):
            return

        url = self._request.url.include_query_params(page=self._page - 1)

        return str(url)

    def _get_total_pages(self, count: int) -> int:
        """Возвращает количество страниц.

        Args:
            count: общее количество элементов

        """

        return count // self._page_size + 1

    @property
    def offset(self):
        return (self._page - 1) * self._page_size

    async def _get_results(self, stmt: Select) -> list[M]:
        """Возвращает объекты.

        Args:
            stmt: sql-запрос

        Notes:
            stmt передаем снаружи, тк невозможно предусмотреть все кейсы,
            чтобы генерировать stmt внутри.  Также это видится неудобным

        """

        stmt = stmt.limit(self._page_size).offset(self.offset)
        results = await self._session.scalars(stmt)

        return results.all()
