import bleach
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

ALLOWED_TAGS: list = []
ALLOWED_ATTRIBUTES: dict = {}


def sanitize_string(value: str) -> str:
    """Strip all HTML tags from a string using bleach."""
    return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)


def sanitize_content(value: str) -> str:
    """Sanitize markdown content — strip dangerous HTML but allow safe markdown."""
    safe_tags = [
        "p", "br", "strong", "em", "code", "pre", "blockquote",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li",
        "a", "img",
    ]
    safe_attrs = {
        "a": ["href", "title"],
        "img": ["src", "alt", "title"],
    }
    return bleach.clean(value, tags=safe_tags, attributes=safe_attrs, strip=True)
