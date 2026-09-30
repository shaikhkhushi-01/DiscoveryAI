from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
paper_authors = Table("paper_authors", Base.metadata, Column("paper_id", ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True), Column("author_id", ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True))
author_institutions = Table("author_institutions", Base.metadata, Column("author_id", ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True), Column("institution_id", ForeignKey("institutions.id", ondelete="CASCADE"), primary_key=True))
class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    orcid: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    papers: Mapped[list["Paper"]] = relationship(secondary=paper_authors, back_populates="authors")
    institutions: Mapped[list["Institution"]] = relationship(secondary=author_institutions, back_populates="authors")
