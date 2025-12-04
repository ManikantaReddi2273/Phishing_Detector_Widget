"""
Main entry point for the Phishing Detector Backend API
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import logger
from app.api.routes import router
from app.services.scanner import start_background_scanner

# Initialize FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-powered phishing detection API for Windows desktop widget",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Server running on http://{settings.HOST}:{settings.PORT}")
    logger.info(f"API documentation available at http://{settings.HOST}:{settings.PORT}/docs")
    
    # Log configuration status
    if settings.OPENAI_API_KEY:
        logger.info("OpenAI API key configured")
    else:
        logger.warning("OpenAI API key not configured - AI analysis will not work")

    # Start continuous background screen scanning
    try:
        start_background_scanner()
        logger.info("Continuous background scanner started")
    except Exception as exc:
        logger.error(f"Failed to start background scanner: {exc}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down Phishing Detector API")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Phishing Detector API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

