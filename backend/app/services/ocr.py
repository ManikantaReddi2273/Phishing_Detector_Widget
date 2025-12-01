"""
OCR fallback service

This module implements OCR as a **fallback** when direct Windows UI Automation
screen text extraction is not available for a given region/window.

Design goals:
- Never crash the backend (all external errors are caught and logged)
- Prefer `easyocr` when available
- Fallback to `pytesseract` when `easyocr` is not available or fails
- Work even when the underlying OCR engines or native binaries are missing
  by returning a safe "unavailable" result instead of raising exceptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal

from app.core.logger import logger

EngineName = Literal["easyocr", "pytesseract", "unavailable"]


@dataclass
class OcrResult:
    """
    Result of an OCR operation.

    Attributes:
        engine:  Which OCR engine was used ("easyocr", "pytesseract", "unavailable").
        text:    Extracted text (may be empty).
        error:   Optional error message if OCR failed or is unavailable.
    """

    engine: EngineName
    text: str
    error: Optional[str] = None


def _run_easyocr(image_path: str, languages: Optional[list[str]] = None) -> OcrResult:
    """
    Try to run OCR using easyocr.
    Returns an OcrResult; never raises to the caller.
    """
    try:
        import easyocr  # type: ignore[import]

        langs = languages or ["en"]
        logger.debug(f"Running easyocr on '{image_path}' with languages={langs}")

        # gpu=False to avoid GPU dependency
        reader = easyocr.Reader(langs, gpu=False)
        # detail=0 → only text strings (no boxes/ confidences)
        lines = reader.readtext(image_path, detail=0)
        text = "\n".join(line.strip() for line in lines if isinstance(line, str))

        return OcrResult(engine="easyocr", text=text)

    except ImportError as exc:
        logger.info(f"easyocr not installed, skipping: {exc}")
        return OcrResult(engine="unavailable", text="", error="easyocr not installed")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning(f"easyocr OCR failed: {exc}")
        return OcrResult(engine="unavailable", text="", error=f"easyocr failed: {exc}")


def _run_pytesseract(image_path: str) -> OcrResult:
    """
    Try to run OCR using pytesseract.
    Returns an OcrResult; never raises to the caller.
    """
    try:
        from PIL import Image  # type: ignore[import]
        import pytesseract  # type: ignore[import]

        logger.debug(f"Running pytesseract on '{image_path}'")

        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return OcrResult(engine="pytesseract", text=text or "")

    except ImportError as exc:
        logger.info(f"pytesseract or Pillow not installed, skipping: {exc}")
        return OcrResult(
            engine="unavailable",
            text="",
            error="pytesseract or Pillow not installed",
        )
    except Exception as exc:  # pragma: no cover - defensive
        # pytesseract raises TesseractNotFoundError if binary is missing
        logger.warning(f"pytesseract OCR failed: {exc}")
        return OcrResult(engine="unavailable", text="", error=f"pytesseract failed: {exc}")


def perform_ocr(image_path: str, languages: Optional[list[str]] = None) -> OcrResult:
    """
    Perform OCR on the given image path using the configured fallback strategy.

    Strategy:
    1. Try easyocr (if installed and succeeds)  → return that result.
    2. Otherwise, try pytesseract               → return that result if succeeds.
    3. If both are unavailable/fail, return engine='unavailable' with an error.

    This function NEVER raises exceptions; it always returns an OcrResult.
    """
    logger.info(f"Starting OCR fallback for image: {image_path}")

    # Try easyocr first
    easyocr_result = _run_easyocr(image_path, languages=languages)
    if easyocr_result.engine == "easyocr" and not easyocr_result.error:
        logger.info(
            f"OCR completed using easyocr, chars={len(easyocr_result.text or '')}"
        )
        return easyocr_result

    # Then try pytesseract
    pytesseract_result = _run_pytesseract(image_path)
    if pytesseract_result.engine == "pytesseract" and not pytesseract_result.error:
        logger.info(
            f"OCR completed using pytesseract, chars={len(pytesseract_result.text or '')}"
        )
        return pytesseract_result

    # Both unavailable or failed – build combined error message
    combined_error = "OCR engines unavailable or failed"
    details = []
    if easyocr_result.error:
        details.append(f"easyocr: {easyocr_result.error}")
    if pytesseract_result.error:
        details.append(f"pytesseract: {pytesseract_result.error}")
    if details:
        combined_error += " (" + " | ".join(details) + ")"

    logger.warning(combined_error)
    return OcrResult(engine="unavailable", text="", error=combined_error)


