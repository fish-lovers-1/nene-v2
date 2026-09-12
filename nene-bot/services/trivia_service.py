from __future__ import annotations

from returns.result import Failure, Result, Success

from clients.opentdb import GetMultipleQuestionsRequest, OpenTDBClient, TriviaQuestion


def _single[T](xs: list[T]) -> Result[T, str]:
    if len(xs) == 1:
        return Success(xs[0])
    else:
        return Failure(f"Expected list of size 1, but was {len(xs)}")


class TriviaService:
    opentdb_client: OpenTDBClient

    def __init__(self, opentdb_client: OpenTDBClient) -> None:
        self.opentdb_client = opentdb_client

    async def get_question(self, difficulty: str) -> Result[TriviaQuestion, str]:
        return (
            await self.opentdb_client.get_questions(
                GetMultipleQuestionsRequest(
                    amount=1, type="multiple", difficulty=difficulty
                )
            )
        ).bind(_single)
