from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands

SYDNEY_TZ = ZoneInfo("Australia/Sydney")


class DateTimeTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> datetime:
        for fmt in ("%d-%m-%Y %H:%M", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass

        raise ValueError("Expected DD-MM-YYYY or DD-MM-YYYY HH:MM")
