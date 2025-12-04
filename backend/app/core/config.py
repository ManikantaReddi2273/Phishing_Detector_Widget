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
    OPENAI_MAX_TOKENS: int = 400  # Optimized for faster responses
    OPENAI_TEMPERATURE: float = 0.5  # Increased for better detection sensitivity
    OPENAI_TIMEOUT: int = 30  # Timeout in seconds for API calls
    OPENAI_MAX_INPUT_LENGTH: int = 4000  # Maximum characters to send to OpenAI (truncate if longer)
    
    # Continuous scanning configuration
    SCAN_INTERVAL_SECONDS: int = 5  # How often to rescan the active window
    
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

