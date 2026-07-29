"""Structured logging utilities."""

import logging
import sys

from app.config import settings


def setup_logging() -> None:
    """Configure application-wide structured logging."""
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
