from alembic import op
import sqlalchemy as sa

revision = "0003_scientific_models"
down_revision = "0002_core_models"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("papers", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("title",sa.String(500),nullable=False), sa.Column("doi",sa.String(255),unique=True), sa.Column("abstract",sa.Text()), sa.Column("publication_date",sa.Date()), sa.Column("venue",sa.String(255)))
    op.create_table("authors", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("full_name",sa.String(255),nullable=False), sa.Column("orcid",sa.String(50),unique=True))
    op.create_table("institutions", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("name",sa.String(300),nullable=False), sa.Column("country",sa.String(100)))
    op.create_table("documents", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("paper_id",sa.Integer(),sa.ForeignKey("papers.id",ondelete="CASCADE"),unique=True,nullable=False), sa.Column("document_type",sa.String(50),nullable=False), sa.Column("storage_uri",sa.String(1000)), sa.Column("checksum",sa.String(128),unique=True), sa.Column("status",sa.String(50),nullable=False))
    for name in ("datasets","methods","topics","problems","applications","metrics"):
        op.create_table(name, sa.Column("id",sa.Integer(),primary_key=True), sa.Column("name",sa.String(255),nullable=False), sa.Column("description",sa.Text()))
    op.create_table("paper_authors", sa.Column("paper_id",sa.Integer(),sa.ForeignKey("papers.id",ondelete="CASCADE"),primary_key=True), sa.Column("author_id",sa.Integer(),sa.ForeignKey("authors.id",ondelete="CASCADE"),primary_key=True))
    op.create_table("author_institutions", sa.Column("author_id",sa.Integer(),sa.ForeignKey("authors.id",ondelete="CASCADE"),primary_key=True), sa.Column("institution_id",sa.Integer(),sa.ForeignKey("institutions.id",ondelete="CASCADE"),primary_key=True))
    op.create_table("research_gaps", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("title",sa.String(500),nullable=False), sa.Column("description",sa.Text(),nullable=False), sa.Column("gap_type",sa.String(50),nullable=False), sa.Column("confidence",sa.Float()), sa.Column("project_id",sa.Integer(),sa.ForeignKey("projects.id",ondelete="SET NULL")))
    op.create_table("hypotheses", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("statement",sa.Text(),nullable=False), sa.Column("rationale",sa.Text()), sa.Column("status",sa.String(50),nullable=False), sa.Column("research_gap_id",sa.Integer(),sa.ForeignKey("research_gaps.id",ondelete="SET NULL")))
    op.create_table("experiments", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("name",sa.String(255),nullable=False), sa.Column("methodology",sa.Text()), sa.Column("status",sa.String(50),nullable=False), sa.Column("hypothesis_id",sa.Integer(),sa.ForeignKey("hypotheses.id",ondelete="SET NULL")))

def downgrade():
    for name in ("experiments","hypotheses","research_gaps","author_institutions","paper_authors","metrics","applications","problems","topics","methods","datasets","documents","institutions","authors","papers"):
        op.drop_table(name)
