"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_phishing_text():
    """Sample phishing text for testing"""
    return "Your bank account will be blocked. Click here immediately: http://fakebank-security.com"


@pytest.fixture
def sample_safe_text():
    """Sample safe text for testing"""
    return "Hello, this is a normal message from a friend. How are you doing today?"


@pytest.fixture
def analyze_request_phishing(sample_phishing_text):
    """Sample analyze request with phishing text"""
    return {
        "text": sample_phishing_text,
        "include_urls": True
    }


@pytest.fixture
def analyze_request_safe(sample_safe_text):
    """Sample analyze request with safe text"""
    return {
        "text": sample_safe_text,
        "include_urls": True
    }

