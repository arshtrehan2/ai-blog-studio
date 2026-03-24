import bleach


def sanitize_html(text: str) -> str:
    """Strip all HTML tags from input text."""
    return bleach.clean(text, tags=[], strip=True)


def sanitize_string(value: str, max_length: int = None) -> str:
    """Sanitize a string input: strip HTML and optionally truncate."""
    clean = sanitize_html(value)
    if max_length and len(clean) > max_length:
        clean = clean[:max_length]
    return clean
