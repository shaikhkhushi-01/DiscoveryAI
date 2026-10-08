"""add durable background indexing jobs

Revision ID: 0006_indexing_jobs
Revises: 0005_document_parsing_fields
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_indexing_jobs"
down_revision = "0005_document_parsing_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "indexing_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("vector_status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("graph_status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("document_id", name="uq_indexing_jobs_document_id"),
    )
    op.create_index("ix_indexing_jobs_document_id", "indexing_jobs", ["document_id"], unique=True)
    op.create_index("ix_indexing_jobs_status", "indexing_jobs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_indexing_jobs_status", table_name="indexing_jobs")
    op.drop_index("ix_indexing_jobs_document_id", table_name="indexing_jobs")
    op.drop_table("indexing_jobs")
