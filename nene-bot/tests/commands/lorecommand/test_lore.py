from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from freezegun import freeze_time
from sqlalchemy import select

from argparsers.DateTimeTransformer import SYDNEY_TZ
from commands.LoreCommand import LoreCommand
from db.Database import Database
from db.models.Lore import Lore
from nene.Nene import Nene


def make_member(id: int = 123) -> MagicMock:
    member = MagicMock(spec=discord.Member)
    member.id = id
    member.display_name = f"Member {id}"
    return member


def make_interaction(user_id: int = 123) -> MagicMock:
    interaction = MagicMock(spec=discord.Interaction)
    interaction.response.send_message = AsyncMock()
    interaction.user.id = user_id
    return interaction


@pytest.mark.asyncio
@freeze_time("2026-03-10 11:11:11")
async def test_lore_add(test_nene: Nene):
    db = test_nene.db
    lore_cog = LoreCommand(nene=test_nene, db=db)
    interaction = make_interaction()
    member = make_member(456)
    interaction.response.send_message = AsyncMock()
    await lore_cog.add.callback(
        lore_cog,  # ty: ignore[invalid-argument-type]
        interaction,
        member=member,  # ty: ignore[parameter-already-assigned]
        lore="Nene did something suspicious",
        timestamp=None,
    )

    async with db.session() as session:
        lores = (await session.execute(select(Lore))).scalars().all()

    assert len(lores) == 1
    lore = lores[0]
    assert lore.content == "Nene did something suspicious"
    assert lore.target_user_discord_ref == str(456)
    assert lore.adder_dicord_ref == str(123)
    assert lore.sort_by_timestamp == lore.created_at
    interaction.response.send_message.assert_awaited_once_with(
        "Lore added!", ephemeral=True
    )


@pytest.mark.asyncio
async def test_lore_add_with_timestamp(test_nene: Nene):
    db = test_nene.db
    lore_cog = LoreCommand(nene=test_nene, db=db)
    interaction = make_interaction()
    member = make_member(456)

    interaction.response.send_message = AsyncMock()
    await lore_cog.add.callback(
        lore_cog,  # ty: ignore[invalid-argument-type]
        interaction,
        member=member,  # ty: ignore[parameter-already-assigned]
        lore="Nene is cute today too",
        timestamp=datetime(2026, 3, 3, tzinfo=SYDNEY_TZ),
    )

    async with db.session() as session:
        lores = (await session.execute(select(Lore))).scalars().all()

    assert len(lores) == 1
    lore = lores[0]
    assert lore.content == "Nene is cute today too"
    assert lore.target_user_discord_ref == str(456)
    assert lore.adder_dicord_ref == str(123)
    assert lore.sort_by_timestamp == datetime(2026, 3, 3)
    assert lore.created_at != lore.sort_by_timestamp
    interaction.response.send_message.assert_awaited_once_with(
        "Lore added!", ephemeral=True
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("adder_id", "referenced_id", "remover_id", "should_delete"),
    ([1, 2, 1, True], [1, 2, 2, True], [1, 2, 3, False]),
)
async def test_lore_remove(
    test_nene: Nene, adder_id, referenced_id, remover_id, should_delete: bool
):
    db = test_nene.db
    lore_cog = LoreCommand(nene=test_nene, db=db)

    async with db.session() as session:
        lore = Lore(
            adder_dicord_ref=str(adder_id),
            target_user_discord_ref=str(referenced_id),
            content="this lore is fake",
            timestamp=None,
        )

        session.add(lore)

    async with db.session() as session:
        lores = (await session.execute(select(Lore))).scalars().all()

    assert len(lores) == 1
    lore = lores[0]

    interaction = make_interaction(remover_id)
    await lore_cog.remove.callback(lore_cog, interaction, lore_id=lore.id)  # ty: ignore[parameter-already-assigned, invalid-argument-type]

    async with db.session() as session:
        lores = (await session.execute(select(Lore))).scalars().all()

    if should_delete:
        assert len(lores) == 0
        interaction.response.send_message.assert_awaited_once_with(
            "Your embarrassing moment has been deleted successfully!", ephemeral=True
        )

    else:
        assert len(lores) == 1
        interaction.response.send_message.assert_awaited_once_with(
            "Lore can only be deleted by either the adder or the person referenced in the lore"
        )


@pytest.mark.asyncio
async def test_lore_list_sorts_chronologically(test_nene: Nene, db: Database):
    member = make_member()
    interaction = make_interaction()

    async with db.session() as session:
        lore_3 = Lore(
            adder_dicord_ref="1",
            target_user_discord_ref=str(member.id),
            content="Third",
            timestamp=datetime(2026, 3, 12),
        )

        lore_1 = Lore(
            adder_dicord_ref="1",
            target_user_discord_ref=str(member.id),
            content="First",
            timestamp=datetime(2026, 3, 10),
        )

        lore_2 = Lore(
            adder_dicord_ref="1",
            target_user_discord_ref=str(member.id),
            content="Second",
            timestamp=datetime(2026, 3, 11),
        )

        # Deliberately insert out of order
        session.add_all([lore_3, lore_1, lore_2])

    cog = LoreCommand(test_nene, db)

    await cog._list.callback(
        cog,  # ty: ignore[invalid-argument-type]
        interaction,
        member,
        None,  # ty: ignore[too-many-positional-arguments]
    )

    interaction.response.send_message.assert_awaited_once()

    embed = interaction.response.send_message.await_args.kwargs["embed"]

    assert embed.description.index("First") < embed.description.index("Second")
    assert embed.description.index("Second") < embed.description.index("Third")
