"""AI service — wraps Anthropic Claude SDK calls."""
import json
import time
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.modules.posts.models import AIUsageLog
from .prompts import (
    IMPROVE_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    TAGS_SYSTEM_PROMPT,
    SEO_TITLE_SYSTEM_PROMPT,
    TLDR_SYSTEM_PROMPT,
)
from .schemas import (
    ImproveRequest, ImproveResponse,
    SummaryRequest, SummaryResponse,
    TagsRequest, TagsResponse,
    SeoTitleRequest, SeoTitleResponse,
    TldrRequest, TldrResponse,
    UsageInfo,
)

settings = get_settings()

_anthropic_client = None


def _get_client():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _anthropic_client


def _call_claude(system_prompt: str, user_content: str) -> tuple[str, int, int, int]:
    """
    Returns (text, input_tokens, output_tokens, latency_ms).
    Raises HTTP 504 on timeout.
    """
    client = _get_client()
    try:
        start = time.monotonic()
        message = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        text = message.content[0].text
        return text, message.usage.input_tokens, message.usage.output_tokens, latency_ms
    except Exception as exc:
        error_str = str(exc).lower()
        if "timeout" in error_str or "timed out" in error_str:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI service timeout",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {exc}",
        )


def _log_usage(
    db: Session,
    user_id: UUID,
    tool: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    post_id: Optional[UUID] = None,
) -> None:
    log = AIUsageLog(
        user_id=user_id,
        tool=tool,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        post_id=post_id,
    )
    db.add(log)
    db.commit()


# ── Tool implementations ─────────────────────────────────────────────────────────

def improve_content(
    db: Session,
    user_id: UUID,
    payload: ImproveRequest,
) -> ImproveResponse:
    text, inp, out, lat = _call_claude(IMPROVE_SYSTEM_PROMPT, payload.content)
    _log_usage(db, user_id, "improve", inp, out, lat, payload.post_id)
    return ImproveResponse(
        improved_content=text,
        model=settings.anthropic_model,
        usage=UsageInfo(input_tokens=inp, output_tokens=out),
    )


def generate_summary(
    db: Session,
    user_id: UUID,
    payload: SummaryRequest,
) -> SummaryResponse:
    system = SUMMARY_SYSTEM_PROMPT.format(max_sentences=payload.max_sentences)
    text, inp, out, lat = _call_claude(system, payload.content)
    _log_usage(db, user_id, "summary", inp, out, lat, payload.post_id)
    return SummaryResponse(
        summary=text,
        model=settings.anthropic_model,
        usage=UsageInfo(input_tokens=inp, output_tokens=out),
    )


def suggest_tags(
    db: Session,
    user_id: UUID,
    payload: TagsRequest,
) -> TagsResponse:
    system = TAGS_SYSTEM_PROMPT.format(max_tags=payload.max_tags)
    user_content = payload.content
    if payload.title:
        user_content = f"Title: {payload.title}\n\n{payload.content}"
    text, inp, out, lat = _call_claude(system, user_content)
    try:
        tags = json.loads(text)
        if not isinstance(tags, list):
            tags = []
    except json.JSONDecodeError:
        # Fallback: split by comma
        tags = [t.strip().strip('"').lower() for t in text.split(",") if t.strip()]
    _log_usage(db, user_id, "tags", inp, out, lat, payload.post_id)
    return TagsResponse(
        tags=tags,
        model=settings.anthropic_model,
        usage=UsageInfo(input_tokens=inp, output_tokens=out),
    )


def generate_seo_title(
    db: Session,
    user_id: UUID,
    payload: SeoTitleRequest,
) -> SeoTitleResponse:
    user_content = payload.content
    if payload.title:
        user_content = f"Current title: {payload.title}\n\n{payload.content}"
    if payload.target_keyword:
        user_content = f"Target keyword: {payload.target_keyword}\n\n{user_content}"
    text, inp, out, lat = _call_claude(SEO_TITLE_SYSTEM_PROMPT, user_content)
    try:
        data = json.loads(text)
        seo_title = data.get("seo_title", "")
        seo_description = data.get("seo_description", "")
    except json.JSONDecodeError:
        seo_title = text[:60]
        seo_description = text[:155]
    _log_usage(db, user_id, "seo-title", inp, out, lat, payload.post_id)
    return SeoTitleResponse(
        seo_title=seo_title,
        seo_description=seo_description,
        model=settings.anthropic_model,
        usage=UsageInfo(input_tokens=inp, output_tokens=out),
    )


def generate_tldr(
    db: Session,
    user_id: UUID,
    payload: TldrRequest,
) -> TldrResponse:
    text, inp, out, lat = _call_claude(TLDR_SYSTEM_PROMPT, payload.content)
    _log_usage(db, user_id, "tldr", inp, out, lat, payload.post_id)
    return TldrResponse(
        tldr=text,
        model=settings.anthropic_model,
        usage=UsageInfo(input_tokens=inp, output_tokens=out),
    )
