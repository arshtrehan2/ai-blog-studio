"""Input sanitization middleware helpers."""
import bleach

# Tags allowed in stored markdown (rendered via react-markdown, not raw HTML)
ALLOWED_TAGS: list[str] = [
    "p", "br", "strong", "em", "u", "s", "code", "pre",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "blockquote",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "hr",
]

ALLOWED_ATTRIBUTES: dict = {
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "pre": ["class"],
}


def sanitize_html(text: str) -> str:
    """Strip disallowed HTML tags / attributes from user-provided content."""
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )
