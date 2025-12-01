"""
Tests for OCR fallback service.

These tests are intentionally light-weight and do NOT require that
easyocr / pytesseract / Tesseract binaries are present. They only
verify that:
- perform_ocr() never raises
- it always returns an OcrResult with expected fields
"""

from app.services.ocr import OcrResult, perform_ocr


def test_perform_ocr_returns_result_object_for_invalid_path():
    """
    Even for an invalid/non-existent image path, perform_ocr should
    return a safe OcrResult and not raise an exception.
    """
    result = perform_ocr("non_existent_image_path.png")

    assert isinstance(result, OcrResult)
    assert result.engine in {"easyocr", "pytesseract", "unavailable"}
    assert isinstance(result.text, str)


def test_perform_ocr_unavailable_is_safe():
    """
    When OCR engines are not available or fail, engine should be
    'unavailable' and an error message should be provided, but it
    must still be a valid OcrResult.
    """
    result = perform_ocr("non_existent_image_path.png")

    if result.engine == "unavailable":
        assert result.error is not None
        assert isinstance(result.error, str)


