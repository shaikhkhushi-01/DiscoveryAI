"""add parsed document fields

Revision ID: 0005_document_parsing_fields
Revises: 0004_discovery_score
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_document_parsing_fields"
down_revision = "0004_discovery_score"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("page_count", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("metadata_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "metadata_json")
    op.drop_column("documents", "extracted_text")
    op.drop_column("documents", "page_count")
