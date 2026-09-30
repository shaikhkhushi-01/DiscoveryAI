"""add discovery score fields

Revision ID: 0004_discovery_score
Revises: 0003_scientific_models
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_discovery_score"
down_revision = "0003_scientific_models"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("research_gaps", sa.Column("discovery_score", sa.Float(), nullable=True))
    op.add_column("research_gaps", sa.Column("score_version", sa.String(length=20), nullable=True))
    op.add_column("research_gaps", sa.Column("evidence_status", sa.String(length=50), nullable=True))

def downgrade() -> None:
    op.drop_column("research_gaps", "evidence_status")
    op.drop_column("research_gaps", "score_version")
    op.drop_column("research_gaps", "discovery_score")
