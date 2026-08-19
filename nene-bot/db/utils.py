from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column

from db.Base import Base

Timestamp = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True)),
]


def get_all_db_tables() -> list[type[Base]]:
    return [mapper.class_ for mapper in Base.registry.mappers]
