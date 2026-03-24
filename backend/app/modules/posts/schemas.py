import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class AuthorInfo(BaseModel):
    id: uuid.UUID
    display_name: str

    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    title: str
    content: str
    tags: list[str] = []
    status: str = "draft"
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v) > 255:
            raise ValueError("Title must be 255 characters or less")
        return v.strip()

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        if v not in ("draft", "published"):
            raise ValueError("Status must be 'draft' or 'published'")
        return v


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")
            if len(v) > 255:
                raise ValueError("Title must be 255 characters or less")
            return v.strip()
        return v


class PostResponse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    content: str
    tags: list[str] = []
    status: str
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    author_id: uuid.UUID
    author: Optional[AuthorInfo] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_post(cls, post) -> "PostResponse":
        return cls(
            id=post.id,
            title=post.title,
            slug=post.slug,
            content=post.content,
            tags=[tag.name for tag in post.tags] if post.tags else [],
            status=post.status,
            summary=post.summary,
            seo_title=post.seo_title,
            seo_description=post.seo_description,
            author_id=post.author_id,
            author=AuthorInfo.model_validate(post.author) if post.author else None,
            published_at=post.published_at,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )


class PostListItem(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    summary: Optional[str] = None
    tags: list[str] = []
    author: AuthorInfo
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedPostsResponse(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class PublishResponse(BaseModel):
    id: uuid.UUID
    status: str
    published_at: datetime
    slug: str
