import asyncio
import logging
import sys

import discord
from dishka import make_async_container

from clients.provider import ClientProvider, HttpProvider
from config import ConfigProvider, EnvConfig
from db.Database import Database
from db.provider import DbProvider
from nene.Nene import Nene
from services.provider import ServiceProvider
from services.trivia_service import TriviaService

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

discord.utils.setup_logging(
    level=logging.INFO,
    root=True,
)
logging.getLogger("discord").setLevel(logging.WARNING)


async def main():
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        HttpProvider(),
        ClientProvider(),
        ServiceProvider(),
    )
    try:
        env = await container.get(EnvConfig)
        db = await container.get(Database)
        trivia_service = await container.get(TriviaService)

        nene = Nene(
            env=env,
            db=db,
            trivia_service=trivia_service,
        )
        await nene.nene_start()
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
