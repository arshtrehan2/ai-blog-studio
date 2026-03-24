import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    posts: Mapped[list] = relationship("Post", secondary="post_tags", back_populates="tags")


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class Post(Base):
    __tablename__ = "posts"

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'deleted')", name="post_status_check"),
        Index("ix_posts_status_published_at", "status", "published_at"),
        Index("ix_posts_author_id", "author_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    seo_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    # Relationships
    author: Mapped["User"] = relationship("User", back_populates="posts")
    tags: Mapped[list[Tag]] = relationship("Tag", secondary="post_tags", back_populates="posts")
    ai_usage_logs: Mapped[list] = relationship("AIUsageLog", back_populates="post")


class AIUsageLog(Base):
    __tablename__ = "ai_usage_log"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tool: Mapped[str] = mapped_column(String(50), nullable=False)
    input_tokens: Mapped[int] = mapped_column(nullable=False)
    output_tokens: Mapped[int] = mapped_column(nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(nullable=True)
    post_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    user: Mapped["User"] = relationship("User", back_populates="ai_usage_logs")
    post: Mapped["Post"] = relationship("Post", back_populates="ai_usage_logs")
