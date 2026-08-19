from datetime import datetime
from unittest.mock import MagicMock

import discord
import pytest

from argparsers.DateTimeTransformer import DateTimeTransformer


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "03-03-2026",
            datetime(2026, 3, 3),
        ),
        (
            "03-03-2026 14:30",
            datetime(2026, 3, 3, 14, 30),
        ),
    ],
)
@pytest.mark.asyncio
async def test_datetime_transform(value, expected):
    transformer = DateTimeTransformer()

    result = await transformer.transform(
        MagicMock(spec=discord.Interaction),
        value,
    )

    assert result == expected


@pytest.mark.asyncio
async def test_datetime_transform_invalid():
    transformer = DateTimeTransformer()

    with pytest.raises(ValueError):
        await transformer.transform(
            MagicMock(spec=discord.Interaction),
            "not a date",
        )
