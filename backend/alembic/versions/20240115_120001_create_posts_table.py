"""create posts table

Revision ID: 002_posts
Revises: 001_users
Create Date: 2024-01-15 12:00:01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_posts"
down_revision = "001_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(300), nullable=False, unique=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("seo_title", sa.String(255), nullable=True),
        sa.Column("seo_description", sa.String(500), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("status IN ('draft', 'published', 'deleted')", name="chk_post_status"),
    )
    op.create_index("ix_posts_author_id", "posts", ["author_id"])
    op.create_index("ix_posts_slug", "posts", ["slug"])
    op.create_index("ix_posts_status", "posts", ["status"])
    op.create_index("ix_posts_deleted_at", "posts", ["deleted_at"])
    op.create_index("ix_posts_published_at", "posts", ["published_at"])


def downgrade() -> None:
    op.drop_index("ix_posts_published_at", "posts")
    op.drop_index("ix_posts_deleted_at", "posts")
    op.drop_index("ix_posts_status", "posts")
    op.drop_index("ix_posts_slug", "posts")
    op.drop_index("ix_posts_author_id", "posts")
    op.drop_table("posts")
