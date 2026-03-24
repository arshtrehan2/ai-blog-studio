"""create ai_usage_log table

Revision ID: 005_ai_usage_log
Revises: 004_post_tags
Create Date: 2024-01-15 12:00:04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "005_ai_usage_log"
down_revision = "004_post_tags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_usage_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tool", sa.String(50), nullable=False),
        sa.Column("input_tokens", sa.String(20), nullable=False),
        sa.Column("output_tokens", sa.String(20), nullable=False),
        sa.Column("latency_ms", sa.String(20), nullable=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_ai_usage_log_user_id", "ai_usage_log", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_usage_log_user_id", "ai_usage_log")
    op.drop_table("ai_usage_log")
