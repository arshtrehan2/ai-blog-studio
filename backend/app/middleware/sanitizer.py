import bleach

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "code", "pre",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "a", "img",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
}

MAX_CONTENT_LENGTH = 10_000


def sanitize_content(content: str) -> str:
    """Strip dangerous HTML from markdown content."""
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


def validate_content_length(content: str, max_length: int = MAX_CONTENT_LENGTH) -> bool:
    return len(content) <= max_length
