import asyncio
import logging

import pytest
from sqlalchemy import URL

from app.config import settings
from tests.database import generate_test_database, create_database, migrate, drop_database

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def create_database_and_apply_migrations():
    """Создание тестовой БД и применение миграций."""

    database = generate_test_database()
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
