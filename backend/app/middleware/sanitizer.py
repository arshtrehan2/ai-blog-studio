import bleach


def sanitize_html(content: str) -> str:
    """Strip all HTML tags — used before persisting markdown to DB."""
    return bleach.clean(content, tags=[], strip=True)


def sanitize_for_ai(content: str, max_length: int = 10_000) -> str:
    """
    Strip HTML and enforce a maximum character limit before sending
    content to the Claude API.
    """
    cleaned = bleach.clean(content, tags=[], strip=True)
    if len(cleaned) > max_length:
        raise ValueError(
            f"Content exceeds the maximum allowed length of {max_length} characters."
        )
    return cleaned
