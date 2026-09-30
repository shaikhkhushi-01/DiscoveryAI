from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
class Paper(Base):
    __tablename__ = "papers"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    doi: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    abstract: Mapped[str | None] = mapped_column(Text)
    publication_date: Mapped[Date | None] = mapped_column(Date)
    venue: Mapped[str | None] = mapped_column(String(255))
    document: Mapped["Document | None"] = relationship(back_populates="paper", uselist=False)
    authors: Mapped[list["Author"]] = relationship(secondary="paper_authors", back_populates="papers")
