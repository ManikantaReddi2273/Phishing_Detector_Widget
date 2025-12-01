"""
Tests for API endpoints
"""
import pytest
from fastapi import status


def test_screen_scan_endpoint(monkeypatch, client):
    """Test screen scan endpoint with mocked extraction"""
    from app.api import routes
    from app.services.text_extractor import ScreenTextExtractionResult

    def mock_extract():
        return ScreenTextExtractionResult(
            method="uia",
            windows=[],
            raw_text="Test screen text",
            error=None,
        )

    monkeypatch.setattr(routes, "extract_screen_text", mock_extract)

    response = client.post("/api/scan-screen", json={"include_urls": True})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "is_phishing" in data
    assert data["extracted_text"] == "Test screen text"


def test_screen_scan_endpoint_no_text(monkeypatch, client):
    """Screen scan should return 503 if no text extracted"""
    from app.api import routes
    from app.services.text_extractor import ScreenTextExtractionResult

    def mock_extract():
        return ScreenTextExtractionResult(
            method="uia",
            windows=[],
            raw_text="",
            error="No text found",
        )

    monkeypatch.setattr(routes, "extract_screen_text", mock_extract)

    response = client.post("/api/scan-screen", json={"include_urls": True})
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE



def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_status_endpoint(client):
    """Test status endpoint"""
    response = client.get("/api/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "services" in data
    assert "timestamp" in data
    assert isinstance(data["services"], dict)


def test_analyze_endpoint_phishing(client, analyze_request_phishing):
    """Test analyze endpoint with phishing text"""
    response = client.post("/api/analyze", json=analyze_request_phishing)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Validate response structure
    assert "is_phishing" in data
    assert "status" in data
    assert "risk_level" in data
    assert "confidence" in data
    assert "reason" in data
    assert "recommended_action" in data
    assert "extracted_text" in data
    assert "extracted_urls" in data
    
    # Validate data types
    assert isinstance(data["is_phishing"], bool)
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["extracted_urls"], list)


def test_analyze_endpoint_safe(client, analyze_request_safe):
    """Test analyze endpoint with safe text"""
    response = client.post("/api/analyze", json=analyze_request_safe)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "is_phishing" in data
    assert "status" in data
    assert "risk_level" in data
    assert "confidence" in data


def test_analyze_endpoint_empty_text(client):
    """Test analyze endpoint with empty text (should fail validation)"""
    response = client.post("/api/analyze", json={"text": "", "include_urls": True})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_analyze_endpoint_missing_text(client):
    """Test analyze endpoint without text field (should fail validation)"""
    response = client.post("/api/analyze", json={"include_urls": True})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data

