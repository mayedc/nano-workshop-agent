"""Demo entry point - uses SQLite + MemoryStorage, no external services needed."""
import asyncio
import os

# Override settings before any app imports
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./demo.db")

import uvicorn
from app.main import app
from app.db.base import Base
from app.db.session import engine
from app.services.storage import MemoryStorage, set_storage


async def init_demo():
    """Create tables and set up in-memory storage."""
    import app.models  # ensure all models are registered with Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    set_storage(MemoryStorage())
    print("Demo database initialized at demo.db")
    print("Using MemoryStorage (no MinIO required)")


if __name__ == "__main__":
    asyncio.run(init_demo())
    print("=" * 60)
    print("Nano Workshop Agent - Demo Mode")
    print("Using SQLite database (no PostgreSQL required)")
    print("Using MemoryStorage (no MinIO required)")
    print("Using Mock AI Providers (no API keys required)")
    print("=" * 60)
    uvicorn.run("demo_main:app", host="0.0.0.0", port=8000, reload=False)
