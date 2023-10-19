from app.database import SessionLocal


async def get_session():
    """Provide a transactional scope around a series of operations."""

    session = SessionLocal()
    print("получение сессии")
    try:
        yield session
    finally:
        print("закрытие сесиси")
        await session.close()
