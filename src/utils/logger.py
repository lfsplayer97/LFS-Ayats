"""
Logger utility module.

Provides factory functions for consistent logger configuration
across all modules in the LFS-Ayats system.
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


def get_logger(
    name: Optional[str] = None,
    level: int = logging.DEBUG,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Get or create a logger with standard configuration.

    This function ensures consistent logging setup across
    all modules in the LFS-Ayats system.

    Args:
        name: Logger name. If None, uses calling module name.
        level: Logging level (default: DEBUG)
        log_file: Optional file path for file logging

    Returns:
        Configured logger instance

    Example:
        >>> from src.utils import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("System initialized")
    """
    if name is None:
        import inspect

        name = inspect.currentframe().f_back.f_globals["__name__"]

    logger = logging.getLogger(name)

    # Configure only if not already configured
    if not logger.handlers:
        # Console handler with colors if available
        handler = logging.StreamHandler(sys.stdout)

        if COLORLOG_AVAILABLE:
            # Colored format for colorlog
            color_format = (
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            formatter = colorlog.ColoredFormatter(
                color_format,
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        else:
            # Fallback to standard formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

        # Add file handler if log_file is specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

    return logger


def configure_root_logger(level: int = logging.INFO) -> None:
    """
    Configure the root logger for the entire application.

    Args:
        level: Default logging level
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,  # Force reconfiguration
    )


def setup_logger(
    name: str = "lfs_ayats",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    log_format: Optional[str] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Configure the logging system with colorlog (legacy function).

    DEPRECATED: Use get_logger() instead for new code.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file (None to not use file)
        console: Show logs on console
        log_format: Log format
        use_colors: Use colors on console (requires colorlog)

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
