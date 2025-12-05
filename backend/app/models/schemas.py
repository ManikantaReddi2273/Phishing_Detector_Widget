"""
Pydantic models for API request and response schemas
"""
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PhishingStatus(str, Enum):
    """Phishing detection status"""
    SAFE = "safe"
    PHISHING = "phishing"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"


class RecommendedAction(str, Enum):
    """Recommended user actions"""
    IGNORE = "ignore"
    VERIFY = "verify"
    REPORT = "report"
    DELETE = "delete"
    BLOCK = "block"


class AnalyzeRequest(BaseModel):
    """Request model for phishing analysis"""
    text: str = Field(..., description="Text content to analyze for phishing", min_length=1)
    include_urls: bool = Field(True, description="Whether to extract and analyze URLs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Your bank account will be blocked. Click here: http://fakebank-security.com",
                "include_urls": True
            }
        }


class ScreenScanRequest(BaseModel):
    """Request model for full screen scan"""
    include_urls: bool = Field(True, description="Whether to include URLs found in extracted screen text")


class SuspiciousElement(BaseModel):
    """Model for suspicious elements found in text"""
    type: str = Field(..., description="Type of suspicious element (url, urgency, threat, etc.)")
    value: str = Field(..., description="The actual suspicious content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")


class AnalyzeResponse(BaseModel):
    """Response model for phishing analysis"""
    is_phishing: bool = Field(..., description="Whether the text is identified as phishing")
    status: PhishingStatus = Field(..., description="Phishing detection status")
    risk_level: RiskLevel = Field(..., description="Risk level assessment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reason: str = Field(..., description="Detailed explanation of the detection result")
    suspicious_elements: List[SuspiciousElement] = Field(default_factory=list, description="List of suspicious elements found")
    recommended_action: RecommendedAction = Field(..., description="Recommended action for the user")
    extracted_text: Optional[str] = Field(None, description="Text that was analyzed (from Windows UI Automation)")
    extracted_urls: List[str] = Field(default_factory=list, description="URLs found in the text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_phishing": True,
                "status": "phishing",
                "risk_level": "high",
                "confidence": 0.95,
                "reason": "Suspicious URL detected with urgency tactics. The domain 'fakebank-security.com' is not associated with any legitimate bank.",
                "suspicious_elements": [
                    {
                        "type": "url",
                        "value": "http://fakebank-security.com",
                        "confidence": 0.98
                    },
                    {
                        "type": "urgency",
                        "value": "will be blocked",
                        "confidence": 0.85
                    }
                ],
                "recommended_action": "ignore",
                "extracted_text": "Your bank account will be blocked. Click here: http://fakebank-security.com",
                "extracted_urls": ["http://fakebank-security.com"]
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class StatusResponse(BaseModel):
    """Response model for backend status"""
    status: str = Field(..., description="Backend status")
    version: str = Field(..., description="API version")
    services: dict = Field(..., description="Status of various services")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "operational",
                "version": "0.1.0",
                "services": {
                    "screen_text_extractor": "ready",
                    "ai_analyzer": "ready",
                    "continuous_scanner": "running"
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class LatestScanResponse(BaseModel):
    """Response model for the latest continuous scan result."""

    last_scan_at: Optional[str] = Field(
        None, description="Timestamp of the last scan in ISO-8601 format"
    )
    has_result: bool = Field(
        ..., description="Whether a scan result is currently available"
    )
    error: Optional[str] = Field(
        None, description="Last error encountered during scanning, if any"
    )
    result: Optional[AnalyzeResponse] = Field(
        None, description="Latest phishing analysis result, if available"
    )

