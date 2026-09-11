from __future__ import annotations

import html
from typing import Literal

import aiohttp
from pydantic import BaseModel, field_validator
from returns.result import Failure, Result, Success


class GetMultipleQuestionsRequest(BaseModel):
    amount: int
    type: Literal["multiple"]
    difficulty: str | None  # todo: this should be literal


class GetMultipleQuestionsResponse(BaseModel):
    response_code: int
    results: list[TriviaQuestion]


class TriviaQuestion(BaseModel):
    category: str
    difficulty: str
    question: str
    correct_answer: str
    incorrect_answers: list[str]

    @field_validator("question", "correct_answer", mode="before")
    @classmethod
    def unescape_string(cls, value: str) -> str:
        return html.unescape(value)

    @field_validator("incorrect_answers", mode="before")
    @classmethod
    def unescape_list(cls, value: list[str]) -> list[str]:
        return [html.unescape(ans) for ans in value]


class OpenTDBClient:
    """
    https://opentdb.com/api_config.php
    """

    _session: aiohttp.ClientSession
    BASE_URL: str = "https://opentdb.com/api.php"

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def get_questions(
        self, request: GetMultipleQuestionsRequest
    ) -> Result[list[TriviaQuestion], str]:
        async with self._session.get(
            self.BASE_URL, params=request.model_dump()
        ) as response:
            if response.status != 200:
                return Failure(f"Received http response code {response.status}")
            data = GetMultipleQuestionsResponse.model_validate(await response.json())

        if data.response_code != 0 or not data.results:
            return Failure(
                f"Received unexpected API response code {data.response_code}"
            )

        return Success(data.results)
