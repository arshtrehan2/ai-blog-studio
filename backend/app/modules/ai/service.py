import json
import time
from sqlalchemy.orm import Session
from anthropic import Anthropic
from typing import Optional
from .models import AIUsageLog
from .prompts import (
    IMPROVE_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    TAGS_SYSTEM_PROMPT,
    SEO_TITLE_SYSTEM_PROMPT,
    TLDR_SYSTEM_PROMPT,
)
from ...config import settings

MODEL = "claude-3-5-sonnet-20241022"


def get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def log_usage(
    db: Session,
    user_id: str,
    tool: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    post_id: Optional[str] = None,
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
    try:
        db.commit()
    except Exception:
        db.rollback()


def call_claude(
    system_prompt: str, user_content: str
) -> tuple:
    """Returns (text, model, input_tokens, output_tokens, latency_ms)."""
    client = get_anthropic_client()
    start = time.time()
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    latency_ms = int((time.time() - start) * 1000)
    text = response.content[0].text
    return (
        text,
        response.model,
        response.usage.input_tokens,
        response.usage.output_tokens,
        latency_ms,
    )


def improve_content(
    db: Session, user_id: str, content: str, context: Optional[str] = None
) -> dict:
    system = IMPROVE_SYSTEM_PROMPT
    if context:
        system += f" Context: {context}"
    text, model, input_tokens, output_tokens, latency_ms = call_claude(
        system, content
    )
    log_usage(db, user_id, "improve", input_tokens, output_tokens, latency_ms)
    return {
        "improved_content": text,
        "model": model,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    }


def generate_summary(
    db: Session, user_id: str, content: str, max_sentences: int = 3
) -> dict:
    system = SUMMARY_SYSTEM_PROMPT.format(max_sentences=max_sentences)
    text, model, input_tokens, output_tokens, latency_ms = call_claude(
        system, content
    )
    log_usage(db, user_id, "summary", input_tokens, output_tokens, latency_ms)
    return {
        "summary": text,
        "model": model,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    }


def generate_tags(
    db: Session,
    user_id: str,
    content: str,
    title: Optional[str] = None,
    max_tags: int = 5,
) -> dict:
    system = TAGS_SYSTEM_PROMPT.format(max_tags=max_tags)
    user_content = f"Title: {title}\n\n{content}" if title else content
    text, model, input_tokens, output_tokens, latency_ms = call_claude(
        system, user_content
    )
    log_usage(db, user_id, "tags", input_tokens, output_tokens, latency_ms)
    try:
        tags = json.loads(text)
        if not isinstance(tags, list):
            tags = []
    except json.JSONDecodeError:
        tags = [
            t.strip().strip('"').strip("'")
            for t in text.strip("[]").split(",")
            if t.strip()
        ]
    return {
        "tags": tags,
        "model": model,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    }


def generate_seo_title(
    db: Session,
    user_id: str,
    content: str,
    title: Optional[str] = None,
    target_keyword: Optional[str] = None,
) -> dict:
    user_content = content
    if title:
        user_content = f"Current title: {title}\n\n{user_content}"
    if target_keyword:
        user_content = f"Target keyword: {target_keyword}\n\n{user_content}"
    text, model, input_tokens, output_tokens, latency_ms = call_claude(
        SEO_TITLE_SYSTEM_PROMPT, user_content
    )
    log_usage(db, user_id, "seo-title", input_tokens, output_tokens, latency_ms)
    try:
        result = json.loads(text)
        seo_title = result.get("seo_title", "")
        seo_description = result.get("seo_description", "")
    except json.JSONDecodeError:
        seo_title = text[:60]
        seo_description = text[:155]
    return {
        "seo_title": seo_title,
        "seo_description": seo_description,
        "model": model,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    }


def generate_tldr(db: Session, user_id: str, content: str) -> dict:
    text, model, input_tokens, output_tokens, latency_ms = call_claude(
        TLDR_SYSTEM_PROMPT, content
    )
    log_usage(db, user_id, "tldr", input_tokens, output_tokens, latency_ms)
    return {
        "tldr": text,
        "model": model,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    }
