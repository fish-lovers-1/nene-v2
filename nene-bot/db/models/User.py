from sqlalchemy.orm import Mapped, mapped_column

from db.Base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_ref: Mapped[str] = mapped_column(unique=True, nullable=False)
    username_in_server: Mapped[str]
    global_username: Mapped[str]
