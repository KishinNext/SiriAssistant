import logging
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.auth.utils import get_secrets

secrets = get_secrets()

DB_CONFIG = f"postgresql+asyncpg://{secrets['database']['user']}:{secrets['database']['password']}@{secrets['database']['host']}:{secrets['database']['port']}/{secrets['database']['database']}"  # noqa


async def check_connection():
    try:
        engine = create_async_engine(DB_CONFIG, echo=False, future=True)
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            return True
    except TimeoutError as e:
        raise e
    except Exception as e:
        logging.error('Database connection error, check the database configuration, details: %s', e)
        raise e


class DatabaseSession:

    def __init__(self):
        self.engine = create_async_engine(DB_CONFIG, echo=False, future=True)
        self.session = sessionmaker(self.engine, expire_on_commit=True, class_=AsyncSession)

    @asynccontextmanager
    async def session_scope(self):
        session = self.session()

        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


db = DatabaseSession()
