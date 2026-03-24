import json
import time
from typing import Tuple

import anthropic

from app.config import settings
from app.modules.ai.prompts import (
    IMPROVE_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    TAGS_SYSTEM_PROMPT,
    SEO_TITLE_SYSTEM_PROMPT,
    TLDR_SYSTEM_PROMPT,
)
from app.modules.ai.schemas import UsageInfo


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _call_claude(system_prompt: str, user_content: str) -> Tuple[str, UsageInfo, int]:
    client = _get_client()
    start = time.time()
    response = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    latency_ms = int((time.time() - start) * 1000)
    text = response.content[0].text
    usage = UsageInfo(
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
    return text, usage, latency_ms


def improve_content(content: str, context: str = None) -> Tuple[str, UsageInfo, int]:
    user_content = content
    if context:
        user_content = f"Context: {context}\n\n{content}"
    return _call_claude(IMPROVE_SYSTEM_PROMPT, user_content)


def generate_summary(content: str, max_sentences: int = 3) -> Tuple[str, UsageInfo, int]:
    system = SUMMARY_SYSTEM_PROMPT.format(max_sentences=max_sentences)
    return _call_claude(system, content)


def suggest_tags(content: str, title: str = None, max_tags: int = 5) -> Tuple[list, UsageInfo, int]:
    system = TAGS_SYSTEM_PROMPT.format(max_tags=max_tags)
    user_content = content
    if title:
        user_content = f"Title: {title}\n\n{content}"
    text, usage, latency = _call_claude(system, user_content)
    try:
        tags = json.loads(text.strip())
        if not isinstance(tags, list):
            tags = []
    except (json.JSONDecodeError, ValueError):
        tags = []
    return tags, usage, latency


def generate_seo_title(
    content: str, title: str = None, target_keyword: str = None
) -> Tuple[str, str, UsageInfo, int]:
    user_content = content
    if title:
        user_content = f"Current title: {title}\n\n{user_content}"
    if target_keyword:
        user_content = f"Target keyword: {target_keyword}\n\n{user_content}"
    text, usage, latency = _call_claude(SEO_TITLE_SYSTEM_PROMPT, user_content)
    try:
        data = json.loads(text.strip())
        seo_title = data.get("seo_title", "")
        seo_description = data.get("seo_description", "")
    except (json.JSONDecodeError, ValueError):
        seo_title = ""
        seo_description = ""
    return seo_title, seo_description, usage, latency


def generate_tldr(content: str) -> Tuple[str, UsageInfo, int]:
    return _call_claude(TLDR_SYSTEM_PROMPT, content)
