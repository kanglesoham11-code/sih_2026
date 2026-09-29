"""
ORCA Logging Configuration
Structured JSON logging with loguru
"""

import sys
from loguru import logger

from app.core.config import settings


def setup_logging():
    """Configure logging for ORCA"""
    
    # Remove default logger
    logger.remove()
    
    # Console logging (structured for production, pretty for development)
    if settings.is_development:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
        )
    else:
        # JSON logging for production
        logger.add(
            sys.stdout,
            format="{message}",
            level="INFO",
            serialize=True,  # JSON output
        )
    
    # File logging (best-effort — skipped on ephemeral filesystems like Render)
    try:
        logger.add(
            "logs/orca_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # Rotate at midnight
            retention="30 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
        )
        
        # Error file
        logger.add(
            "logs/orca_errors_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="90 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
        )
    except Exception:
        # File logging unavailable (e.g., read-only or ephemeral filesystem)
        pass
    
    logger.info("Logging configured successfully")


def get_logger(name: str):
    """Get a logger instance for a specific module"""
    return logger.bind(module=name)
