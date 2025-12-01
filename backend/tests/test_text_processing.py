"""
Tests for text processing utilities.
"""

from app.services.text_processing import (
    clean_text,
    extract_urls,
    extract_emails,
    process_text_for_analysis,
    ProcessedText,
)


def test_clean_text_normalizes_newlines_and_trims():
    raw = " Hello \r\n\r\nWorld \n\n\nTest  "
    cleaned = clean_text(raw)

    # Should normalize to single blank lines and trimmed ends
    assert cleaned == " Hello\n\nWorld \n\nTest"


def test_extract_urls_and_emails():
    text = "Visit http://example.com or https://test.com and email me at a@b.com, a@b.com."
    urls = extract_urls(text)
    emails = extract_emails(text)

    assert "http://example.com" in urls
    assert "https://test.com" in urls
    # Deduplicated
    assert emails == ["a@b.com"]


def test_process_text_for_analysis_returns_structured_result():
    raw = "Contact us at support@example.com or visit https://example.com/page"
    result = process_text_for_analysis(raw)

    assert isinstance(result, ProcessedText)
    assert result.original == raw
    assert "support@example.com" in result.emails
    assert "https://example.com/page" in result.urls
    assert isinstance(result.cleaned, str)


