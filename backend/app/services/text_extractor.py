"""
Screen text extraction service using Windows UI Automation (primary)

This module is responsible for extracting ALL visible text on the screen
as real text (not images), preserving structure and context as much as possible.

Design goals (aligned with project idea):
- Capture all visible text on the entire screen
- Include headers, labels, buttons, menu items, status bars, etc.
- Work safely even if Windows UI Automation packages are not available
- Never crash the backend if extraction fails

Note:
- This implementation provides a safe, working foundation that can run on any
  machine. When Windows UI Automation packages are available (pywin32, comtypes)
  it will attempt real extraction. Otherwise it will return an empty-but-valid
  result and log a warning. This keeps execution clean and error‑free.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app.core.logger import logger


@dataclass
class WindowText:
    """
    Represents text extracted from a single window.

    Attributes:
        title: The window title (caption).
        text:  All visible text content extracted from this window.
    """

    title: str
    text: str


@dataclass
class ScreenTextExtractionResult:
    """
    Result of a screen text extraction operation.

    Attributes:
        method:   Which method was used ("uia", "fallback", "unavailable").
        windows:  List of per‑window text objects.
        raw_text: Combined plain text for all windows (for AI analysis).
        error:    Optional error message if extraction failed or degraded.
    """

    method: str
    windows: List[WindowText] = field(default_factory=list)
    raw_text: str = ""
    error: Optional[str] = None


def extract_screen_text() -> ScreenTextExtractionResult:
    """
    Extract all visible text from the entire screen.

    Primary strategy:
        - Use Windows UI Automation (via pywin32 + comtypes) to enumerate
          top‑level windows and read their text content.

    Fallback behaviour:
        - If UI Automation libraries are not available or an error occurs,
          return a result with method='unavailable' and an empty text payload,
          but DO NOT raise exceptions. This keeps the backend stable.

    Returns:
        ScreenTextExtractionResult describing the extracted on‑screen text.
    """

    try:
        # Try to import UI Automation dependencies lazily so the module can
        # still be imported even if these aren't installed yet.
        import win32gui  # type: ignore[import]
        import win32con  # type: ignore[import]
        import comtypes.client  # type: ignore[import]

        try:
            from comtypes.gen import UIAutomationClient  # type: ignore[import]
        except Exception:  # pragma: no cover - generated module edge cases
            # Generate UIAutomationClient wrapper if not already generated
            logger.debug("Generating UIAutomationClient COM wrapper")
            comtypes.client.GetModule("UIAutomationCore.dll")
            from comtypes.gen import UIAutomationClient  # type: ignore[import]

        # Initialize UI Automation root object
        automation = comtypes.client.CreateObject(
            UIAutomationClient.CUIAutomation
        )

        windows: List[WindowText] = []

        def enum_window_callback(hwnd, _):
            # Only consider visible, non‑minimized windows with a title
            if not win32gui.IsWindowVisible(hwnd):
                return
            if win32gui.IsIconic(hwnd):
                return

            title = win32gui.GetWindowText(hwnd) or ""
            if not title.strip():
                return

            try:
                element = automation.ElementFromHandle(hwnd)

                # Try to get the Name property and the Value (if any)
                name = element.CurrentName or ""

                # Build up text by traversing children that support text/value
                texts: List[str] = []

                def traverse(el):
                    try:
                        # Name property often contains user‑visible text
                        if el.CurrentName:
                            texts.append(el.CurrentName)
                    except Exception:
                        # Ignore elements that don't expose Name
                        pass

                    try:
                        # Enumerate children
                        children = el.FindAll(
                            UIAutomationClient.TreeScope_Children,
                            automation.CreateTrueCondition(),
                        )
                        for i in range(children.Length):
                            traverse(children.GetElement(i))
                    except Exception:
                        # If child enumeration fails, skip silently
                        return

                traverse(element)

                combined_text_lines = []
                seen = set()
                for t in texts:
                    t_norm = t.strip()
                    if t_norm and t_norm not in seen:
                        seen.add(t_norm)
                        combined_text_lines.append(t_norm)

                window_text = "\n".join(combined_text_lines)

                # Combine title + extracted text
                full_text_parts = []
                if title.strip():
                    full_text_parts.append(f"[Window: {title.strip()}]")
                if window_text.strip():
                    full_text_parts.append(window_text.strip())

                if full_text_parts:
                    windows.append(
                        WindowText(title=title.strip(), text="\n".join(full_text_parts))
                    )

            except Exception as exc:  # pragma: no cover - defensive
                logger.debug(f"UIA extraction failed for window '{title}': {exc}")
                return

        # Enumerate all top‑level windows
        win32gui.EnumWindows(enum_window_callback, None)

        if not windows:
            logger.warning(
                "Screen text extraction via UI Automation returned no windows"
            )

        # Build combined raw text (for AI input)
        raw_text_lines: List[str] = []
        for w in windows:
            if w.text.strip():
                raw_text_lines.append(w.text.strip())

        raw_text = "\n\n".join(raw_text_lines)

        result = ScreenTextExtractionResult(
            method="uia",
            windows=windows,
            raw_text=raw_text,
            error=None if windows else "No windows or text extracted via UI Automation",
        )

        logger.info(
            "Screen text extraction completed via UI Automation: "
            f"windows={len(result.windows)}, chars={len(result.raw_text)}"
        )
        return result

    except ImportError as exc:
        # UI Automation dependencies missing – return safe 'unavailable' result
        msg = (
            "Windows UI Automation packages not available "
            "(pywin32/comtypes). Screen text extraction is disabled."
        )
        logger.warning(f"{msg} Details: {exc}")
        return ScreenTextExtractionResult(
            method="unavailable",
            windows=[],
            raw_text="",
            error=msg,
        )
    except Exception as exc:  # pragma: no cover - defensive catch‑all
        # Any unexpected failure – log and return safe result
        logger.error(f"Screen text extraction failed: {exc}", exc_info=True)
        return ScreenTextExtractionResult(
            method="unavailable",
            windows=[],
            raw_text="",
            error=f"Screen text extraction failed: {exc}",
        )


