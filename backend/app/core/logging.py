"""
GridShield AI - Logging Configuration
WHY: Structured logging for debugging, auditing, and monitoring.
HOW: Uses loguru for structured, colored, rotated log output.
"""

import sys
from loguru import logger
from .config import settings


def setup_logging():
    """Configure application logging."""
    logger.remove()

    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )

    # File output
    logger.add(
        f"{settings.LOGS_DIR}/gridshield_{{time:YYYY-MM-DD}}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
               "{name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )

    # Error file
    logger.add(
        f"{settings.LOGS_DIR}/errors_{{time:YYYY-MM-DD}}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
               "{name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="10 MB",
        retention="30 days"
    )

    logger.info(f"Logging initialized - Level: {settings.LOG_LEVEL}")
    return logger


app_logger = setup_logging()
