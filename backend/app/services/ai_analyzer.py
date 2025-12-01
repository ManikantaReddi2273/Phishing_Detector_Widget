"""
AI phishing detection service (Phase 4)

This module integrates with an LLM (OpenAI by default) to analyze text
for phishing risk and return a structured result that maps cleanly onto
our AnalyzeResponse schema.

Design goals:
- Respect environment configuration (no hard-coded API keys)
- Never crash the backend on API errors (fail soft, with clear reason)
- Maintain compatibility with the existing AnalyzeResponse model
"""

from __future__ import annotations

import json
from typing import Any, Dict

from app.core.config import settings
from app.core.logger import logger
from app.models.schemas import (
    AnalyzeResponse,
    PhishingStatus,
    RiskLevel,
    RecommendedAction,
    SuspiciousElement,
)
from app.services.text_processing import ProcessedText


def _build_system_prompt() -> str:
    """System prompt describing the task and expected JSON schema."""
    return (
        "You are an expert security analyst specializing in phishing detection. "
        "Analyze the provided text for phishing indicators and respond ONLY with "
        "a strict JSON object matching this exact schema:\n\n"
        "{\n"
        '  "is_phishing": true or false,\n'
        '  "risk_level": "low" | "medium" | "high" | "critical",\n'
        '  "reason": "concise explanation of your assessment",\n'
        '  "suspicious_elements": [\n'
        '    {"type": "url" | "urgency" | "threat" | "credential_request" | "other",\n'
        '     "value": "specific suspicious element found",\n'
        '     "confidence": number between 0 and 1}\n'
        "  ],\n"
        '  "recommended_action": "ignore" | "verify" | "report" | "delete" | "block"\n'
        "}\n\n"
        "Detection Guidelines:\n"
        "- Phishing indicators: urgent language, threats, suspicious URLs, requests for credentials, "
        "prize scams, account suspension warnings, unusual domains, typosquatting\n"
        "- Safe indicators: normal communication, legitimate domains, no urgency, no credential requests\n"
        "- IMPORTANT: Ignore localhost (127.0.0.1, localhost) and development URLs - these are NOT phishing\n"
        "- Be accurate: Only mark as phishing if there are clear indicators\n"
        "- Risk levels: critical (obvious scam), high (strong indicators), medium (some concerns), low (minimal risk)\n\n"
        "Response Rules:\n"
        "- Do NOT include any extra keys beyond those specified.\n"
        "- Do NOT include comments or explanations outside the JSON.\n"
        "- Keep JSON valid and parseable.\n"
        "- Be precise and conservative in your assessment.\n"
    )


def _build_user_prompt(processed: ProcessedText) -> str:
    """Construct the user prompt given processed text."""
    parts = [
        "You are analyzing text content for phishing indicators. Consider:",
        "- Urgent language and threats",
        "- Suspicious URLs (especially HTTP, unusual domains, typosquatting)",
        "- Requests for personal information or credentials",
        "- Unusual sender addresses or domains",
        "- Prize/winning scams",
        "- Account suspension threats",
        "",
        "IMPORTANT: Ignore localhost URLs (127.0.0.1, localhost) and development URLs as they are not phishing.",
        "",
        "TEXT TO ANALYZE:",
        processed.cleaned or processed.original or "",
    ]
    if processed.urls:
        parts.append("")
        parts.append("URLs detected in the text:")
        for url in processed.urls:
            # Filter out localhost URLs from the list shown to AI
            if not any(safe in url.lower() for safe in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]):
                parts.append(f"- {url}")
    if processed.emails:
        parts.append("")
        parts.append("Email addresses detected:")
        for email in processed.emails:
            parts.append(f"- {email}")
    return "\n".join(parts).strip()


def analyze_with_llm(processed: ProcessedText) -> AnalyzeResponse:
    """
    Analyze processed text with an LLM and map the result into AnalyzeResponse.

    Raises:
        RuntimeError if OpenAI is not configured or another hard failure occurs.
        The caller is expected to catch and fall back to a rule-based method.
    """
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    try:
        # Lazy import so the module can be imported without openai installed.
        from openai import OpenAI  # type: ignore[import]
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"OpenAI SDK not available: {exc}") from exc

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(processed)

    text_length = len(processed.cleaned or processed.original)
    logger.info(
        f"🤖 Calling OpenAI API for phishing analysis "
        f"(model={settings.OPENAI_MODEL}, text_len={text_length}, "
        f"urls={len(processed.urls)}, emails={len(processed.emails)})"
    )

    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = completion.choices[0].message.content or "{}"
        logger.debug(f"OpenAI raw response: {content[:500]}")  # Log first 500 chars
        data: Dict[str, Any] = json.loads(content)

        # Map JSON fields to AnalyzeResponse
        is_phishing = bool(data.get("is_phishing", False))
        risk_level_str = str(data.get("risk_level", "low")).lower()
        reason = str(data.get("reason", "")).strip() or "No reason provided by model."
        recommended_action_str = str(data.get("recommended_action", "verify")).lower()
        
        logger.info(
            f"✅ OpenAI decision: is_phishing={is_phishing}, "
            f"risk_level={risk_level_str}, reason={reason[:100]}"
        )

        # Clamp risk level to known enum values
        if risk_level_str not in {"low", "medium", "high", "critical"}:
            risk_level_str = "low"

        # Clamp recommended action
        if recommended_action_str not in {"ignore", "verify", "report", "delete", "block"}:
            recommended_action_str = "verify"

        # Suspicious elements
        suspicious_elements_data = data.get("suspicious_elements", []) or []
        suspicious_elements: list[SuspiciousElement] = []
        for elem in suspicious_elements_data:
            try:
                suspicious_elements.append(
                    SuspiciousElement(
                        type=str(elem.get("type", "other")),
                        value=str(elem.get("value", "")),
                        confidence=float(elem.get("confidence", 0.5)),
                    )
                )
            except Exception:
                # Skip malformed elements
                continue

        # Simple confidence heuristic: high if phishing, else medium
        confidence = 0.9 if is_phishing else 0.7

        # Filter out localhost URLs from extracted URLs
        safe_domains = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
        filtered_urls = [
            url for url in processed.urls 
            if not any(safe in url.lower() for safe in safe_domains)
        ]
        
        return AnalyzeResponse(
            is_phishing=is_phishing,
            status=PhishingStatus.PHISHING if is_phishing else PhishingStatus.SAFE,
            risk_level=RiskLevel(risk_level_str),
            confidence=confidence,
            reason=reason,
            suspicious_elements=suspicious_elements,
            recommended_action=RecommendedAction(recommended_action_str),
            extracted_text=processed.cleaned or processed.original,
            extracted_urls=filtered_urls,
        )

    except Exception as exc:  # pragma: no cover - network / API errors
        logger.error(f"OpenAI phishing analysis failed: {exc}", exc_info=True)
        raise RuntimeError(f"OpenAI analysis failed: {exc}") from exc


