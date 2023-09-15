# coding: utf-8

from contextlib import asynccontextmanager
from enum import Enum

from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from sqlalchemy.pool import QueuePool

from settings import DATABASES


class DBNames(Enum):
    examine = "main"
    general = "test"


try:
    db_connections = {
        "main": sessionmaker(
            bind=create_async_engine(
                'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}:{DB_PORT}/{DB_NAME}'.format(
                    DB_USER=DATABASES["main"]["user"],
                    DB_PASSWORD=DATABASES["main"]["password"],
                    DB_ADDRESS=DATABASES["main"]["address"],
                    DB_PORT=DATABASES["main"]["port"],
                    DB_NAME=DATABASES["main"]["name"],
                ),
                echo=False,
                #poolclass=NullPool,
                poolclass=QueuePool,
                pool_recycle=3600,
                pool_pre_ping=True,
                pool_use_lifo=True,
            ),
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        ),
        "test": sessionmaker(
            bind=create_async_engine(
                'sqlite+aiosqlite:///{}.db'.format(
                    DB_USER=DATABASES["test"]["name"],
                ),
                echo=False,
                #poolclass=NullPool,
                poolclass=QueuePool,
                pool_recycle=3600,
                pool_pre_ping=True,
                pool_use_lifo=True,
            ),
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        ),
    }
except BaseException:
    db_connections = {"main": None, "test": None}


@asynccontextmanager
async def get_session(bind="main") -> AsyncSession:
    session = db_connections.get(bind)()
    try:
        yield session
    finally:
        if session is not None:
            await session.close()
