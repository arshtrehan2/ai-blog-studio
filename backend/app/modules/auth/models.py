import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ...database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    posts = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )
    ai_usage_logs = relationship(
        "AIUsageLog", back_populates="user", cascade="all, delete-orphan"
    )
