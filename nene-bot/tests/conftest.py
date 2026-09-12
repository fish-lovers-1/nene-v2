from collections.abc import AsyncIterator

import discord.ext.test as dpytest
import pytest
import pytest_asyncio

from db.Base import Base
from db.Database import Database
from nene.Nene import Nene


@pytest.fixture(autouse=True)
def test_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GUILD_ID", "123456")
    monkeypatch.setenv("BOT_CHANNEL_ID", "123456")
    monkeypatch.setenv("GITHUB_SHA", "123456")


@pytest_asyncio.fixture
async def db() -> AsyncIterator[Database]:
    db = Database("sqlite+aiosqlite:///:memory:")
    try:
        await db.init()
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield db
    finally:
        await db.close()


@pytest_asyncio.fixture
async def test_nene(db: Database) -> AsyncIterator[Nene]:
    nene = Nene(discord_token="FAKE-TOKEN", db=db)
    await nene._async_setup_hook()
    await nene._add_commands()
    dpytest.configure(nene)

    yield nene

    await dpytest.empty_queue()
