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
    Extract all visible text from the **currently active (foreground) window**.

    Primary strategy:
        - Use Windows UI Automation (via pywin32 + comtypes) to locate the
          foreground window and read its text content.

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

        # Get the currently active (foreground) window
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            logger.warning("No foreground window detected for screen text extraction")
        else:
            # Only consider visible, non‑minimized windows with a title
            if win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd):
                title = win32gui.GetWindowText(hwnd) or ""
                try:
                    element = automation.ElementFromHandle(hwnd)

                    texts: List[str] = []

                    def traverse(el, depth=0):
                        # Limit depth to avoid infinite recursion
                        if depth > 20:
                            return
                        
                        try:
                            # Get element name (labels, headings, etc.)
                            try:
                                name = el.CurrentName
                                if name and name.strip():
                                    texts.append(name.strip())
                            except Exception:
                                pass
                            
                            # Get element value (text content, input values, etc.)
                            try:
                                value = el.GetCurrentPropertyValue(
                                    UIAutomationClient.UIA_ValueValuePropertyId
                                )
                                if value and str(value).strip():
                                    texts.append(str(value).strip())
                            except Exception:
                                pass
                            
                            # Get HelpText property (often contains additional text)
                            try:
                                help_text = el.GetCurrentPropertyValue(
                                    UIAutomationClient.UIA_HelpTextPropertyId
                                )
                                if help_text and str(help_text).strip():
                                    texts.append(str(help_text).strip())
                            except Exception:
                                pass
                            
                            # Try to get text pattern for text elements (most important for browsers)
                            try:
                                text_pattern = el.GetCurrentPattern(
                                    UIAutomationClient.UIA_TextPatternId
                                )
                                if text_pattern:
                                    # Get document range
                                    try:
                                        doc_range = text_pattern.DocumentRange
                                        if doc_range:
                                            full_text = doc_range.GetText(-1)
                                            if full_text and full_text.strip():
                                                texts.append(full_text.strip())
                                    except Exception:
                                        pass
                                    
                                    # Also try visible ranges
                                    try:
                                        visible_ranges = text_pattern.GetVisibleRanges()
                                        if visible_ranges and visible_ranges.Length > 0:
                                            for i in range(visible_ranges.Length):
                                                try:
                                                    text = visible_ranges.GetElement(i).GetText(-1)
                                                    if text and text.strip():
                                                        texts.append(text.strip())
                                                except Exception:
                                                    pass
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            
                            # Get item status (sometimes contains text)
                            try:
                                item_status = el.GetCurrentPropertyValue(
                                    UIAutomationClient.UIA_ItemStatusPropertyId
                                )
                                if item_status and str(item_status).strip():
                                    texts.append(str(item_status).strip())
                            except Exception:
                                pass
                                
                        except Exception:
                            pass

                        # Use Descendants scope to get ALL elements, not just direct children
                        # This is crucial for browsers which have deep DOM structures
                        try:
                            descendants = el.FindAll(
                                UIAutomationClient.TreeScope_Descendants,
                                automation.CreateTrueCondition(),
                            )
                            if descendants and descendants.Length > 0:
                                for i in range(descendants.Length):
                                    try:
                                        child = descendants.GetElement(i)
                                        traverse(child, depth + 1)
                                    except Exception:
                                        continue
                        except Exception:
                            # Fallback to children if descendants fails
                            try:
                                children = el.FindAll(
                                    UIAutomationClient.TreeScope_Children,
                                    automation.CreateTrueCondition(),
                                )
                                if children and children.Length > 0:
                                    for i in range(children.Length):
                                        try:
                                            child = children.GetElement(i)
                                            traverse(child, depth + 1)
                                        except Exception:
                                            continue
                            except Exception:
                                return

                    traverse(element, depth=0)

                    combined_text_lines = []
                    seen = set()
                    for t in texts:
                        t_norm = t.strip()
                        # Only add non-empty text that we haven't seen
                        # Also filter out very short fragments that are likely UI noise
                        if t_norm and len(t_norm) > 1 and t_norm not in seen:
                            seen.add(t_norm)
                            combined_text_lines.append(t_norm)
                    
                    logger.debug(f"Extracted {len(combined_text_lines)} unique text fragments from window '{title}'")

                    window_text = "\n".join(combined_text_lines)

                    full_text_parts = []
                    if title.strip():
                        full_text_parts.append(f"[Window: {title.strip()}]")
                    if window_text.strip():
                        full_text_parts.append(window_text.strip())

                    if full_text_parts:
                        windows.append(
                            WindowText(
                                title=title.strip(),
                                text="\n".join(full_text_parts),
                            )
                        )
                except Exception as exc:  # pragma: no cover - defensive
                    logger.debug(f"UIA extraction failed for foreground window '{title}': {exc}")

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


