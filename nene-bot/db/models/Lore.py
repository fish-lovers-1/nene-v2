import datetime

from sqlalchemy.orm import Mapped, mapped_column

from db.Base import BaseModel


class Lore(BaseModel):
    __tablename__ = "lore"

    # test
    id: Mapped[int] = mapped_column(primary_key=True)
    adder_dicord_ref: Mapped[str]
    target_user_discord_ref: Mapped[str]
    content: Mapped[str]
    optional_timestamp: Mapped[datetime.datetime | None]
