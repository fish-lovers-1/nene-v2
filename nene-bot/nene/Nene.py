import logging

import discord
from discord.ext import commands

from commands.Greet import Greet
from db.Database import Database
from nene.utils import sync_users

logger = logging.getLogger(__name__)


class Nene(commands.Bot):
    def __init__(self, discord_token: str, db: Database):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents, command_prefix="Nene ")
        self._token = discord_token
        self.db = db

    async def setup_hook(self):
        logger.info("Starting Nene")
        await self.add_cog(Greet(self))
        await sync_users(self.db, self.fetch_guilds())
        logger.info("Nene started")

    async def on_ready(self):
        logger.info(f"Nene signed in as {self.user}")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        await ctx.send(f"Error: {error}")

    async def nene_start(self):
        await self.start(self._token)
