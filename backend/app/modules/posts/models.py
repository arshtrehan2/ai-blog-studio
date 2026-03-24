import uuid
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, CheckConstraint,
    Table, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# Join table for many-to-many posts <-> tags
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(300), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default="draft",
        index=True,
    )
    summary = Column(Text, nullable=True)
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(String(500), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'deleted')", name="chk_post_status"),
    )

    # Relationships
    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    ai_usage_logs = relationship("AIUsageLog", back_populates="post")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    posts = relationship("Post", secondary=post_tags, back_populates="tags")


class AIUsageLog(Base):
    __tablename__ = "ai_usage_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tool = Column(String(50), nullable=False)
    input_tokens = Column(String(20), nullable=False)
    output_tokens = Column(String(20), nullable=False)
    latency_ms = Column(String(20), nullable=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="ai_usage_logs")
    post = relationship("Post", back_populates="ai_usage_logs")
