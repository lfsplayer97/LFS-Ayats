"""
Tests for logger utility module.

Tests the centralized logger factory functions for consistent
logging configuration across all modules.
"""

import logging
import pytest
from pathlib import Path
import tempfile
import os

from src.utils import get_logger, configure_root_logger


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_with_name(self):
        """Test logger creation with explicit name."""
        logger = get_logger("test_module")
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_auto_name(self):
        """Test logger creation with automatic name detection."""
        logger = get_logger()
        assert logger.name == __name__

    def test_logger_has_handler(self):
        """Test logger has StreamHandler configured."""
        logger = get_logger("test_handler")
        assert len(logger.handlers) > 0
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_logger_level(self):
        """Test logger level configuration."""
        logger = get_logger("test_level", level=logging.WARNING)
        assert logger.level == logging.WARNING

    def test_logger_default_level(self):
        """Test logger uses DEBUG level by default."""
        logger = get_logger("test_default_level")
        assert logger.level == logging.DEBUG

    def test_logger_has_formatter(self):
        """Test logger handler has proper formatter."""
        logger = get_logger("test_formatter")
        handler = logger.handlers[0]
        assert handler.formatter is not None

    def test_logger_singleton_pattern(self):
        """Test that getting the same logger name returns the same instance."""
        logger1 = get_logger("singleton_test")
        logger2 = get_logger("singleton_test")
        assert logger1 is logger2

    def test_logger_no_duplicate_handlers(self):
        """Test that getting logger multiple times doesn't add duplicate handlers."""
        logger1 = get_logger("duplicate_test")
        handler_count = len(logger1.handlers)
        logger2 = get_logger("duplicate_test")
        assert len(logger2.handlers) == handler_count

    def test_logger_with_file(self):
        """Test logger creation with file logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = get_logger("test_file_logger", log_file=log_file)

            # Should have both console and file handlers
            assert len(logger.handlers) >= 1

            # Write a log message
            logger.info("Test message")

            # Verify file was created
            assert os.path.exists(log_file)

    def test_logger_file_creates_directory(self):
        """Test that logger creates parent directories for log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "subdir", "test.log")
            logger = get_logger("test_mkdir_logger", log_file=log_file)

            # Verify parent directory was created
            assert os.path.exists(os.path.dirname(log_file))

    def test_different_loggers_independent(self):
        """Test that different loggers are independent."""
        logger1 = get_logger("independent_1", level=logging.DEBUG)
        logger2 = get_logger("independent_2", level=logging.ERROR)

        assert logger1.level == logging.DEBUG
        assert logger2.level == logging.ERROR
        assert logger1 is not logger2


class TestConfigureRootLogger:
    """Test cases for configure_root_logger function."""

    def test_configure_root_logger_default(self):
        """Test root logger configuration with default level."""
        configure_root_logger()
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_configure_root_logger_custom_level(self):
        """Test root logger configuration with custom level."""
        configure_root_logger(level=logging.WARNING)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING

    def test_configure_root_logger_debug(self):
        """Test root logger configuration with DEBUG level."""
        configure_root_logger(level=logging.DEBUG)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG


class TestLoggerIntegration:
    """Integration tests for logger utility."""

    def test_logger_can_log_messages(self, caplog):
        """Test that logger can actually log messages."""
        logger = get_logger("test_logging")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")

        assert "Test info message" in caplog.text
        assert "Test warning message" in caplog.text
        assert "Test error message" in caplog.text

    def test_logger_respects_level(self, caplog):
        """Test that logger respects logging level."""
        logger = get_logger("test_level_respect", level=logging.WARNING)

        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")

        # Debug and info should not appear
        assert "Debug message" not in caplog.text
        assert "Info message" not in caplog.text
        # Warning should appear
        assert "Warning message" in caplog.text

    def test_multiple_modules_can_use_get_logger(self):
        """Test that multiple modules can use get_logger independently."""
        logger_a = get_logger("module.a", level=logging.DEBUG)
        logger_b = get_logger("module.b", level=logging.INFO)
        logger_c = get_logger("module.c", level=logging.WARNING)

        assert logger_a.name == "module.a"
        assert logger_b.name == "module.b"
        assert logger_c.name == "module.c"

        assert logger_a.level == logging.DEBUG
        assert logger_b.level == logging.INFO
        assert logger_c.level == logging.WARNING
