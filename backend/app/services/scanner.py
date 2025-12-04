"""Continuous background screen scanning service.

This module runs a background loop that periodically scans the active
Windows screen using UI Automation and sends the extracted text through
our LLM-based phishing analyzer. The latest result is stored in memory
and exposed via simple helper functions so API routes (or other
components) can read it.

Detection is **LLM-only** – this module never uses any heuristic or
rule-based detection.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings
from app.core.logger import logger
from app.models.schemas import AnalyzeResponse
from app.services.text_extractor import extract_screen_text
from app.services.text_processing import process_text_for_analysis
from app.services.ai_analyzer import analyze_with_llm


_latest_result: Optional[AnalyzeResponse] = None
_last_scan_at: Optional[datetime] = None
_last_error: Optional[str] = None
_is_running: bool = False
_scan_task: Optional[asyncio.Task] = None


def _set_state(*, result: Optional[AnalyzeResponse], error: Optional[str]) -> None:
    global _latest_result, _last_scan_at, _last_error
    _latest_result = result
    _last_scan_at = datetime.now(timezone.utc)
    _last_error = error


async def _scan_once() -> None:
    """Perform a single scan of the active window and update state."""
    try:
        extraction = extract_screen_text()
        if not extraction.raw_text or not extraction.raw_text.strip():
            logger.debug("[scanner] No text extracted from screen; skipping analysis")
            _set_state(result=None, error="No text extracted from screen")
            return

        processed = process_text_for_analysis(extraction.raw_text)
        logger.info(
            "[scanner] Running LLM phishing analysis (len=%s, urls=%s, emails=%s)",
            len(processed.cleaned or processed.original),
            len(processed.urls),
            len(processed.emails),
        )

        response = analyze_with_llm(processed)
        # Make sure extracted_text reflects the full raw screen capture
        response.extracted_text = extraction.raw_text
        _set_state(result=response, error=None)

        logger.info(
            "[scanner] Scan completed: is_phishing=%s risk_level=%s status=%s",
            response.is_phishing,
            response.risk_level,
            response.status,
        )

    except Exception as exc:  # pragma: no cover - defensive network / UI errors
        logger.error("[scanner] Continuous scan failed: %s", exc, exc_info=True)
        _set_state(result=None, error=str(exc))


async def _scan_loop() -> None:
    """Background loop that continuously scans at a fixed interval."""
    global _is_running
    logger.info(
        "[scanner] Starting continuous scan loop (interval=%ss)",
        settings.SCAN_INTERVAL_SECONDS,
    )
    _is_running = True

    try:
        # Initial small delay so the app can finish startup
        await asyncio.sleep(2)
        while True:
            await _scan_once()
            await asyncio.sleep(max(1, settings.SCAN_INTERVAL_SECONDS))
    except asyncio.CancelledError:  # pragma: no cover - shutdown path
        logger.info("[scanner] Scan loop cancelled; shutting down")
        raise
    finally:
        _is_running = False


def start_background_scanner() -> None:
    """Start the background scanning task if not already running.

    This is intended to be called from the FastAPI startup event.
    """
    global _scan_task
    if _scan_task is not None and not _scan_task.done():
        logger.debug("[scanner] Background scanner already running; skipping start")
        return

    loop = asyncio.get_event_loop()
    _scan_task = loop.create_task(_scan_loop())
    logger.info("[scanner] Background scanner task created")


def get_latest_scan_state() -> dict:
    """Return a serializable representation of the latest scan state.

    The structure is intentionally simple so that API routes can easily
    wrap it in a Pydantic model:

    {
      "last_scan_at": ISO-8601 string or None,
      "has_result": bool,
      "error": str | None,
      "result": AnalyzeResponse | None
    }
    """
    return {
      "last_scan_at": _last_scan_at.isoformat().replace("+00:00", "Z") if _last_scan_at else None,
      "has_result": _latest_result is not None,
      "error": _last_error,
      "result": _latest_result,
    }
