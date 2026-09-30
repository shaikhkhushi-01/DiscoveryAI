"""Initial DiscoveryAI database schema.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alembic_version_guard",
        sa.Column("id", sa.Integer(), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("alembic_version_guard")
