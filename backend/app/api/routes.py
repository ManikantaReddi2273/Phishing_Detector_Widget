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
        is_phish = any(
            keyword in text_lower
            for keyword in [
                "click here",
                "urgent",
                "blocked",
                "deactivated",
                "verify",
                "update",
                "suspended",
                "expired",
            ]
        )

        if is_phish:
            status_val = PhishingStatus.PHISHING
            risk_level_val = (
                RiskLevel.HIGH if processed_text.urls else RiskLevel.MEDIUM
            )
            recommended_action_val = RecommendedAction.IGNORE
            reason_val = (
                "Suspicious keywords and patterns detected. "
                "This appears to be a phishing attempt."
            )
            confidence_val = 0.8
        else:
            status_val = PhishingStatus.SAFE
            risk_level_val = RiskLevel.LOW
            recommended_action_val = RecommendedAction.VERIFY
            reason_val = (
                "No obvious phishing indicators detected. However, "
                "always verify suspicious messages independently."
            )
            confidence_val = 0.6

        return AnalyzeResponse(
            is_phishing=is_phish,
            status=status_val,
            risk_level=risk_level_val,
            confidence=confidence_val,
            reason=reason_val,
            suspicious_elements=[],
            recommended_action=recommended_action_val,
            extracted_text=processed_text.cleaned or processed_text.original,
            extracted_urls=processed_text.urls if include_urls else [],
        )

    # Use LLM if configured; otherwise fall back to rule-based analysis
    if settings.OPENAI_API_KEY:
        try:
            ai_response = analyze_with_llm(processed_text)
            logger.info(
                "AI analysis completed: "
                f"is_phishing={ai_response.is_phishing}, "
                f"risk_level={ai_response.risk_level}"
            )
            if not include_urls:
                ai_response.extracted_urls = []
            return ai_response
        except Exception as ai_exc:  # pragma: no cover - network/API issues
            logger.warning(
                f"AI analysis failed, falling back to rule-based detection: {ai_exc}"
            )
            return rule_based_fallback()
    else:
        logger.info("OPENAI_API_KEY not configured; using rule-based analysis")
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

    if not extraction.raw_text.strip():
        logger.error("Screen text extraction returned no text")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=extraction.error or "Unable to extract screen text.",
        )

    processed = process_text_for_analysis(extraction.raw_text)

    try:
        response = _run_analysis(processed, include_urls=request.include_urls)
        # Ensure extracted text reflects full screen capture
        response.extracted_text = extraction.raw_text
        if not request.include_urls:
            response.extracted_urls = []
        logger.info(
            "Screen scan completed: "
            f"method={extraction.method}, "
            f"is_phishing={response.is_phishing}"
        )
        return response
    except Exception as e:
        logger.error(f"Screen scan analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Screen scan failed due to an internal error.",
        )

