"""
Tests for screen text extraction service

These tests are designed to be safe and not depend on the actual presence of
Windows UI Automation on the CI machine. They only validate:
- The function returns a ScreenTextExtractionResult
- The fields have the correct types
- The method field is one of the expected values
"""

from app.services.text_extractor import (
    extract_screen_text,
    ScreenTextExtractionResult,
    WindowText,
)


def test_extract_screen_text_returns_result_object():
    """extract_screen_text should always return a ScreenTextExtractionResult."""
    result = extract_screen_text()

    assert isinstance(result, ScreenTextExtractionResult)
    assert result.method in {"uia", "fallback", "unavailable"}
    assert isinstance(result.windows, list)
    assert isinstance(result.raw_text, str)


def test_extract_screen_text_window_structure():
    """
    If any windows are returned, they must follow the WindowText structure.
    We don't assert there MUST be windows, because that depends on the runtime
    environment and open applications.
    """
    result = extract_screen_text()

    for w in result.windows:
        assert isinstance(w, WindowText)
        assert isinstance(w.title, str)
        assert isinstance(w.text, str)


