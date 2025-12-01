"""
API routes for the Phishing Detector application
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    StatusResponse,
    PhishingStatus,
    RiskLevel,
    RecommendedAction,
    ScreenScanRequest,
)
from app.core.config import settings
from app.core.logger import logger
from app.services.text_processing import process_text_for_analysis
from app.services.ai_analyzer import analyze_with_llm
from app.services.text_extractor import extract_screen_text, ScreenTextExtractionResult

router = APIRouter(prefix=settings.API_PREFIX, tags=["phishing-detector"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify the API is running
    
    Returns:
        HealthResponse with service status
    """
    logger.debug("Health check requested")
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@router.get("/status", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def get_status():
    """
    Get detailed backend status including service availability
    
    Returns:
        StatusResponse with backend and service status
    """
    logger.debug("Status check requested")
    
    # Check service availability (will be implemented in later phases)
    services_status = {
        "screenshot": "ready",  # Will be implemented in Phase 2
        "ocr": "ready",  # Will be implemented in Phase 3
        "ai_analyzer": "ready" if settings.OPENAI_API_KEY else "not_configured"  # Will be implemented in Phase 4
    }
    
    # Determine overall status
    overall_status = "operational" if all(
        status == "ready" for status in services_status.values()
    ) else "degraded"
    
    return StatusResponse(
        status=overall_status,
        version=settings.API_VERSION,
        services=services_status,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


def _run_analysis(processed_text, include_urls: bool) -> AnalyzeResponse:
    """
    Internal helper that runs AI + fallback logic on processed text.
    """

    def rule_based_fallback() -> AnalyzeResponse:
        text_lower = processed_text.cleaned.lower()
        
        # Phishing indicators - more comprehensive list
        phishing_keywords = [
            "click here", "click now", "verify now", "verify immediately",
            "urgent", "urgently", "immediate action", "act now",
            "blocked", "deactivated", "suspended", "expired", "locked",
            "verify your account", "verify your identity", "verify payment",
            "update your account", "update payment", "update information",
            "your account will be", "account will be closed", "lose access",
            "last chance", "expires in", "offer expires",
            "congratulations", "you've won", "claim your prize",
            "security alert", "suspicious activity", "unauthorized access",
        ]
        
        # Suspicious URL patterns (exclude localhost and common dev domains)
        safe_domains = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
        suspicious_url_patterns = [
            ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq",  # Suspicious TLDs
            "verify-", "secure-", "update-", "login-", "account-",  # Suspicious subdomains
        ]
        
        # Check for phishing keywords
        keyword_matches = [kw for kw in phishing_keywords if kw in text_lower]
        
        # Check for suspicious URLs (exclude localhost/dev URLs)
        suspicious_urls = []
        for url in processed_text.urls:
            url_lower = url.lower()
            # Skip localhost and dev URLs
            if any(safe in url_lower for safe in safe_domains):
                continue
            # Check for HTTP (not HTTPS) - but only if it's not localhost
            if url_lower.startswith("http://") and not any(safe in url_lower for safe in safe_domains):
                suspicious_urls.append(url)
            # Check for suspicious patterns
            elif any(pattern in url_lower for pattern in suspicious_url_patterns):
                suspicious_urls.append(url)
        
        # Determine if phishing
        is_phish = len(keyword_matches) > 0 or len(suspicious_urls) > 0
        
        if is_phish:
            # Higher risk if both keywords and suspicious URLs
            if len(keyword_matches) >= 2 and len(suspicious_urls) > 0:
                risk_level_val = RiskLevel.CRITICAL
            elif len(suspicious_urls) > 0:
                risk_level_val = RiskLevel.HIGH
            elif len(keyword_matches) >= 2:
                risk_level_val = RiskLevel.HIGH
            else:
                risk_level_val = RiskLevel.MEDIUM
            
            status_val = PhishingStatus.PHISHING
            recommended_action_val = RecommendedAction.BLOCK if risk_level_val in [RiskLevel.HIGH, RiskLevel.CRITICAL] else RecommendedAction.IGNORE
            
            reasons = []
            if keyword_matches:
                reasons.append(f"Suspicious keywords detected: {', '.join(keyword_matches[:3])}")
            if suspicious_urls:
                reasons.append(f"Suspicious URLs found: {len(suspicious_urls)}")
            reason_val = ". ".join(reasons) if reasons else "Phishing indicators detected."
            confidence_val = 0.85
        else:
            status_val = PhishingStatus.SAFE
            risk_level_val = RiskLevel.LOW
            recommended_action_val = RecommendedAction.VERIFY
            reason_val = (
                "No obvious phishing indicators detected. However, "
                "always verify suspicious messages independently."
            )
            confidence_val = 0.6

        # Filter out localhost URLs from extracted URLs
        filtered_urls = []
        if include_urls and processed_text.urls:
            safe_domains = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
            filtered_urls = [
                url for url in processed_text.urls 
                if not any(safe in url.lower() for safe in safe_domains)
            ]
        
        return AnalyzeResponse(
            is_phishing=is_phish,
            status=status_val,
            risk_level=risk_level_val,
            confidence=confidence_val,
            reason=reason_val,
            suspicious_elements=[],
            recommended_action=recommended_action_val,
            extracted_text=processed_text.cleaned or processed_text.original,
            extracted_urls=filtered_urls,
        )

    # PRIMARY: Use OpenAI LLM if configured (this is the main decision maker)
    if settings.OPENAI_API_KEY:
        logger.info("Using OpenAI API for phishing detection (primary method)")
        try:
            ai_response = analyze_with_llm(processed_text)
            logger.info(
                "✅ OpenAI analysis completed: "
                f"is_phishing={ai_response.is_phishing}, "
                f"risk_level={ai_response.risk_level}, "
                f"status={ai_response.status}, "
                f"reason={ai_response.reason[:100] if ai_response.reason else 'N/A'}"
            )
            if not include_urls:
                ai_response.extracted_urls = []
            return ai_response
        except Exception as ai_exc:  # pragma: no cover - network/API issues
            logger.error(
                f"❌ OpenAI API failed, falling back to rule-based detection: {ai_exc}"
            )
            logger.warning("Using rule-based fallback (less accurate than OpenAI)")
            return rule_based_fallback()
    else:
        logger.warning("⚠️ OPENAI_API_KEY not configured; using rule-based analysis (less accurate)")
        return rule_based_fallback()


@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_200_OK)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze provided text for phishing content.
    """
    logger.info(f"Analysis requested for text length: {len(request.text)}")
    processed = process_text_for_analysis(request.text)
    try:
        return _run_analysis(processed, include_urls=request.include_urls)
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed due to an internal error.",
        )


@router.post("/scan-screen", response_model=AnalyzeResponse, status_code=status.HTTP_200_OK)
async def scan_screen(request: ScreenScanRequest):
    """
    Capture all visible screen text and analyze it for phishing content.
    """
    logger.info("Screen scan requested")
    extraction: ScreenTextExtractionResult = extract_screen_text()

    # Log extracted text for debugging
    logger.info(f"📄 Extracted text length: {len(extraction.raw_text)} characters")
    logger.info(f"📄 Extraction method: {extraction.method}, windows: {len(extraction.windows)}")
    if extraction.raw_text:
        preview = extraction.raw_text[:1000]  # Show first 1000 chars
        logger.info(f"📄 Extracted text preview:\n{preview}")
        if len(extraction.raw_text) > 1000:
            logger.info(f"📄 ... (truncated, total {len(extraction.raw_text)} chars)")
    else:
        logger.warning("⚠️ No text extracted from screen!")

    if not extraction.raw_text.strip():
        logger.error("Screen text extraction returned no text")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=extraction.error or "Unable to extract screen text.",
        )

    processed = process_text_for_analysis(extraction.raw_text)
    logger.info(f"Processed text length: {len(processed.cleaned)}, URLs found: {len(processed.urls)}")
    if processed.urls:
        logger.info(f"URLs extracted: {processed.urls}")

    try:
        response = _run_analysis(processed, include_urls=request.include_urls)
        # Ensure extracted text reflects full screen capture
        response.extracted_text = extraction.raw_text
        
        # Filter out localhost URLs from the response
        if response.extracted_urls:
            safe_domains = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
            response.extracted_urls = [
                url for url in response.extracted_urls 
                if not any(safe in url.lower() for safe in safe_domains)
            ]
        
        if not request.include_urls:
            response.extracted_urls = []
        logger.info(
            "Screen scan completed: "
            f"method={extraction.method}, "
            f"is_phishing={response.is_phishing}, "
            f"risk_level={response.risk_level}, "
            f"status={response.status}"
        )
        return response
    except Exception as e:
        logger.error(f"Screen scan analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Screen scan failed due to an internal error.",
        )

