from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

DATABASE_URL = (
    f"postgresql+asyncpg://{Config.USER_DB_USER}:{Config.USER_DB_PASSWORD}"
    f"@{Config.USER_DB_HOST}:{Config.USER_DB_PORT}/{Config.USER_DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()