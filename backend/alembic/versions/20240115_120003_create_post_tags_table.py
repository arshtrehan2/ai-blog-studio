"""create post_tags join table

Revision ID: 004_post_tags
Revises: 003_tags
Create Date: 2024-01-15 12:00:03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004_post_tags"
down_revision = "003_tags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "post_tags",
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("post_tags")
