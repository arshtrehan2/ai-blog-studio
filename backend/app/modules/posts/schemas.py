import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AuthorResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    display_name: str


class PostCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    status: str = "draft"
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None


class PostResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    slug: str
    content: str
    tags: List[str] = []
    status: str
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    author_id: uuid.UUID
    author: Optional[AuthorResponse] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None


class PostListItem(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    slug: str
    summary: Optional[str] = None
    tags: List[str] = []
    author: AuthorResponse
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    items: List[PostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class PublishResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    status: str
    published_at: datetime
    slug: str
