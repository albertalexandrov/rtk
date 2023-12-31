import asyncio
import logging

import pytest
from httpx import AsyncClient
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from tests.database import (
    create_database,
    drop_database,
    generate_test_database,
    migrate,
)

from app.config import settings
from app.dependencies.database import get_session
from app.main import app
from app.repositories import UsersRepository

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def database():
    return generate_test_database()


@pytest.fixture(scope="session", autouse=True)
async def create_database_and_apply_migrations(database):
    """Создание тестовой БД и применение миграций."""

    url = URL.create(
        drivername=settings.db.drivername,
        host=settings.db.host,
        port=settings.db.port,
        username=settings.db.username,
        password=settings.db.password,
        # здесь без database, тк БД еще не создана и вызов engine.connect() будет провоцировать ошибку отсутствия БД
    )

    await create_database(url, database)
    await migrate(url, database)

    yield

    await drop_database(url, database)


@pytest.fixture
async def engine(database):
    url = URL.create(
        drivername=settings.db.drivername,
        host=settings.db.host,
        port=settings.db.port,
        username=settings.db.username,
        password=settings.db.password,
        database=database,
    )
    engine_ = create_async_engine(url)
    yield engine_
    await engine_.dispose()


@pytest.fixture
async def session(engine):
    session_ = AsyncSession(engine)
    session_.begin_nested()
    yield session_
    await session_.rollback()
    await session_.close()


@pytest.fixture
async def users_repository(session):
    return UsersRepository(session)


@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
async def session_override(session):
    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
