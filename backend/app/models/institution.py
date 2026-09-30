from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.author import author_institutions
class Institution(Base):
    __tablename__ = "institutions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    country: Mapped[str | None] = mapped_column(String(100))
    authors: Mapped[list["Author"]] = relationship(secondary=author_institutions, back_populates="institutions")
