"""
Logging configuration for the application
"""
import logging
import sys
import re
from pathlib import Path
from logging.handlers import RotatingFileHandler
import colorlog
from app.core.config import settings


def sanitize_text_for_logging(text: str) -> str:
    """
    Remove or replace Unicode characters that can't be encoded in Windows console.
    This prevents UnicodeEncodeError when logging text with emojis or special characters.
    """
    if not text:
        return text
    
    # Replace common emojis and Unicode characters with ASCII equivalents
    # This is a simple approach - just remove non-ASCII characters that cause issues
    try:
        # Try to encode with cp1252 (Windows default) to see if it fails
        text.encode('cp1252', errors='strict')
        return text  # If it works, return as-is
    except UnicodeEncodeError:
        # If encoding fails, replace problematic characters
        # Keep ASCII and common printable characters, replace others
        sanitized = re.sub(r'[^\x00-\x7F]+', '[?]', text)
        return sanitized


def setup_logger(name: str = "phishing_detector") -> logging.Logger:
    """
    Set up and configure the application logger
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    # Set UTF-8 encoding for Windows console to handle Unicode characters
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass  # If reconfiguration fails, continue with default
    
    # Create a custom StreamHandler that handles encoding errors gracefully
    class SafeStreamHandler(logging.StreamHandler):
        def emit(self, record):
            try:
                super().emit(record)
            except UnicodeEncodeError:
                # If encoding fails, try to sanitize and retry
                try:
                    record.msg = sanitize_text_for_logging(str(record.msg))
                    record.args = tuple(sanitize_text_for_logging(str(arg)) if isinstance(arg, str) else arg 
                                       for arg in record.args)
                    super().emit(record)
                except Exception:
                    # Last resort: log a safe message
                    safe_record = logging.LogRecord(
                        record.name, record.levelno, record.pathname, record.lineno,
                        "Log message contains characters that cannot be encoded", (), None
                    )
                    super().emit(safe_record)
    
    console_handler = SafeStreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = settings.LOGS_DIR / f"{name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        settings.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


# Create main application logger
logger = setup_logger()

