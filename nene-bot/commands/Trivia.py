import discord
from discord import app_commands
from discord.ext import commands

import random
import html
import aiohttp
import asyncio


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

        answer_markers = ["🍎", "🍑", "🍇", "🍉"]
        answer_list = "\n".join(
            f"{marker}  {answer}" for marker, answer in zip(answer_markers, answers, strict=True)
        )
        message = f"## {question}\n```\n{answer_list}\n```"
        await interaction.response.send_message(message)
        trivia_message = await interaction.original_response()
        for marker in answer_markers:
            await trivia_message.add_reaction(marker)

        await asyncio.sleep(15)
        await interaction.followup.send(
            f"The correct answer was: {correct_answer}"
        )
