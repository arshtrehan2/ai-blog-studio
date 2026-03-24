"""create tags table

Revision ID: 003_tags
Revises: 002_posts
Create Date: 2024-01-15 12:00:02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003_tags"
down_revision = "002_posts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_tags_name", "tags", ["name"])
    op.create_index("ix_tags_slug", "tags", ["slug"])


def downgrade() -> None:
    op.drop_index("ix_tags_slug", "tags")
    op.drop_index("ix_tags_name", "tags")
    op.drop_table("tags")
