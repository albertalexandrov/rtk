from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_session
from app.repositories import UsersRepository


async def get_users_repository(session: AsyncSession = Depends(get_session)):
    return UsersRepository(session)
