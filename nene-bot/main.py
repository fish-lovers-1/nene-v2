import asyncio
import logging
import os
import sys

import discord
from dotenv import load_dotenv

from db.Database import Database
from nene.Nene import Nene

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

discord.utils.setup_logging(
    level=logging.INFO,
    root=True,
)
logging.getLogger("discord").setLevel(logging.WARNING)
load_dotenv()


async def main():
    database_url = os.environ["DATABASE_URL"]
    db = Database(database_url)
    await db.init()

    token = os.environ["DISCORD_TOKEN"]
    nene = Nene(discord_token=token, db=db)
    await nene.nene_start()


if __name__ == "__main__":
    asyncio.run(main())
