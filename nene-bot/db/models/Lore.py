from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from db.Base import BaseModel


class Lore(BaseModel):
    __tablename__ = "lore"

    id: Mapped[int] = mapped_column(primary_key=True)
    adder_dicord_ref: Mapped[str]
    target_user_discord_ref: Mapped[str]
    content: Mapped[str]
    optional_timestamp: Mapped[datetime | None]

    def __init__(
        self,
        adder_dicord_ref: str,
        target_user_discord_ref: str,
        content: str,
        timestamp: datetime | None,
    ):
        self.adder_dicord_ref = adder_dicord_ref
        self.target_user_discord_ref = target_user_discord_ref
        self.content = content
        self.optional_timestamp = timestamp

    @hybrid_property
    def sort_by_timestamp(self) -> datetime:
        return self.optional_timestamp or self.created_at

    @sort_by_timestamp.inplace.expression
    @classmethod
    def _sort_by_timestamp_sql(cls):
        return func.coalesce(cls.optional_timestamp, cls.created_at)
