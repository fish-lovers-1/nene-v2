import discord
from discord import app_commands
from discord.ext import commands


class Trivia(commands.Cog):
    trivia_group = app_commands.Group(
        name="trivia",
        description="Perform trivia related commands"
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @trivia_group.command(
        name="ask",
        description="Ask a trivia question"
    )
    async def ask(
        self,
        interaction: discord.Interaction,
    ):
        question = "What is the capital of France?"

        await interaction.response.send_message(question)
