import asyncio
import logging
import sys

import discord
from dishka import make_async_container

from clients.provider import HttpProvider
from clients.registry import client_provider
from config import ConfigProvider, EnvConfig
from db.Database import Database
from db.provider import DbProvider
from nene.Nene import Nene
from services.provider import Services
from services.registry import service_provider

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
        client_provider,
        service_provider,
    )
    try:
        env = await container.get(EnvConfig)
        db = await container.get(Database)
        services = await container.get(Services)

        nene = Nene(
            env=env,
            db=db,
            services=services,
        )
        await nene.nene_start()
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
