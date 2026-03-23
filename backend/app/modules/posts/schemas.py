from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class AuthorInfo(BaseModel):
    id: uuid.UUID
    display_name: str

    model_config = {"from_attributes": True}


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
    id: uuid.UUID
    title: str
    slug: str
    content: str
    tags: List[str] = []
    status: str
    summary: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    author_id: Optional[uuid.UUID] = None
    author: Optional[AuthorInfo] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListItem(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    summary: Optional[str] = None
    tags: List[str] = []
    author: AuthorInfo
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
    id: uuid.UUID
    status: str
    published_at: datetime
    slug: str

    model_config = {"from_attributes": True}
