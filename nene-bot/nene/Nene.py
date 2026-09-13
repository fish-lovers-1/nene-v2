import logging
import traceback
from typing import Any, Final, override

import discord
from discord import TextChannel, app_commands
from discord.ext import commands
from dishka import AsyncContainer

from commands.greet import Greet
from commands.lore_command import LoreCommand
from commands.trivia import Trivia
from config import EnvConfig
from db.Database import Database
from nene.utils import sync_users
from services.trivia_service import TriviaService

logger = logging.getLogger(__name__)


def _get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    return intents


class Nene(commands.Bot):
    def __init__(self, env: EnvConfig, db: Database, container: AsyncContainer):
        self._env = env
        self._token = env.DISCORD_TOKEN
        self.db = db
        self._container = container

        self._bot_channel_id: Final[int] = env.BOT_CHANNEL_ID
        super().__init__(intents=_get_intents(), command_prefix="Nene ")
        self.guild = discord.Object(env.GUILD_ID)

        self._bot_channel: TextChannel | None = None

    async def _add_commands(self):
        trivia_service = await self._container.get(TriviaService)

        await self.add_cog(Greet(self))
        await self.add_cog(LoreCommand(self, self.db))
        await self.add_cog(Trivia(self, trivia_service))

    async def _sync_app_commands(self):
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

    async def _fetch_bot_channel(self):
        if self._bot_channel is not None:
            return self._bot_channel

        try:
            channel = await self.fetch_channel(self._bot_channel_id)

            if not isinstance(channel, TextChannel):
                raise TypeError(f"Expect a text channel, got {channel}")
        except Exception as e:
            logger.warning(f"Cannot fetch bot channel due to {e}")
            return

        self._bot_channel = channel
        return channel

    async def nene_says(self, message: str):
        channel = await self._fetch_bot_channel()

        if channel is None:
            return

        await channel.send(message)

    @override
    async def setup_hook(self):
        logger.info("Starting Nene")
        self.tree.on_error = self.on_tree_error  # type: ignore
        await self._add_commands()
        await self._sync_app_commands()
        await sync_users(self.db, self.fetch_guilds())

        logger.info("Nene started")

    async def on_ready(self):
        logger.info(f"Nene signed in as {self.user}")
        await self._startup_greet()

    async def _startup_greet(self):
        if self._env.ENVIRONMENT == "dev":
            return

        github_sha = self._env.GITHUB_SHA
        await self.nene_says(
            f"Nene has been deployed successfully. \nDeployment snapshot: https://github.com/fish-lovers-1/nene-v2/tree/{github_sha}"
        )

    @override
    async def on_command_error(
        self, ctx: commands.Context[Any], error: commands.CommandError, /
    ) -> None:
        exc = (
            error.original
            if isinstance(error, discord.app_commands.CommandInvokeError)
            else error
        )

        trace_back = traceback.format_exception(exc)
        await ctx.send(f"Error: {''.join(trace_back)}")

    async def on_tree_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        exc = (
            error.original
            if isinstance(error, discord.app_commands.CommandInvokeError)
            else error
        )

        trace_back = traceback.format_exception(exc)
        await interaction.response.send_message(f"Error: {''.join(trace_back)}")

    async def nene_start(self):
        await self.start(self._token)
