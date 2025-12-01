"""
Text processing utilities for cleaned AI-ready text.

Responsibilities:
- Clean raw text (from UI Automation or OCR)
- Extract URLs and email addresses
- Provide helpers that keep business logic out of routes
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

URL_PATTERN = re.compile(
    r"http[s]?://(?:[a-zA-Z0-9]|[$-_@.&+]|[!*'(),]|"
    r"(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
)


@dataclass
class ProcessedText:
    """
    Structured representation of processed text for AI analysis.

    Attributes:
        original: Original raw text.
        cleaned:  Cleaned/normalized text.
        urls:     List of URLs found in the text.
        emails:   List of email addresses found in the text.
    """

    original: str
    cleaned: str
    urls: List[str]
    emails: List[str]


def clean_text(text: str) -> str:
    """
    Normalize text for AI analysis:
    - Strip leading/trailing whitespace
    - Normalize line endings to '\n'
    - Collapse excessive blank lines
    """
    if not text:
        return ""

    # Normalize newlines
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strip trailing spaces on each line
    lines = [line.rstrip() for line in normalized.split("\n")]

    # Collapse multiple blank lines
    cleaned_lines: List[str] = []
    blank = False
    for line in lines:
        if line.strip() == "":
            if not blank:
                cleaned_lines.append("")  # keep a single blank line
                blank = True
        else:
            cleaned_lines.append(line)
            blank = False

    cleaned = "\n".join(cleaned_lines).strip()
    return cleaned


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    if not text:
        return []
    return list(dict.fromkeys(URL_PATTERN.findall(text)))


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    if not text:
        return []
    return list(dict.fromkeys(EMAIL_PATTERN.findall(text)))


def process_text_for_analysis(text: str) -> ProcessedText:
    """
    High-level helper to clean text and extract URLs/emails.
    """
    cleaned = clean_text(text)
    urls = extract_urls(cleaned)
    emails = extract_emails(cleaned)
    return ProcessedText(original=text, cleaned=cleaned, urls=urls, emails=emails)


