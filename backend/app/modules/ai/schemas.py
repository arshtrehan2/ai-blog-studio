from pydantic import BaseModel
from typing import Optional, List


class UsageInfo(BaseModel):
    input_tokens: int
    output_tokens: int


class ImproveRequest(BaseModel):
    content: str
    context: Optional[str] = None


class ImproveResponse(BaseModel):
    improved_content: str
    model: str
    usage: UsageInfo


class SummaryRequest(BaseModel):
    content: str
    max_sentences: int = 3


class SummaryResponse(BaseModel):
    summary: str
    model: str
    usage: UsageInfo


class TagsRequest(BaseModel):
    content: str
    title: Optional[str] = None
    max_tags: int = 5


class TagsResponse(BaseModel):
    tags: List[str]
    model: str
    usage: UsageInfo


class SEOTitleRequest(BaseModel):
    content: str
    title: Optional[str] = None
    target_keyword: Optional[str] = None


class SEOTitleResponse(BaseModel):
    seo_title: str
    seo_description: str
    model: str
    usage: UsageInfo


class TLDRRequest(BaseModel):
    content: str


class TLDRResponse(BaseModel):
    tldr: str
    model: str
    usage: UsageInfo
