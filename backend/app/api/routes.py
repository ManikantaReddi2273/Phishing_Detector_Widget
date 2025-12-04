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
    LatestScanResponse,
)
from app.core.config import settings
from app.core.logger import logger
from app.services.text_processing import process_text_for_analysis
from app.services.ai_analyzer import analyze_with_llm
from app.services.text_extractor import extract_screen_text, ScreenTextExtractionResult
from app.services.scanner import get_latest_scan_state

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
    
    services_status = {
        "screen_text_extractor": "ready",
        "ai_analyzer": "ready" if settings.OPENAI_API_KEY else "not_configured",
        "continuous_scanner": "running",
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


@router.get(
    "/latest-scan",
    response_model=LatestScanResponse,
    status_code=status.HTTP_200_OK,
)
async def latest_scan():
    """
    Get the most recent result from the continuous background scanner.

    This endpoint is intended for the floating Flutter desktop client to
    poll periodically (e.g. every few seconds) and show an alert when
    phishing content is detected, without requiring any user click.
    """
    state = get_latest_scan_state()
    return LatestScanResponse(
        last_scan_at=state["last_scan_at"],
        has_result=state["has_result"],
        error=state["error"],
        result=state["result"],
    )


def _run_analysis(processed_text, include_urls: bool) -> AnalyzeResponse:
    """
    Internal helper that runs OpenAI API analysis on processed text.
    OpenAI API is the ONLY detection method - no fallbacks.
    """
    # Check if OpenAI API key is configured
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is not configured. Please set OPENAI_API_KEY in your environment variables.",
        )

    # Use OpenAI LLM as the ONLY detection method
    logger.info("Using OpenAI API for phishing detection (ONLY method)")
    try:
        ai_response = analyze_with_llm(processed_text)
        logger.info(
            "[AI] OpenAI analysis completed: "
            f"is_phishing={ai_response.is_phishing}, "
            f"risk_level={ai_response.risk_level}, "
            f"status={ai_response.status}, "
            f"reason={ai_response.reason[:100] if ai_response.reason else 'N/A'}"
        )
        if not include_urls:
            ai_response.extracted_urls = []
        return ai_response
    except Exception as ai_exc:
        error_msg = str(ai_exc)
        logger.error(f"[ERROR] OpenAI API failed: {ai_exc}", exc_info=True)
        
        # Provide user-friendly error messages
        if "429" in error_msg or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
            detail = "OpenAI API quota exceeded. Please check your OpenAI account billing and quota limits."
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            detail = "OpenAI API key is invalid or expired. Please check your OPENAI_API_KEY in .env file."
        else:
            detail = f"OpenAI API analysis failed: {error_msg}. Please check your API key and network connection."
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )


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
    logger.info(f"[TEXT] Extracted text length: {len(extraction.raw_text)} characters")
    logger.info(f"[TEXT] Extraction method: {extraction.method}, windows: {len(extraction.windows)}")
    if extraction.raw_text:
        preview = extraction.raw_text[:1000]  # Show first 1000 chars
        # Sanitize preview to avoid Unicode encoding errors
        from app.core.logger import sanitize_text_for_logging
        safe_preview = sanitize_text_for_logging(preview)
        logger.info(f"[TEXT] Extracted text preview:\n{safe_preview}")
        if len(extraction.raw_text) > 1000:
            logger.info(f"[TEXT] ... (truncated, total {len(extraction.raw_text)} chars)")
    else:
        logger.warning("[WARN] No text extracted from screen!")

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
    
    # Log a sample of the cleaned text to verify quality
    if processed.cleaned:
        sample_text = processed.cleaned[:500] if len(processed.cleaned) > 500 else processed.cleaned
        # Sanitize sample to avoid Unicode encoding errors
        from app.core.logger import sanitize_text_for_logging
        safe_sample = sanitize_text_for_logging(sample_text)
        logger.info(f"[TEXT] Cleaned text sample (first 500 chars):\n{safe_sample}")
        if len(processed.cleaned) > 500:
            logger.info(f"[TEXT] ... (truncated, total {len(processed.cleaned)} chars)")

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

