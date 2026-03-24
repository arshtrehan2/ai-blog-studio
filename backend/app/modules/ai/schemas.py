import uuid
from typing import Optional
from pydantic import BaseModel, field_validator

MAX_CONTENT_LENGTH = 10_000


class UsageInfo(BaseModel):
    input_tokens: int
    output_tokens: int


class ImproveRequest(BaseModel):
    content: str
    context: Optional[str] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        if len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Content must be {MAX_CONTENT_LENGTH} characters or less")
        return v


class ImproveResponse(BaseModel):
    improved_content: str
    model: str
    usage: UsageInfo


class SummaryRequest(BaseModel):
    content: str
    max_sentences: int = 3

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        if len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Content must be {MAX_CONTENT_LENGTH} characters or less")
        return v


class SummaryResponse(BaseModel):
    summary: str
    model: str
    usage: UsageInfo


class TagsRequest(BaseModel):
    content: str
    title: Optional[str] = None
    max_tags: int = 5

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v


class TagsResponse(BaseModel):
    tags: list[str]
    model: str
    usage: UsageInfo


class SEOTitleRequest(BaseModel):
    content: str
    title: Optional[str] = None
    target_keyword: Optional[str] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v


class SEOTitleResponse(BaseModel):
    seo_title: str
    seo_description: str
    model: str
    usage: UsageInfo


class TLDRRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        if len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Content must be {MAX_CONTENT_LENGTH} characters or less")
        return v


class TLDRResponse(BaseModel):
    tldr: str
    model: str
    usage: UsageInfo
