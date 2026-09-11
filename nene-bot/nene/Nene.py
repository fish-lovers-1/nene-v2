import logging
import os

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from clients.opentdb import OpenTDBClient
from commands.greet import Greet
from commands.lore_command import LoreCommand
from commands.trivia import Trivia
from db.Database import Database
from nene.utils import sync_users
from services.trivia_service import TriviaService

logger = logging.getLogger(__name__)


class Nene(commands.Bot):
    def __init__(self, discord_token: str, db: Database):
        GUILD_ID = os.environ["GUILD_ID"]
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents, command_prefix="Nene ")
        self._token = discord_token
        self.db = db
        self.guild = discord.Object(GUILD_ID)

    async def _add_commands(self):
        async with aiohttp.ClientSession() as session:
            open_tdb_client = OpenTDBClient(session)
            trivia_service = TriviaService(open_tdb_client)

            await self.add_cog(Greet(self))
            await self.add_cog(LoreCommand(self, self.db))
            await self.add_cog(Trivia(self, trivia_service))

    async def _sync_app_commands(self):
        logger.info(
            "Global tree: %s",
            [c.name for c in self.tree.get_commands()],
        )

        logger.info(
            "Guild tree: %s",
            [c.name for c in self.tree.get_commands(guild=self.guild)],
        )
        logger.info("about to sync commands")
        self.tree.copy_global_to(guild=self.guild)
        synced = await self.tree.sync(guild=self.guild)
        if len(synced) > 0:
            logger.info(
                "Synced application commands: %s",
                ", ".join(c.name for c in synced),
            )

    async def setup_hook(self):
        logger.info("Starting Nene")
        self.tree.on_error = self.on_tree_error  # ty: ignore[invalid-assignment]
        await self._add_commands()
        await self._sync_app_commands()
        await sync_users(self.db, self.fetch_guilds())
        logger.info("Nene started")

    async def on_ready(self):
        logger.info(f"Nene signed in as {self.user}")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        await ctx.send(f"Error: {error}")

    async def on_tree_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        await interaction.response.send_message(f"Error: {error}")

    async def nene_start(self):
        await self.start(self._token)
