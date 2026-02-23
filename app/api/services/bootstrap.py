import app.db.models  # noqa: F401
from app.db.models.base import Base, engine


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)