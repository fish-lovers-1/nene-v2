from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from db.Base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_ref: Mapped[str] = mapped_column(unique=True, nullable=False)
    username_in_server: Mapped[str]
    global_username: Mapped[str]

    @classmethod
    async def get_lookup_table(cls, session: AsyncSession) -> dict[str, "User"]:
        users = (await session.execute(select(User))).scalars().all()
        return {user.discord_ref: user for user in users}
