from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, field_validator


class AuthorOut(BaseModel):
    id: UUID
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
            raise ValueError("title must not be empty")
        return v.strip()[:255]

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        if v not in ("draft", "published"):
            raise ValueError("status must be draft or published")
        return v


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None


class PostOut(BaseModel):
    id: UUID
    title: str
    slug: str
    content: str
    tags: list[str]
    status: str
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    author_id: Optional[UUID] = None
    author: Optional[AuthorOut] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    summary: Optional[str] = None
    tags: list[str]
    author: Optional[AuthorOut] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedPosts(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class PublishResponse(BaseModel):
    id: UUID
    status: str
    published_at: datetime
    slug: str
