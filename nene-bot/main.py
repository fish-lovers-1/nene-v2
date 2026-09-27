import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler

import discord
from discord.abc import MISSING
from dishka import AsyncContainer, make_async_container

from clients.provider import HttpProvider
from clients.registry import client_provider
from config import ConfigProvider, EnvConfig
from db.Database import Database
from db.provider import DbProvider
from nene.Nene import Nene
from services.registry import service_provider

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def setup_logging(container: AsyncContainer):
    config = await container.get(EnvConfig)

    log_handler = (
        RotatingFileHandler(
            filename="/app/logs/nene.log", maxBytes=10000000, backupCount=5
        )
        if config.ENVIRONMENT == "prod"
        else MISSING
    )

    discord.utils.setup_logging(
        handler=log_handler,
        level=logging.INFO,
        root=True,
    )

    logging.getLogger("discord").setLevel(logging.WARNING)


async def main():
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        HttpProvider(),
        client_provider,
        service_provider,
    )
    await setup_logging(container)

    try:
        env = await container.get(EnvConfig)
        db = await container.get(Database)

        nene = Nene(
            env=env,
            db=db,
            container=container,
        )
        await nene.nene_start()
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
