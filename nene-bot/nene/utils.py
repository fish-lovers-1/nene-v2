import logging
from collections.abc import AsyncIterator

from discord import Guild
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.Database import Database
from db.models.User import User

logger = logging.getLogger(__name__)


async def sync_users(db: Database, guilds: AsyncIterator[Guild]):
    async with db.session() as session:
        async for guild in guilds:
            await _sync_user_in_guild(guild=guild, session=session)


async def _sync_user_in_guild(guild: Guild, session: AsyncSession):
    async for member in guild.fetch_members(limit=None):
        logger.info(f"about to sync user {member.name}")
        stmt = insert(User).values(
            discord_ref=str(member.id),
            username_in_server=member.display_name,
            global_username=member.name,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=[User.discord_ref],
            set_={
                "username_in_server": stmt.excluded.username_in_server,
                "global_username": stmt.excluded.global_username,
            },
        )
        await session.execute(stmt)
    await session.commit()
