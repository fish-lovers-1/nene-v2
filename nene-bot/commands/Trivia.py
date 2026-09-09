import discord
from discord import app_commands
from discord.ext import commands

import random
import html
import aiohttp
import asyncio
from typing import Literal

FRUIT_MARKERS = [
    "🍇", "🍈", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏",
    "🍐", "🍑", "🍒", "🍓", "🫐", "🥝", "🍅", "🫒", "🥥", "🥑",
    "🍆", "🥔", "🥕", "🌽", "🌶️", "🫑", "🥒", "🥬", "🥦", "🧄",
    "🧅", "🥜", "🫘", "🫚", "🫛", "🍄", "🌰",
]


class TriviaAnswerButton(discord.ui.Button):
    def __init__(self, marker: str, answer: str):
        super().__init__(label=answer, emoji=marker, style=discord.ButtonStyle.secondary)
        self.marker = marker
        self.answer = answer

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        # Freeze button if question is done
        if not isinstance(view, TriviaView) or view.revealed:
            await interaction.response.defer()
            return

        # Send user-only answer confirmation message, or edit it if they already answered
        user_id = interaction.user.id
        view.answers_by_user[user_id] = self.answer
        answer_message = view.answer_messages.get(user_id)
        if answer_message is None:
            await interaction.response.send_message(
                f"{self.marker} {self.answer}", ephemeral=True
            )
            view.answer_messages[user_id] = await interaction.original_response()
        else:
            await interaction.response.defer()
            await answer_message.edit(content=f"{self.marker}  {self.answer}")


class TriviaView(discord.ui.View):
    def __init__(
        self, markers: list[str], answers: list[str], correct_answer: str
    ):
        super().__init__(timeout=None)
        self.correct_answer = correct_answer
        self.markers_by_answer = dict(zip(answers, markers, strict=True))
        self.answers_by_user: dict[int, str] = {}
        self.answer_messages: dict[int, discord.InteractionMessage] = {}
        self.revealed = False
        for marker, answer in zip(markers, answers, strict=True):
            self.add_item(TriviaAnswerButton(marker, answer))

    def reveal_answer(self):
        # Make correct answer glow green and disable all buttons
        self.revealed = True
        for button in self.children:
            if not isinstance(button, TriviaAnswerButton):
                continue

            if button.answer == self.correct_answer:
                button.style = discord.ButtonStyle.success

    def get_results_message(self) -> str:
        users_by_answer: dict[str, list[str]] = {}
        for user_id, answer in self.answers_by_user.items():
            users_by_answer.setdefault(answer, []).append(f"<@{user_id}>")

        correct_rows = [
            f"{self.markers_by_answer[answer]} {', '.join(users)}"
            for answer, users in users_by_answer.items()
            if answer == self.correct_answer
        ]
        incorrect_rows = [
            f"{self.markers_by_answer[answer]} {', '.join(users)}"
            for answer, users in users_by_answer.items()
            if answer != self.correct_answer
        ]
        results = []
        if correct_rows:
            results.append("**Correct:**\n" + "\n".join(correct_rows))
        if incorrect_rows:
            results.append("**Incorrect:**\n" + "\n".join(incorrect_rows))

        return "\n".join(results) or "Nobody answered this question."


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
    @app_commands.describe(difficulty="Choose a question difficulty")
    async def ask(
        self,
        interaction: discord.Interaction,
        difficulty: Literal["any", "easy", "medium", "hard"] = "any",
    ):
        # See here for api details: https://opentdb.com/api_config.php
        # First fetch a potential question
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
        if difficulty != "any":
            url += f"&difficulty={difficulty}"
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
        # Then deconstruct the question and answers
        result = data["results"][0]
        question = html.unescape(result["question"])
        correct_answer = html.unescape(result["correct_answer"])
        incorrect_answers = [html.unescape(answer) for answer in result["incorrect_answers"]]
        answers = [correct_answer] + incorrect_answers
        random.shuffle(answers)

        # Format the discord embed
        answer_markers = random.sample(FRUIT_MARKERS, k=len(answers))
        message = f"## {question}"
        view = TriviaView(answer_markers, answers, correct_answer)
        await interaction.response.send_message(message, view=view)

        # Wait before revealing the answer
        await asyncio.sleep(15)
        view.reveal_answer()
        await interaction.edit_original_response(view=view)
        await interaction.followup.send(view.get_results_message())
