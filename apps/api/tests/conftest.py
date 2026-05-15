import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def override_get_db(db):
    """Override the FastAPI dependency to use the test SQLite DB."""
    from app.db.session import get_db as original_get_db

    async def _override():
        yield db

    from app.main import app

    app.dependency_overrides[original_get_db] = _override
    yield
    app.dependency_overrides.clear()
