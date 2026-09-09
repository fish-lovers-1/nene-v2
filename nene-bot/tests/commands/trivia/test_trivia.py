from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.trivia import Trivia, TriviaAnswerButton, TriviaView
from nene.Nene import Nene

TRIVIA_DATA = {
    "response_code": 0,
    "results": [
        {
            "question": "What is the capital of Spain?",
            "correct_answer": "Madrid",
            "incorrect_answers": ["Barcelona", "Sevilla", "Toledo"],
        }
    ],
}


class MockResponse:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def json(self):
        return TRIVIA_DATA


class MockSession:
    def __init__(self):
        self.url: str | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    def get(self, url: str):
        self.url = url
        return MockResponse()


def make_interaction(user_id: int = 123) -> MagicMock:
    interaction = MagicMock(spec=discord.Interaction)
    answer_message = MagicMock()
    answer_message.edit = AsyncMock()
    interaction.user.id = user_id
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.original_response = AsyncMock(return_value=answer_message)
    return interaction


def get_button(view: TriviaView, answer: str) -> TriviaAnswerButton:
    return next(
        button
        for button in view.children
        if isinstance(button, TriviaAnswerButton) and button.answer == answer
    )


async def ask_question(
    cog: Trivia,
    interaction: MagicMock,
    session: MockSession,
    *,
    difficulty: str = "any",
    time: int = 1,
    while_waiting=None,
) -> tuple[TriviaView, AsyncMock]:
    async def mock_sleep(seconds: int):
        assert seconds == time
        if while_waiting is not None:
            view = interaction.response.send_message.await_args.kwargs["view"]
            await while_waiting(view)

    with (
        patch("commands.trivia.aiohttp.ClientSession", return_value=session),
        patch(
            "commands.trivia.asyncio.sleep",
            new=AsyncMock(side_effect=mock_sleep),
        ) as sleep,
    ):
        await cog.ask.callback(
            cog,  # ty: ignore[invalid-argument-type]
            interaction,
            difficulty=difficulty,  # ty: ignore[parameter-already-assigned]
            time=time,  # ty: ignore[parameter-already-assigned]
        )

    view = interaction.response.send_message.await_args.kwargs["view"]
    return view, sleep


@pytest.mark.asyncio
async def test_trivia_ask(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()

    view, _ = await ask_question(Trivia(test_nene), interaction, session)

    assert session.url == "https://opentdb.com/api.php?amount=1&type=multiple"
    assert interaction.response.send_message.await_args.args[0] == (
        "## What is the capital of Spain?"
    )
    assert len(view.children) == 4


@pytest.mark.asyncio
async def test_trivia_ask_with_difficulty(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()

    await ask_question(Trivia(test_nene), interaction, session, difficulty="hard")

    assert session.url == (
        "https://opentdb.com/api.php?amount=1&type=multiple&difficulty=hard"
    )


@pytest.mark.asyncio
async def test_trivia_ask_with_time(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()

    _, sleep = await ask_question(Trivia(test_nene), interaction, session, time=1)

    sleep.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_trivia_ask_with_no_answers(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()

    view, _ = await ask_question(Trivia(test_nene), interaction, session)

    assert view.revealed is True
    assert get_button(view, "Madrid").style is discord.ButtonStyle.success
    interaction.followup.send.assert_awaited_once_with("Nobody answered this question.")


@pytest.mark.asyncio
async def test_trivia_ask_with_correct_answer(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()
    button_interaction = make_interaction()

    async def answer_correctly(view: TriviaView):
        await get_button(view, "Madrid").callback(button_interaction)

    view, _ = await ask_question(
        Trivia(test_nene), interaction, session, while_waiting=answer_correctly
    )

    marker = view.markers_by_answer["Madrid"]
    assert get_button(view, "Madrid").style is discord.ButtonStyle.success
    interaction.followup.send.assert_awaited_once_with(f"**Correct:**\n{marker} <@123>")


@pytest.mark.asyncio
async def test_trivia_ask_with_incorrect_answer(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()
    button_interaction = make_interaction()

    async def answer_incorrectly(view: TriviaView):
        await get_button(view, "Barcelona").callback(button_interaction)

    view, _ = await ask_question(
        Trivia(test_nene), interaction, session, while_waiting=answer_incorrectly
    )

    marker = view.markers_by_answer["Barcelona"]
    assert get_button(view, "Madrid").style is discord.ButtonStyle.success
    interaction.followup.send.assert_awaited_once_with(
        f"**Incorrect:**\n{marker} <@123>"
    )


@pytest.mark.asyncio
async def test_trivia_ask_when_answer_changes_from_wrong_to_right(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()
    button_interaction = make_interaction()

    async def switch_to_correct_answer(view: TriviaView):
        await get_button(view, "Barcelona").callback(button_interaction)
        await get_button(view, "Madrid").callback(button_interaction)

    view, _ = await ask_question(
        Trivia(test_nene), interaction, session, while_waiting=switch_to_correct_answer
    )

    marker = view.markers_by_answer["Madrid"]
    assert view.answers_by_user == {123: "Madrid"}
    interaction.followup.send.assert_awaited_once_with(f"**Correct:**\n{marker} <@123>")


@pytest.mark.asyncio
async def test_trivia_ask_when_answer_changes_from_right_to_wrong(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()
    button_interaction = make_interaction()

    async def switch_to_incorrect_answer(view: TriviaView):
        await get_button(view, "Madrid").callback(button_interaction)
        await get_button(view, "Barcelona").callback(button_interaction)

    view, _ = await ask_question(
        Trivia(test_nene),
        interaction,
        session,
        while_waiting=switch_to_incorrect_answer,
    )

    marker = view.markers_by_answer["Barcelona"]
    assert view.answers_by_user == {123: "Barcelona"}
    interaction.followup.send.assert_awaited_once_with(
        f"**Incorrect:**\n{marker} <@123>"
    )


@pytest.mark.asyncio
async def test_trivia_ask_when_same_answer_is_clicked_multiple_times(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()
    button_interaction = make_interaction()

    async def click_same_answer_twice(view: TriviaView):
        await get_button(view, "Madrid").callback(button_interaction)
        await get_button(view, "Madrid").callback(button_interaction)

    view, _ = await ask_question(
        Trivia(test_nene), interaction, session, while_waiting=click_same_answer_twice
    )

    marker = view.markers_by_answer["Madrid"]
    assert view.answers_by_user == {123: "Madrid"}
    interaction.followup.send.assert_awaited_once_with(f"**Correct:**\n{marker} <@123>")


@pytest.mark.asyncio
async def test_trivia_ask_when_many_buttons_are_clicked(test_nene: Nene):
    interaction = make_interaction()
    session = MockSession()
    button_interaction = make_interaction()

    async def click_every_answer(view: TriviaView):
        for button in view.children:
            if isinstance(button, TriviaAnswerButton):
                await button.callback(button_interaction)

    view, _ = await ask_question(
        Trivia(test_nene), interaction, session, while_waiting=click_every_answer
    )

    last_answer = next(
        button.answer
        for button in reversed(view.children)
        if isinstance(button, TriviaAnswerButton)
    )
    marker = view.markers_by_answer[last_answer]
    expected_heading = "**Correct:**" if last_answer == "Madrid" else "**Incorrect:**"
    interaction.followup.send.assert_awaited_once_with(
        f"{expected_heading}\n{marker} <@123>"
    )
