import discord
from discord import app_commands
from discord.ext import commands

import random
import html
import aiohttp
import asyncio

PRODUCE_MARKERS = [
    "🍇", "🍈", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏",
    "🍐", "🍑", "🍒", "🍓", "🫐", "🥝", "🍅", "🫒", "🥥", "🥑",
    "🍆", "🥔", "🥕", "🌽", "🌶️", "🫑", "🥒", "🥬", "🥦", "🧄",
    "🧅", "🥜", "🫘", "🫚", "🫛", "🍄", "🌰",
]


class TriviaAnswerButton(discord.ui.Button):
    def __init__(self, marker: str, answer: str):
        super().__init__(label=answer, emoji=marker, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"You chose: {self.label}", ephemeral=True
        )


class TriviaView(discord.ui.View):
    def __init__(self, markers: list[str], answers: list[str]):
        super().__init__(timeout=None)
        for marker, answer in zip(markers, answers, strict=True):
            self.add_item(TriviaAnswerButton(marker, answer))


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
        # See here for api details: https://opentdb.com/api_config.php
        url = "https://opentdb.com/api.php?amount=1&type=multiple&difficulty=easy"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
        if data["response_code"] != 0:
            await interaction.response.send_message(
                "Failed to retrieve a trivia question."
            )
            return

        """
        json format looks like this:
        [
            {
                "type": str
                "difficulty": str
                "category": str
                "question": str
                "correct_answer": str
                "incorrect_answers": [str]
            }
        ]
        """
        result = data["results"][0]
        question = html.unescape(result["question"])
        correct_answer = html.unescape(result["correct_answer"])
        incorrect_answers = [html.unescape(answer) for answer in result["incorrect_answers"]]
        answers = [correct_answer] + incorrect_answers
        random.shuffle(answers)

        answer_markers = random.sample(PRODUCE_MARKERS, k=len(answers))
        message = f"## {question}"
        view = TriviaView(answer_markers, answers)
        await interaction.response.send_message(message, view=view)

        await asyncio.sleep(15)
        for button in view.children:
            button.disabled = True
        await interaction.edit_original_response(view=view)
        await interaction.followup.send(
            f"The correct answer was: {correct_answer}"
        )
