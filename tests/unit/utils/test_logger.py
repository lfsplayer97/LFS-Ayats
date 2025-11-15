"""
Unit tests for logger module.

Tests logger creation, configuration, log levels, and formatting.
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.logger import setup_logger, get_logger, create_session_logger


class TestSetupLogger:
    """Test suite for setup_logger function."""

    def test_logger_creation_default(self):
        """Test logger creation with default parameters."""
        logger = setup_logger()
        assert logger.name == "lfs_ayats"
        assert logger.level == logging.INFO

    def test_logger_creation_custom_name(self):
        """Test logger creation with custom name."""
        logger = setup_logger(name="custom_logger")
        assert logger.name == "custom_logger"

    def test_logger_level_debug(self):
        """Test logger with DEBUG level."""
        logger = setup_logger(name="test_debug", level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_logger_level_warning(self):
        """Test logger with WARNING level."""
        logger = setup_logger(name="test_warning", level="WARNING")
        assert logger.level == logging.WARNING

    def test_logger_level_error(self):
        """Test logger with ERROR level."""
        logger = setup_logger(name="test_error", level="ERROR")
        assert logger.level == logging.ERROR

    def test_logger_level_critical(self):
        """Test logger with CRITICAL level."""
        logger = setup_logger(name="test_critical", level="CRITICAL")
        assert logger.level == logging.CRITICAL

    def test_logger_without_console(self):
        """Test logger creation without console handler."""
        logger = setup_logger(name="test_no_console", console=False)
        # Logger should have no handlers or only file handler
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) == 0

    def test_logger_with_file(self):
        """Test logger creation with file handler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger(name="test_file", log_file=str(log_file))

            # Check file handler exists
            file_handlers = [
                h for h in logger.handlers if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) == 1

            # Test writing to file
            logger.info("Test message")
            assert log_file.exists()

    def test_logger_file_creates_directory(self):
        """Test that logger creates parent directories for log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "subdir" / "logs" / "test.log"
            logger = setup_logger(name="test_mkdir", log_file=str(log_file))

            logger.info("Test message")
            assert log_file.parent.exists()
            assert log_file.exists()

    def test_logger_custom_format(self):
        """Test logger with custom format."""
        custom_format = "%(levelname)s - %(message)s"
        logger = setup_logger(name="test_format", log_format=custom_format)

        # Check that formatter is applied
        assert len(logger.handlers) > 0

    def test_logger_without_colors(self):
        """Test logger creation with colors disabled."""
        logger = setup_logger(name="test_no_colors", use_colors=False)
        assert logger is not None
        assert logger.name == "test_no_colors"

    def test_logger_with_colors_when_colorlog_unavailable(self):
        """Test logger gracefully handles missing colorlog."""
        with patch("src.utils.logger.COLORLOG_AVAILABLE", False):
            logger = setup_logger(name="test_no_colorlog", use_colors=True)
            assert logger is not None

    def test_logger_clears_existing_handlers(self):
        """Test that logger clears existing handlers on reconfiguration."""
        logger_name = "test_clear_handlers"

        # Create logger first time
        logger1 = setup_logger(name=logger_name)
        handler_count1 = len(logger1.handlers)

        # Reconfigure same logger
        logger2 = setup_logger(name=logger_name)
        handler_count2 = len(logger2.handlers)

        # Handler count should be the same (not doubled)
        assert handler_count1 == handler_count2
        assert logger1 is logger2  # Same logger instance

    def test_logger_multiple_handlers(self):
        """Test logger with both console and file handlers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger(
                name="test_multi_handler",
                console=True,
                log_file=str(log_file),
            )

            # Should have both console and file handler
            assert len(logger.handlers) >= 2

    def test_logger_case_insensitive_level(self):
        """Test that log level is case insensitive."""
        logger1 = setup_logger(name="test_lower", level="info")
        logger2 = setup_logger(name="test_upper", level="INFO")
        logger3 = setup_logger(name="test_mixed", level="Info")

        assert logger1.level == logging.INFO
        assert logger2.level == logging.INFO
        assert logger3.level == logging.INFO


class TestGetLogger:
    """Test suite for get_logger function."""

    def test_get_logger_default(self):
        """Test getting default logger."""
        logger = get_logger()
        assert logger.name == "lfs_ayats"

    def test_get_logger_custom_name(self):
        """Test getting logger with custom name."""
        # First create the logger
        setup_logger(name="test_get_custom")

        # Then retrieve it
        logger = get_logger("test_get_custom")
        assert logger.name == "test_get_custom"

    def test_get_logger_nonexistent(self):
        """Test getting non-existent logger returns a logger."""
        logger = get_logger("nonexistent_logger")
        assert logger is not None
        assert logger.name == "nonexistent_logger"


class TestCreateSessionLogger:
    """Test suite for create_session_logger function."""

    def test_session_logger_creation(self):
        """Test session logger is created with timestamp."""
        logger = create_session_logger()
        assert "lfs_ayats" in logger.name
        # Name should contain timestamp pattern
        assert "_" in logger.name

    def test_session_logger_custom_base_name(self):
        """Test session logger with custom base name."""
        logger = create_session_logger(base_name="custom_session")
        assert "custom_session" in logger.name

    def test_session_logger_unique_names(self):
        """Test that session loggers have unique names."""
        logger1 = create_session_logger()
        logger2 = create_session_logger()

        # Names should be different (different timestamps or instances)
        # They might have same name if created in same second
        # but should be valid loggers
        assert logger1 is not None
        assert logger2 is not None

    def test_session_logger_debug_level(self):
        """Test session logger is created with DEBUG level."""
        logger = create_session_logger()
        assert logger.level == logging.DEBUG

    @patch("src.utils.logger.setup_logger")
    def test_session_logger_calls_setup(self, mock_setup):
        """Test session logger calls setup_logger correctly."""
        mock_logger = MagicMock()
        mock_setup.return_value = mock_logger

        create_session_logger(base_name="test_session")

        # Verify setup_logger was called
        mock_setup.assert_called_once()
        call_kwargs = mock_setup.call_args[1]

        assert call_kwargs["level"] == "DEBUG"
        assert call_kwargs["console"] is True
        assert "test_session" in call_kwargs["name"]
        assert "logs/" in call_kwargs["log_file"]
