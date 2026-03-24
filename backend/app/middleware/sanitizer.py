import bleach
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


ALLOWED_TAGS: list[str] = []
ALLOWED_ATTRIBUTES: dict = {}


def sanitize_string(value: str) -> str:
    """Strip all HTML tags from a string."""
    return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)


def sanitize_dict(data: dict) -> dict:
    """Recursively sanitize string values in a dict."""
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = sanitize_string(value)
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value)
        elif isinstance(value, list):
            result[key] = [
                sanitize_string(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result
