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
        "You are a cybersecurity expert specializing in phishing detection. "
        "Your CRITICAL mission: Identify and flag ALL phishing attempts to protect users.\n\n"
        "Respond ONLY with valid JSON matching this exact schema:\n"
        "{\n"
        '  "is_phishing": true or false,\n'
        '  "risk_level": "low" | "medium" | "high" | "critical",\n'
        '  "reason": "detailed explanation",\n'
        '  "suspicious_elements": [{"type": "url|urgency|threat|credential_request|other", "value": "...", "confidence": 0.0-1.0}],\n'
        '  "recommended_action": "ignore" | "verify" | "report" | "delete" | "block"\n'
        "}\n\n"
        "PHISHING = TRUE if text contains ANY of these:\n"
        "✓ Urgent/threatening language (urgent, immediately, within 24 hours, act now, account suspended/blocked/closed, expired, locked)\n"
        "✓ Suspicious URLs (http:// not https://, unusual domains, verify-/secure-/update-/login- subdomains, typosquatting)\n"
        "✓ Credential requests (verify account/details, update information, complete verification, update KYC)\n"
        "✓ Prize/scam language (congratulations, you've won, claim prize)\n"
        "✓ Suspicious activity claims (unusual activity, unauthorized access)\n\n"
        "CRITICAL: Analyze the ACTUAL CONTENT, not disclaimers. If text says 'fake phishing example' but contains phishing patterns, STILL MARK AS PHISHING.\n"
        "The presence of phishing indicators makes it phishing, regardless of labels like 'fake', 'example', or 'test'.\n\n"
        "SAFE = FALSE only if: Normal communication, legitimate https:// domains, no urgency/threats/credential requests.\n\n"
        "IMPORTANT: Ignore localhost/127.0.0.1 URLs. When uncertain, flag as phishing to protect users.\n"
        "Risk: critical (obvious scam), high (threats+suspicious URLs), medium (some indicators), low (minimal but suspicious)."
    )


def _build_user_prompt(processed: ProcessedText) -> str:
    """Construct the user prompt given processed text."""
    # Put the actual text FIRST to give it maximum importance
    text_content = processed.cleaned or processed.original or ""
    
    # Truncate text if too long to speed up analysis
    max_length = settings.OPENAI_MAX_INPUT_LENGTH
    if len(text_content) > max_length:
        logger.warning(
            f"[AI] Input text too long ({len(text_content)} chars), truncating to {max_length} chars for faster analysis"
        )
        # Try to truncate at a word boundary near the limit
        truncated = text_content[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.9:  # If we find a space in the last 10%, use it
            text_content = truncated[:last_space] + "\n[... text truncated for performance ...]"
        else:
            text_content = truncated + "\n[... text truncated for performance ...]"
    
    # Build a concise, focused prompt
    parts = [
        "TEXT TO ANALYZE:",
        text_content,
    ]
    
    # Add URLs and emails as context after the main text
    if processed.urls:
        non_localhost_urls = [
            url for url in processed.urls 
            if not any(safe in url.lower() for safe in ["localhost", "127.0.0.1", "0.0.0.0", "::1"])
        ]
        if non_localhost_urls:
            parts.append("")
            parts.append("URLs found:")
            for url in non_localhost_urls:
                parts.append(f"  - {url}")
    
    if processed.emails:
        parts.append("")
        parts.append("Email addresses found:")
        for email in processed.emails:
            parts.append(f"  - {email}")
    
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

    # Initialize OpenAI client with timeout for faster failure detection
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=settings.OPENAI_TIMEOUT,
    )

    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(processed)

    text_length = len(processed.cleaned or processed.original)
    
    # Log what we're sending to OpenAI for debugging
    logger.info(
        f"[AI] Calling OpenAI API for phishing analysis "
        f"(model={settings.OPENAI_MODEL}, text_len={text_length}, "
        f"urls={len(processed.urls)}, emails={len(processed.emails)}, "
        f"temperature={settings.OPENAI_TEMPERATURE})"
    )
    
    # Log the actual text being analyzed (first 500 chars for debugging)
    logger.debug(f"[AI] Text being analyzed (first 500 chars):\n{user_prompt[:500]}")
    if len(user_prompt) > 500:
        logger.debug(f"[AI] ... (truncated, total {len(user_prompt)} chars)")
    
    # Log URLs if present
    if processed.urls:
        non_localhost_urls = [
            url for url in processed.urls 
            if not any(safe in url.lower() for safe in ["localhost", "127.0.0.1", "0.0.0.0", "::1"])
        ]
        if non_localhost_urls:
            logger.info(f"[AI] URLs being analyzed: {non_localhost_urls}")

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
        logger.info(f"[AI] OpenAI raw response (first 500 chars): {content[:500]}")
        if len(content) > 500:
            logger.debug(f"[AI] Full OpenAI response: {content}")
        
        try:
            data: Dict[str, Any] = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse OpenAI JSON response: {e}")
            logger.error(f"❌ Raw response was: {content}")
            raise RuntimeError(f"OpenAI returned invalid JSON: {e}") from e

        # Map JSON fields to AnalyzeResponse
        is_phishing = bool(data.get("is_phishing", False))
        risk_level_str = str(data.get("risk_level", "low")).lower()
        reason = str(data.get("reason", "")).strip() or "No reason provided by model."
        recommended_action_str = str(data.get("recommended_action", "verify")).lower()
        
        logger.info(
            f"[AI] OpenAI decision: is_phishing={is_phishing}, "
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


