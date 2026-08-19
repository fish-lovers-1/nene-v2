import logging
import resource
from datetime import datetime
from typing import assert_never

import discord
import discord.embeds
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from argparsers.DateTimeTransformer import DateTimeTransformer
from commands.utils import ensure_utc
from constants import EMBEDS_MAX_DESC_LENGTH
from db.Database import Database
from db.models.Lore import Lore
from db.models.User import User

logger = logging.getLogger(__name__)


class LoreCommand(commands.Cog):
    lore = app_commands.Group(
        name="lore",
        description="Add more spicy lore to the beloved members in the server.",
    )

    def __init__(self, nene: commands.Bot, db: Database):
        self.nene = nene
        self.db = db

    @lore.command(description="Add lore to a member")
    @app_commands.describe(
        member="The member to add lore to",
        lore="text to add more spice to the member.",
        timestamp="Optional: DD-MM-YYYY [HH:MM]. If not given the current time is taken",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        lore: app_commands.Range[str, 1, 1000],
        timestamp: app_commands.Transform[datetime, DateTimeTransformer] | None = None,
    ):
        async with self.db.session() as session:
            session.add(
                Lore(
                    adder_dicord_ref=str(interaction.user.id),
                    target_user_discord_ref=str(member.id),
                    content=lore,
                    timestamp=timestamp,
                )
            )

        await interaction.response.send_message("Lore added!", ephemeral=True)

    @lore.command(description="Remove lore added to a member")
    @app_commands.describe(lore_id="The id of the lore to be removed")
    async def remove(self, interaction: discord.Interaction, lore_id: int):
        deleter_ref = str(interaction.user.id)

        async with self.db.session() as session:
            lore = (
                await session.execute(select(Lore).where(Lore.id == lore_id))
            ).scalar_one_or_none()

            if lore is None:
                raise LookupError("Lore does not exist")

            if deleter_ref not in (lore.target_user_discord_ref, lore.adder_dicord_ref):
                await interaction.response.send_message(
                    "Lore can only be deleted by either the adder or the person referenced in the lore"
                )
                return

            await session.delete(lore)

        await interaction.response.send_message(
            "Your embarrassing moment has been deleted successfully!", ephemeral=True
        )

    @lore.command(
        description="List all the lore of a member in chronological order", name="list"
    )
    @app_commands.describe(
        cursor=(
            "Optionally, the ID of a lore entry to start after. "
            "If omitted, starts from the oldest entry."
        )
    )
    async def _list(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        cursor: str | None = None,
    ):
        async with self.db.session() as session:
            cursor_row = (
                (
                    await session.execute(select(Lore).where(Lore.id == cursor))
                ).scalar_one_or_none()
                if cursor is not None
                else None
            )

        if cursor_row is None and cursor is not None:
            raise LookupError("Cannot find the cursor row")

        base_query = (
            select(Lore)
            .where(Lore.target_user_discord_ref == str(member.id))
            .order_by(Lore.sort_by_timestamp.asc(), Lore.id.asc())
        )

        final_query = (
            base_query
            if cursor_row is None
            else base_query.where(
                (Lore.sort_by_timestamp > cursor_row.sort_by_timestamp)
                | (Lore.id > cursor_row.id)
            )
        )

        async with self.db.session() as session:
            lores = list((await session.execute(final_query)).scalars().all())

        response = await self._get_response(member=member, lores=lores)

        match response:
            case discord.Embed():
                await interaction.response.send_message(embed=response)
            case str():
                await interaction.response.send_message(response)
            case _:
                assert_never(resource)

    async def _get_response(
        self, member: discord.Member, lores: list[Lore]
    ) -> discord.Embed | str:
        if len(lores) == 0:
            return "Look at this person with no lore LOL"

        async with self.db.session() as session:
            user_lookup_table = await User.get_lookup_table(session)

        entries: list[str] = []

        for lore in lores:
            adder = user_lookup_table.get(lore.adder_dicord_ref)

            if adder is None:
                logger.warning(
                    f"Adder with discord ref {lore.adder_dicord_ref} is not synced to the user db"
                )

            timestamp = int(ensure_utc(lore.sort_by_timestamp).timestamp())

            entry = (
                f"**{len(entries) + 1}.** "
                f"*added by {adder.username_in_server if adder is not None else 'Unknown'}*\n"
                f"ID: `{lore.id}` • "
                f"<t:{timestamp}:f>\n"
                f"> {lore.content}"
            )

            candidate = "\n\n".join([*entries, entry])
            if len(candidate) > EMBEDS_MAX_DESC_LENGTH:
                break

            entries.append(entry)

        embed = discord.Embed(
            title=f"Lore about {member.display_name} 📖",
            description="\n\n".join(entries),
        )

        return embed
