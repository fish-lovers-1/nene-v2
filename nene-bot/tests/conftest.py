from collections.abc import AsyncIterator

import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from dishka import AsyncContainer, make_async_container

from clients.provider import HttpProvider
from clients.registry import client_provider
from config import ConfigProvider, EnvConfig
from db.Base import Base
from db.Database import Database
from db.provider import DbProvider
from nene.Nene import Nene
from services.registry import service_provider


@pytest.fixture(autouse=True)
def test_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISCORD_TOKEN", "FAKE-TOKEN")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("GUILD_ID", "123456")
    monkeypatch.setenv("BOT_CHANNEL_ID", "123456")
    monkeypatch.setenv("GITHUB_SHA", "123456")


@pytest_asyncio.fixture
async def container() -> AsyncIterator[AsyncContainer]:
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        HttpProvider(),
        client_provider,
        service_provider,
    )
    try:
        yield container
    finally:
        await container.close()


@pytest_asyncio.fixture
async def db(container: AsyncContainer) -> AsyncIterator[Database]:
    db = await container.get(Database)
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield db


@pytest_asyncio.fixture
async def test_nene(container: AsyncContainer, db: Database) -> AsyncIterator[Nene]:
    nene = Nene(
        env=await container.get(EnvConfig),
        db=db,
        container=container,
    )
    await nene._async_setup_hook()
    await nene._add_commands()
    dpytest.configure(nene)

    yield nene

    await dpytest.empty_queue()
