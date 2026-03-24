import json
import time
import uuid
from typing import Optional

import anthropic
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.middleware.sanitizer import sanitize_string
from app.modules.ai.prompts import (
    IMPROVE_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    TAGS_SYSTEM_PROMPT,
    SEO_TITLE_SYSTEM_PROMPT,
    TLDR_SYSTEM_PROMPT,
)
from app.modules.posts.service import log_ai_usage

settings = get_settings()

MODEL = "claude-3-5-sonnet-20241022"


def get_anthropic_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


async def call_claude(
    system_prompt: str,
    user_content: str,
    max_tokens: int = 2048,
) -> tuple[str, dict]:
    """Call Claude API and return (text, usage_dict)."""
    client = get_anthropic_client()
    start = time.time()
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        latency_ms = int((time.time() - start) * 1000)
        text = message.content[0].text if message.content else ""
        usage = {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
            "latency_ms": latency_ms,
        }
        return text, usage
    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


async def improve_content(
    content: str,
    context: Optional[str],
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    clean_content = sanitize_string(content)
    user_message = clean_content
    if context:
        user_message = f"Context: {sanitize_string(context)}\n\n{clean_content}"

    text, usage = await call_claude(IMPROVE_SYSTEM_PROMPT, user_message, max_tokens=4096)
    await log_ai_usage(db, user_id, "improve", usage["input_tokens"], usage["output_tokens"], usage["latency_ms"])
    return {"improved_content": text, "model": MODEL, "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]}}


async def summarize_content(
    content: str,
    max_sentences: int,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    clean_content = sanitize_string(content)
    system = SUMMARY_SYSTEM_PROMPT.format(max_sentences=max_sentences)
    text, usage = await call_claude(system, clean_content, max_tokens=512)
    await log_ai_usage(db, user_id, "summary", usage["input_tokens"], usage["output_tokens"], usage["latency_ms"])
    return {"summary": text, "model": MODEL, "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]}}


async def suggest_tags(
    content: str,
    title: Optional[str],
    max_tags: int,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    clean_content = sanitize_string(content)
    user_message = clean_content
    if title:
        user_message = f"Title: {sanitize_string(title)}\n\n{clean_content}"

    system = TAGS_SYSTEM_PROMPT.format(max_tags=max_tags)
    text, usage = await call_claude(system, user_message, max_tokens=256)

    # Parse JSON array from response
    try:
        # Strip markdown code fences if present
        clean = text.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            clean = "\n".join(lines[1:-1]) if len(lines) > 2 else clean
        tags = json.loads(clean)
        if not isinstance(tags, list):
            tags = []
    except (json.JSONDecodeError, ValueError):
        tags = []

    await log_ai_usage(db, user_id, "tags", usage["input_tokens"], usage["output_tokens"], usage["latency_ms"])
    return {"tags": tags, "model": MODEL, "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]}}


async def generate_seo_title(
    content: str,
    title: Optional[str],
    target_keyword: Optional[str],
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    clean_content = sanitize_string(content)
    parts = [clean_content]
    if title:
        parts.insert(0, f"Current title: {sanitize_string(title)}")
    if target_keyword:
        parts.insert(0, f"Target keyword: {sanitize_string(target_keyword)}")
    user_message = "\n\n".join(parts)

    text, usage = await call_claude(SEO_TITLE_SYSTEM_PROMPT, user_message, max_tokens=256)

    # Parse JSON response
    try:
        clean = text.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            clean = "\n".join(lines[1:-1]) if len(lines) > 2 else clean
        data = json.loads(clean)
        seo_title = data.get("seo_title", "")
        seo_description = data.get("seo_description", "")
    except (json.JSONDecodeError, ValueError):
        seo_title = ""
        seo_description = ""

    await log_ai_usage(db, user_id, "seo-title", usage["input_tokens"], usage["output_tokens"], usage["latency_ms"])
    return {
        "seo_title": seo_title,
        "seo_description": seo_description,
        "model": MODEL,
        "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]},
    }


async def generate_tldr(
    content: str,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict:
    clean_content = sanitize_string(content)
    text, usage = await call_claude(TLDR_SYSTEM_PROMPT, clean_content, max_tokens=256)
    await log_ai_usage(db, user_id, "tldr", usage["input_tokens"], usage["output_tokens"], usage["latency_ms"])
    return {"tldr": text, "model": MODEL, "usage": {"input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]}}
