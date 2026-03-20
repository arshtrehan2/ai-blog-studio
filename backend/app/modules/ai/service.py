"""AI service — wraps the Anthropic Claude SDK for every AI tool."""
import json
import time
from typing import Dict, Optional

import anthropic
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.middleware.sanitizer import sanitize_for_ai
from app.modules.ai.prompts import (
    IMPROVE_SYSTEM_PROMPT,
    SEO_TITLE_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    TAGS_SYSTEM_PROMPT,
    TLDR_SYSTEM_PROMPT,
)
from app.modules.auth.models import User
from app.modules.posts.models import AIUsageLog

_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
MODEL = "claude-3-5-sonnet-20241022"


# ── Shared helpers ───────────────────────────────────────────────────────

def _call_claude(
    system: str,
    user_content: str,
    max_tokens: int = 2048,
) -> anthropic.types.Message:
    try:
        return _client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_content}],
        )
    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")


def _log_usage(
    db: Session,
    user: User,
    tool: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: Optional[int] = None,
    post_id: Optional[str] = None,
) -> None:
    log = AIUsageLog(
        user_id=user.id,
        tool=tool,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        post_id=post_id,
    )
    db.add(log)
    db.commit()


def _usage_dict(msg: anthropic.types.Message) -> Dict[str, int]:
    return {
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
    }


# ── Tool implementations ────────────────────────────────────────────────────

def improve_content(
    db: Session, user: User, content: str, context: Optional[str] = None
) -> dict:
    content = sanitize_for_ai(content)
    system = IMPROVE_SYSTEM_PROMPT
    if context:
        system += f"\n\nContext: {context}"

    t0 = time.perf_counter()
    msg = _call_claude(system, content, max_tokens=4096)
    latency = int((time.perf_counter() - t0) * 1000)

    _log_usage(db, user, "improve", msg.usage.input_tokens, msg.usage.output_tokens, latency)
    return {"improved_content": msg.content[0].text, "model": MODEL, "usage": _usage_dict(msg)}


def generate_summary(
    db: Session, user: User, content: str, max_sentences: int = 3
) -> dict:
    content = sanitize_for_ai(content)
    system = SUMMARY_SYSTEM_PROMPT.format(max_sentences=max_sentences)

    t0 = time.perf_counter()
    msg = _call_claude(system, content, max_tokens=512)
    latency = int((time.perf_counter() - t0) * 1000)

    _log_usage(db, user, "summary", msg.usage.input_tokens, msg.usage.output_tokens, latency)
    return {"summary": msg.content[0].text, "model": MODEL, "usage": _usage_dict(msg)}


def suggest_tags(
    db: Session,
    user: User,
    content: str,
    title: Optional[str] = None,
    max_tags: int = 5,
) -> dict:
    content = sanitize_for_ai(content)
    system = TAGS_SYSTEM_PROMPT.format(max_tags=max_tags)
    user_content = f"Title: {title}\n\n{content}" if title else content

    t0 = time.perf_counter()
    msg = _call_claude(system, user_content, max_tokens=256)
    latency = int((time.perf_counter() - t0) * 1000)

    raw = msg.content[0].text.strip()
    try:
        tags = json.loads(raw)
        if not isinstance(tags, list):
            tags = []
    except Exception:
        tags = []

    _log_usage(db, user, "tags", msg.usage.input_tokens, msg.usage.output_tokens, latency)
    return {"tags": tags, "model": MODEL, "usage": _usage_dict(msg)}


def generate_seo_title(
    db: Session,
    user: User,
    content: str,
    title: Optional[str] = None,
    target_keyword: Optional[str] = None,
) -> dict:
    content = sanitize_for_ai(content)
    parts = []
    if title:
        parts.append(f"Current title: {title}")
    if target_keyword:
        parts.append(f"Target keyword: {target_keyword}")
    parts.append(content)
    user_content = "\n\n".join(parts)

    t0 = time.perf_counter()
    msg = _call_claude(SEO_TITLE_SYSTEM_PROMPT, user_content, max_tokens=256)
    latency = int((time.perf_counter() - t0) * 1000)

    raw = msg.content[0].text.strip()
    try:
        data = json.loads(raw)
        seo_title = data.get("seo_title", "")
        seo_description = data.get("seo_description", "")
    except Exception:
        seo_title, seo_description = "", raw

    _log_usage(db, user, "seo-title", msg.usage.input_tokens, msg.usage.output_tokens, latency)
    return {
        "seo_title": seo_title,
        "seo_description": seo_description,
        "model": MODEL,
        "usage": _usage_dict(msg),
    }


def generate_tldr(db: Session, user: User, content: str) -> dict:
    content = sanitize_for_ai(content)

    t0 = time.perf_counter()
    msg = _call_claude(TLDR_SYSTEM_PROMPT, content, max_tokens=128)
    latency = int((time.perf_counter() - t0) * 1000)

    _log_usage(db, user, "tldr", msg.usage.input_tokens, msg.usage.output_tokens, latency)
    return {"tldr": msg.content[0].text, "model": MODEL, "usage": _usage_dict(msg)}
