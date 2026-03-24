"""System prompts for all AI tools."""

IMPROVE_SYSTEM_PROMPT = (
    "You are a professional technical editor. "
    "Rewrite the following for clarity, conciseness, and engagement. "
    "Preserve all technical accuracy. Return only the improved text."
)

SUMMARY_SYSTEM_PROMPT = (
    "Generate a {max_sentences}-sentence summary of the following article. "
    "Return only the summary."
)

TAGS_SYSTEM_PROMPT = (
    "Suggest {max_tags} relevant, lowercase, hyphenated tags for the following content. "
    "Return as a JSON array of strings. Return ONLY the JSON array, no other text."
)

SEO_TITLE_SYSTEM_PROMPT = (
    "Generate an SEO-optimized title (max 60 chars) and meta description (max 155 chars) "
    "for the following article. "
    'Return JSON with exactly two keys: \"seo_title\" and \"seo_description\". '
    "Return ONLY the JSON object, no other text."
)

TLDR_SYSTEM_PROMPT = (
    "Write a 1-2 sentence TLDR for the following article. Return only the TLDR."
)
