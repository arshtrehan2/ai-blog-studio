from typing import List, Optional

from pydantic import BaseModel


class AIUsage(BaseModel):
    input_tokens: int
    output_tokens: int


# — Improve ————————————————————————————————————————————————————————————

class ImproveRequest(BaseModel):
    content: str
    context: Optional[str] = None


class ImproveResponse(BaseModel):
    improved_content: str
    model: str
    usage: AIUsage


# — Summary ——————————————————————————————————————————————————————————

class SummaryRequest(BaseModel):
    content: str
    max_sentences: int = 3


class SummaryResponse(BaseModel):
    summary: str
    model: str
    usage: AIUsage


# — Tags ——————————————————————————————————————————————————————————————

class TagsRequest(BaseModel):
    content: str
    title: Optional[str] = None
    max_tags: int = 5


class TagsResponse(BaseModel):
    tags: List[str]
    model: str
    usage: AIUsage


# — SEO Title —————————————————————————————————————————————————————————

class SEOTitleRequest(BaseModel):
    content: str
    title: Optional[str] = None
    target_keyword: Optional[str] = None


class SEOTitleResponse(BaseModel):
    seo_title: str
    seo_description: str
    model: str
    usage: AIUsage


# — TLDR ————————————————————————————————————————————————————————————————

class TLDRRequest(BaseModel):
    content: str


class TLDRResponse(BaseModel):
    tldr: str
    model: str
    usage: AIUsage
