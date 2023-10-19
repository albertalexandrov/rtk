import logging
import os
import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import URL, Connection, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

LOGGER = logging.getLogger(__name__)


def generate_test_database() -> str:
    """Генерирует название тестовой БД."""

    timestamp = round(time.time())

    return f"test_{settings.db.database}_{timestamp}"


async def create_database(url: URL, database: str) -> None:
    """Создает тестовую БД."""

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        LOGGER.info(f"Создание тестовой БД {database}")
        await conn.execute(
            text(f'CREATE DATABASE "{database}" ENCODING "utf8" TEMPLATE template1')
        )
        LOGGER.info(f"Тестовая БД {database} создана")

    await engine.dispose()


def apply_migrations(connection: Connection):
    base_dir = Path(__file__).resolve().parent.parent
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
    alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")


async def migrate(url: URL, database: str) -> None:
    """Применяет миграции alembic."""

    url = url.set(database=database)
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        LOGGER.info(f"Применение миграций к тестовой БД {database}")
        await conn.run_sync(apply_migrations)
        LOGGER.info(f"Миграции к тестовой БД {database} применены")

    await engine.dispose()


async def drop_database(url: URL, database: str) -> None:
    """Удаляет тестовую БД."""

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        LOGGER.info(f"Удаление тестовой БД {database}")
        await conn.execute(text(f'DROP DATABASE "{database}"'))
        LOGGER.info(f"Тестовая БД {database} удалена")

    await engine.dispose()
