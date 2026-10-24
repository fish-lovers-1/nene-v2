from sqlalchemy.orm import Mapped, mapped_column

from db.Base import BaseModel


class DeploymentInfo(BaseModel):
    __tablename__ = "deployment_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    sha: Mapped[str]
