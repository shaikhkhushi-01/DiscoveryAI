from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class ResearchGap(Base):
    __tablename__ = "research_gaps"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    gap_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float | None]
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
