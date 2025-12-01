"""
Configuration management for the application
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    API_TITLE: str = "Phishing Detector API"
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # Server Configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.3
    
    # OCR Configuration
    OCR_ENGINE: str = "easyocr"  # Options: "easyocr", "pytesseract"
    OCR_LANGUAGES: list[str] = ["en"]  # Language codes for OCR
    
    # Screenshot Configuration
    SCREENSHOT_FORMAT: str = "PNG"
    SCREENSHOT_QUALITY: int = 95
    
    # File Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    TEMP_DIR: Path = BASE_DIR / "temp"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.TEMP_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()

