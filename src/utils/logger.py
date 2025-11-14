"""
Logger
Logging system for LFS-Ayats with colorlog support.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    import colorlog

    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


def setup_logger(
    name: str = "lfs_ayats",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    log_format: Optional[str] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Configure the logging system with colorlog.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file (None to not use file)
        console: Show logs in console
        log_format: Log format
        use_colors: Use colors in console (requires colorlog)

    Returns:
        logging.Logger: Configured logger

    Example:
        >>> logger = setup_logger("lfs_ayats", "DEBUG", "app.log")
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid duplicates
    if logger.handlers:
        logger.handlers.clear()

    # Default format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s"

    # Console handler with colors
    if console:
        console_handler = logging.StreamHandler(sys.stdout)

        if use_colors and COLORLOG_AVAILABLE:
            # Format with colors for colorlog
            color_format = (
                "%(log_color)s%(levelname)-8s%(reset)s "
                "%(asctime)s - %(cyan)s%(name)s%(reset)s - %(message)s"
            )
            formatter = colorlog.ColoredFormatter(
                color_format,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                secondary_log_colors={},
                style="%",
            )
        else:
            formatter = logging.Formatter(log_format)

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler (without colors)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_formatter = logging.Formatter(log_format)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "lfs_ayats") -> logging.Logger:
    """
    Get an existing logger.

    Args:
        name: Logger name

    Returns:
        logging.Logger: Logger
    """
    return logging.getLogger(name)


def create_session_logger(base_name: str = "lfs_ayats") -> logging.Logger:
    """
    Create a logger for a session with timestamp.

    Args:
        base_name: Base logger name

    Returns:
        logging.Logger: Session logger
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/{base_name}_{timestamp}.log"

    return setup_logger(
        name=f"{base_name}_{timestamp}", level="DEBUG", log_file=log_file, console=True
    )
