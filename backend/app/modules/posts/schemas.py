from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class PostStatus(str, Enum):
    draft = "draft"
    published = "published"


class AuthorResponse(BaseModel):
    id: UUID
    display_name: str

    model_config = {"from_attributes": True}


class PostCreateRequest(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    status: PostStatus = PostStatus.draft
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v) > 255:
            raise ValueError("Title must be at most 255 characters")
        return v.strip()

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v


class PostUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
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
                raise ValueError("Title must be at most 255 characters")
            return v.strip()
        return v


class PostResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    content: str
    tags: List[str] = []
    status: str
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    author_id: Optional[UUID] = None
    author: Optional[AuthorResponse] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    summary: Optional[str] = None
    tags: List[str] = []
    author: Optional[AuthorResponse] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    items: List[PostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class PublishResponse(BaseModel):
    id: UUID
    status: str
    published_at: datetime
    slug: str
