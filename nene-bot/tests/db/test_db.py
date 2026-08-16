import asyncio
import json
import os
import uuid
from collections.abc import AsyncGenerator, Generator
from contextlib import ExitStack, asynccontextmanager, contextmanager

import pytest
from alembic import command
from alembic.config import Config
from pytest_mock import MockerFixture
from sqlalchemy import URL, Engine, create_engine, make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemydiff.comparer import Comparer
from testcontainers.community.postgres import PostgresContainer

from db.Base import Base
from db.utils import get_all_db_tables


@pytest.fixture
def postgres():
    with PostgresContainer(
        "postgres:18", username="test", password="test", dbname="test"
    ) as postgres:
        yield postgres


@asynccontextmanager
async def async_engine(url: str | URL) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(url)
    try:
        yield engine

    finally:
        await engine.dispose()


@contextmanager
def sync_engine(url: str) -> Generator[Engine, None]:
    engine = create_engine(url)

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.mark.asyncio
async def test_migrations_match_models(
    postgres: PostgresContainer, mocker: MockerFixture
):
    migrated_db = f"migration_test_{uuid.uuid4().hex}"
    orm_db = f"orm_test_{uuid.uuid4().hex}"

    url = make_url(postgres.get_connection_url()).set(
        drivername="postgresql+asyncpg",
    )

    async with async_engine(url) as engine, engine.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f'CREATE DATABASE "{migrated_db}"'))
        await conn.execute(text(f'CREATE DATABASE "{orm_db}"'))

    migrated_url = url.set(database=migrated_db).render_as_string(hide_password=False)
    cfg = Config("alembic.ini")
    mocker.patch.dict(
        os.environ,
        {"DATABASE_URL": migrated_url},
    )
    await asyncio.to_thread(command.upgrade, cfg, "head")
    async with async_engine(migrated_url) as engine, engine.begin() as conn:
        # need to drop this cause the orm created db wont have this migration table
        await conn.execute(text("DROP TABLE alembic_version"))

    orm_url = url.set(database=orm_db).render_as_string(hide_password=False)
    async with async_engine(orm_url) as engine, engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    migrated_url_sync = url.set(
        database=migrated_db, drivername="postgresql+psycopg"
    ).render_as_string(hide_password=False)
    orm_url_sync = url.set(
        database=orm_db, drivername="postgresql+psycopg"
    ).render_as_string(hide_password=False)

    with ExitStack() as stack:
        migrated_engine = stack.enter_context(sync_engine(migrated_url_sync))
        orm_engine = stack.enter_context(sync_engine(orm_url_sync))
        result = Comparer(migrated_engine, orm_engine).compare(
            one_alias="migrated schema", two_alias="ORM schema"
        )
        assert result.is_match, (
            f"Migrated schema (one) differs from expected ORM schema (two) {json.dumps({k: v for k, v in result.errors.items() if v != {}}, indent=2)}"
        )


def test_all_tables_have_name():
    assert all(hasattr(table, "__tablename__") for table in get_all_db_tables())
