import re

# Common UI noise patterns
UI_PATTERNS = [
    r"File\s+Edit\s+View\s+Help",
    r"Protection ON",
    r"Pause",
    r"Ln\d+,\s*Col\d+.*",
    r"Windows\s*\(CRLF\).*",
    r"UTF-8",
]

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Normalize newlines
    text = text.replace("\r", "\n")

    # Remove known UI noise
    for pattern in UI_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if len(line) > 3:
            lines.append(line)

    # Remove duplicate lines (preserve order)
    seen = set()
    cleaned_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def chunk_text(text: str, max_words: int = 500):
    """
    Split cleaned text into LLM-safe chunks
    """
    if not text:
        return []

    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
