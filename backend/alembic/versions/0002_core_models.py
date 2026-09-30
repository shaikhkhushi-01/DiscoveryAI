"""Add core account and project models.

Revision ID: 0002_core_models
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_core_models"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("roles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(50), nullable=False), sa.Column("description", sa.String(255)), sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)
    op.create_table("organizations", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(150), nullable=False), sa.Column("slug", sa.String(150), nullable=False))
    op.create_index("ix_organizations_name", "organizations", ["name"])
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(320), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("full_name", sa.String(150)), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("role_id", sa.Integer(), nullable=False), sa.Column("organization_id", sa.Integer()), sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("projects", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(150), nullable=False), sa.Column("slug", sa.String(150), nullable=False), sa.Column("description", sa.Text()), sa.Column("organization_id", sa.Integer(), nullable=False), sa.Column("owner_id", sa.Integer(), nullable=False), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="RESTRICT"))
    op.create_index("ix_projects_slug", "projects", ["slug"])

def downgrade() -> None:
    op.drop_index("ix_projects_slug", table_name="projects"); op.drop_table("projects")
    op.drop_index("ix_users_email", table_name="users"); op.drop_table("users")
    op.drop_index("ix_organizations_slug", table_name="organizations"); op.drop_index("ix_organizations_name", table_name="organizations"); op.drop_table("organizations")
    op.drop_index("ix_roles_name", table_name="roles"); op.drop_table("roles")
