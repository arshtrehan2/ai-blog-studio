from typing import Optional
from uuid import UUID
from pydantic import BaseModel, field_validator


MAX_CONTENT_LENGTH = 10_000


class UsageInfo(BaseModel):
    input_tokens: int
    output_tokens: int


# ── Improve ─────────────────────────────────────────────────────────────────

class ImproveRequest(BaseModel):
    content: str
    context: Optional[str] = None
    post_id: Optional[UUID] = None

    @field_validator("content")
    @classmethod
    def content_length(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be empty")
        if len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f"content must be at most {MAX_CONTENT_LENGTH} characters")
        return v


class ImproveResponse(BaseModel):
    improved_content: str
    model: str
    usage: UsageInfo


# ── Summary ─────────────────────────────────────────────────────────────────

class SummaryRequest(BaseModel):
    content: str
    max_sentences: int = 3
    post_id: Optional[UUID] = None

    @field_validator("content")
    @classmethod
    def content_length(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be empty")
        if len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f"content must be at most {MAX_CONTENT_LENGTH} characters")
        return v


class SummaryResponse(BaseModel):
    summary: str
    model: str
    usage: UsageInfo


# ── Tags ────────────────────────────────────────────────────────────────────

class TagsRequest(BaseModel):
    content: str
    title: Optional[str] = None
    max_tags: int = 5
    post_id: Optional[UUID] = None

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be empty")
        return v


class TagsResponse(BaseModel):
    tags: list[str]
    model: str
    usage: UsageInfo


# ── SEO Title ───────────────────────────────────────────────────────────────

class SeoTitleRequest(BaseModel):
    content: str
    title: Optional[str] = None
    target_keyword: Optional[str] = None
    post_id: Optional[UUID] = None

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be empty")
        return v


class SeoTitleResponse(BaseModel):
    seo_title: str
    seo_description: str
    model: str
    usage: UsageInfo


# ── TLDR ────────────────────────────────────────────────────────────────────

class TldrRequest(BaseModel):
    content: str
    post_id: Optional[UUID] = None

    @field_validator("content")
    @classmethod
    def content_length(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be empty")
        if len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f"content must be at most {MAX_CONTENT_LENGTH} characters")
        return v


class TldrResponse(BaseModel):
    tldr: str
    model: str
    usage: UsageInfo
