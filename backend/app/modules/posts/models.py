import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ...database import Base


post_tags = Table(
    "post_tags",
    Base.metadata,
    Column(
        "post_id",
        Uuid(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Uuid(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    slug = Column(String(300), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    summary = Column(Text, nullable=True)
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(String(500), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    ai_usage_logs = relationship("AIUsageLog", back_populates="post")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", secondary=post_tags, back_populates="tags")
