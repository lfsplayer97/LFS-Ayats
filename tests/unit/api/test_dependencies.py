"""
Unit tests for api.dependencies module.

Tests for dependency injection functions.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from src.api import dependencies


class TestInitDependencies:
    """Test cases for init_dependencies function."""

    def setup_method(self):
        """Reset global dependencies before each test."""
        dependencies._repository = None
        dependencies._settings = None
        dependencies._connection_active = False

    def teardown_method(self):
        """Clean up after each test."""
        dependencies._repository = None
        dependencies._settings = None
        dependencies._connection_active = False

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_init_with_default_parameters(self, mock_settings, mock_repo):
        """Test initialization with default parameters."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Initialize
        dependencies.init_dependencies()

        # Verify repository was created with default connection string
        mock_repo.assert_called_once_with("sqlite:///telemetry.db")
        mock_repo_instance.create_tables.assert_called_once()

        # Verify settings was created with no arguments (default)
        mock_settings.assert_called_once_with()

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_init_with_custom_db_string(self, mock_settings, mock_repo):
        """Test initialization with custom database connection string."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Initialize with custom connection string
        custom_db = "postgresql://user:pass@localhost/testdb"
        dependencies.init_dependencies(db_connection_string=custom_db)

        # Verify custom connection string was used
        mock_repo.assert_called_once_with(custom_db)
        mock_repo_instance.create_tables.assert_called_once()

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_init_with_config_path(self, mock_settings, mock_repo):
        """Test initialization with configuration file path."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.from_yaml = Mock(return_value=mock_settings_instance)

        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test: config")
            config_path = f.name

        try:
            # Initialize with config path
            dependencies.init_dependencies(config_path=config_path)

            # Verify Settings.from_yaml was called
            mock_settings.from_yaml.assert_called_once_with(config_path)
        finally:
            # Clean up temp file
            if os.path.exists(config_path):
                os.unlink(config_path)

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_init_sets_global_variables(self, mock_settings, mock_repo):
        """Test that initialization sets global variables."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Initialize
        dependencies.init_dependencies()

        # Verify globals are set
        assert dependencies._repository is not None
        assert dependencies._settings is not None


class TestGetRepository:
    """Test cases for get_repository function."""

    def setup_method(self):
        """Reset global dependencies before each test."""
        dependencies._repository = None
        dependencies._settings = None

    def teardown_method(self):
        """Clean up after each test."""
        dependencies._repository = None
        dependencies._settings = None

    def test_get_repository_when_not_initialized(self):
        """Test getting repository when not initialized raises error."""
        with pytest.raises(RuntimeError) as exc_info:
            dependencies.get_repository()
        assert "not initialized" in str(exc_info.value)
        assert "init_dependencies" in str(exc_info.value)

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_get_repository_after_init(self, mock_settings, mock_repo):
        """Test getting repository after initialization."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Initialize
        dependencies.init_dependencies()

        # Get repository
        repo = dependencies.get_repository()

        # Verify it returns the initialized repository
        assert repo == mock_repo_instance

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_get_repository_returns_same_instance(self, mock_settings, mock_repo):
        """Test that get_repository returns the same instance on multiple calls."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Initialize
        dependencies.init_dependencies()

        # Get repository multiple times
        repo1 = dependencies.get_repository()
        repo2 = dependencies.get_repository()

        # Verify they are the same instance
        assert repo1 is repo2


class TestGetSettings:
    """Test cases for get_settings function."""

    def setup_method(self):
        """Reset global dependencies before each test."""
        dependencies._repository = None
        dependencies._settings = None

    def teardown_method(self):
        """Clean up after each test."""
        dependencies._repository = None
        dependencies._settings = None

    def test_get_settings_when_not_initialized(self):
        """Test getting settings when not initialized raises error."""
        with pytest.raises(RuntimeError) as exc_info:
            dependencies.get_settings()
        assert "not initialized" in str(exc_info.value)
        assert "init_dependencies" in str(exc_info.value)

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_get_settings_after_init(self, mock_settings, mock_repo):
        """Test getting settings after initialization."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Initialize
        dependencies.init_dependencies()

        # Get settings
        settings = dependencies.get_settings()

        # Verify it returns the initialized settings
        assert settings == mock_settings_instance

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_get_settings_returns_same_instance(self, mock_settings, mock_repo):
        """Test that get_settings returns the same instance on multiple calls."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Initialize
        dependencies.init_dependencies()

        # Get settings multiple times
        settings1 = dependencies.get_settings()
        settings2 = dependencies.get_settings()

        # Verify they are the same instance
        assert settings1 is settings2


class TestConnectionStatus:
    """Test cases for connection status functions."""

    def setup_method(self):
        """Reset connection status before each test."""
        dependencies._connection_active = False

    def teardown_method(self):
        """Clean up after each test."""
        dependencies._connection_active = False

    def test_initial_connection_status(self):
        """Test initial connection status is False."""
        status = dependencies.get_connection_status()
        assert status is False

    def test_set_connection_status_true(self):
        """Test setting connection status to True."""
        dependencies.set_connection_status(True)
        status = dependencies.get_connection_status()
        assert status is True

    def test_set_connection_status_false(self):
        """Test setting connection status to False."""
        dependencies.set_connection_status(True)
        dependencies.set_connection_status(False)
        status = dependencies.get_connection_status()
        assert status is False

    def test_multiple_status_changes(self):
        """Test multiple connection status changes."""
        # Initially False
        assert dependencies.get_connection_status() is False

        # Set to True
        dependencies.set_connection_status(True)
        assert dependencies.get_connection_status() is True

        # Set back to False
        dependencies.set_connection_status(False)
        assert dependencies.get_connection_status() is False

        # Set to True again
        dependencies.set_connection_status(True)
        assert dependencies.get_connection_status() is True


class TestDependenciesIntegration:
    """Integration tests for dependencies module."""

    def setup_method(self):
        """Reset global dependencies before each test."""
        dependencies._repository = None
        dependencies._settings = None
        dependencies._connection_active = False

    def teardown_method(self):
        """Clean up after each test."""
        dependencies._repository = None
        dependencies._settings = None
        dependencies._connection_active = False

    @patch("src.api.dependencies.TelemetryRepository")
    @patch("src.api.dependencies.Settings")
    def test_full_initialization_workflow(self, mock_settings, mock_repo):
        """Test complete initialization and usage workflow."""
        # Setup mocks
        mock_repo_instance = Mock()
        mock_repo.return_value = mock_repo_instance
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance

        # Initialize dependencies
        dependencies.init_dependencies(db_connection_string="sqlite:///:memory:")

        # Get repository and settings
        repo = dependencies.get_repository()
        settings = dependencies.get_settings()

        # Verify they are not None
        assert repo is not None
        assert settings is not None

        # Set and verify connection status
        dependencies.set_connection_status(True)
        assert dependencies.get_connection_status() is True
