import os

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

database_url = os.environ["DATABASE_URL"]

engine = create_async_engine(
    database_url,
)

session_factory = async_sessionmaker(engine)
