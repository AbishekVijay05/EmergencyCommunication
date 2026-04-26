# =============================================================================
# Prediction Database Setup
# =============================================================================
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

class Base(DeclarativeBase):
    pass

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False, pool_size=20, max_overflow=10)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        from app.models.prediction import PredictionRule, Prediction  # noqa
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
