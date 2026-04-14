"""Logging configuration for Silo audiobook metadata editor."""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(name: str = 'silo') -> logging.Logger:
    """Setup application logging.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_dir = Path.home() / '.silo' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers.clear()

    # File handler with rotation
    log_file = log_dir / f'silo_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
