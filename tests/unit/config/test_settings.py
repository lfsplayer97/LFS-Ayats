"""
Unit tests for Settings Configuration
"""

import pytest
import yaml
import os
from src.config.settings import (
    Settings,
    ConnectionSettings,
    TelemetrySettings,
    ExportSettings,
    VisualizationSettings,
    LoggingSettings,
    DatabaseSettings,
    load_config,
    save_config,
    create_default_config,
    get_database_url,
)


class TestConnectionSettings:
    """Test ConnectionSettings dataclass"""

    def test_default_values(self):
        """Test default configuration values"""
        settings = ConnectionSettings()

        assert settings.host == "127.0.0.1"
        assert settings.port == 29999
        assert settings.admin_password == ""
        assert settings.app_name == "LFS-Ayats"
        assert settings.udp is False
        assert settings.timeout == 5.0

    def test_custom_values(self):
        """Test custom configuration values"""
        settings = ConnectionSettings(
            host="192.168.1.100",
            port=12345,
            admin_password="test123",
            app_name="CustomApp",
            udp=True,
            timeout=10.0,
        )

        assert settings.host == "192.168.1.100"
        assert settings.port == 12345
        assert settings.admin_password == "test123"
        assert settings.udp is True
        assert settings.timeout == 10.0


class TestTelemetrySettings:
    """Test TelemetrySettings dataclass"""

    def test_default_values(self):
        """Test default telemetry settings"""
        settings = TelemetrySettings()

        assert settings.interval == 100
        assert settings.max_history == 10000
        assert settings.auto_export is False
        assert settings.export_interval == 60

    def test_custom_values(self):
        """Test custom telemetry settings"""
        settings = TelemetrySettings(
            interval=50, max_history=5000, auto_export=True, export_interval=30
        )

        assert settings.interval == 50
        assert settings.max_history == 5000
        assert settings.auto_export is True


class TestExportSettings:
    """Test ExportSettings dataclass"""

    def test_default_values(self):
        """Test default export settings"""
        settings = ExportSettings()

        assert settings.format == "csv"
        assert settings.output_dir == "data"
        assert settings.filename_template == "telemetry_{timestamp}"
        assert settings.auto_compression is False

    def test_custom_values(self):
        """Test custom export settings"""
        settings = ExportSettings(
            format="json",
            output_dir="/tmp/exports",
            filename_template="race_{timestamp}",
            auto_compression=True,
        )

        assert settings.format == "json"
        assert settings.output_dir == "/tmp/exports"
        assert settings.auto_compression is True


class TestVisualizationSettings:
    """Test VisualizationSettings dataclass"""

    def test_default_values(self):
        """Test default visualization settings"""
        settings = VisualizationSettings()

        assert settings.refresh_rate == 10
        assert settings.show_realtime is True
        assert settings.plot_history == 100


class TestLoggingSettings:
    """Test LoggingSettings dataclass"""

    def test_default_values(self):
        """Test default logging settings"""
        settings = LoggingSettings()

        assert settings.level == "INFO"
        assert settings.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert settings.file is None
        assert settings.console is True

    def test_custom_values(self):
        """Test custom logging settings"""
        settings = LoggingSettings(level="DEBUG", file="app.log", console=False)

        assert settings.level == "DEBUG"
        assert settings.file == "app.log"
        assert settings.console is False


class TestSettings:
    """Test main Settings class"""

    def test_default_initialization(self):
        """Test Settings with default values"""
        settings = Settings()

        assert isinstance(settings.connection, ConnectionSettings)
        assert isinstance(settings.telemetry, TelemetrySettings)
        assert isinstance(settings.export, ExportSettings)
        assert isinstance(settings.visualization, VisualizationSettings)
        assert isinstance(settings.logging, LoggingSettings)

    def test_custom_initialization(self):
        """Test Settings with custom sub-settings"""
        conn = ConnectionSettings(host="192.168.1.1")
        telem = TelemetrySettings(interval=50)

        settings = Settings(connection=conn, telemetry=telem)

        assert settings.connection.host == "192.168.1.1"
        assert settings.telemetry.interval == 50

    def test_to_dict(self):
        """Test converting Settings to dictionary"""
        settings = Settings()
        settings.connection.host = "test.local"
        settings.telemetry.interval = 200

        data = settings.to_dict()

        assert isinstance(data, dict)
        assert "connection" in data
        assert "telemetry" in data
        assert data["connection"]["host"] == "test.local"
        assert data["telemetry"]["interval"] == 200

    def test_from_dict(self):
        """Test creating Settings from dictionary"""
        data = {
            "connection": {"host": "192.168.1.50", "port": 30000},
            "telemetry": {"interval": 150},
        }

        settings = Settings.from_dict(data)

        assert settings.connection.host == "192.168.1.50"
        assert settings.connection.port == 30000
        assert settings.telemetry.interval == 150

    def test_from_dict_partial(self):
        """Test creating Settings from partial dictionary"""
        data = {"connection": {"host": "10.0.0.1"}}

        settings = Settings.from_dict(data)

        # Custom values
        assert settings.connection.host == "10.0.0.1"

        # Default values for unspecified
        assert settings.connection.port == 29999
        assert settings.telemetry.interval == 100

    def test_from_dict_empty(self):
        """Test creating Settings from empty dictionary"""
        settings = Settings.from_dict({})

        # Should use all default values
        assert settings.connection.host == "127.0.0.1"
        assert settings.telemetry.interval == 100


class TestLoadConfig:
    """Test load_config function"""

    def test_load_config_yaml(self, tmp_path):
        """Test loading configuration from YAML"""
        config_file = tmp_path / "test_config.yaml"

        # Create test config
        config_data = {
            "connection": {"host": "test.server", "port": 12345},
            "telemetry": {"interval": 200},
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Load config
        settings = load_config(str(config_file))

        assert settings.connection.host == "test.server"
        assert settings.connection.port == 12345
        assert settings.telemetry.interval == 200

    def test_load_nonexistent_config(self, tmp_path):
        """Test loading non-existent config file"""
        config_file = tmp_path / "nonexistent.yaml"

        # Should return default settings
        settings = load_config(str(config_file))

        assert isinstance(settings, Settings)
        assert settings.connection.host == "127.0.0.1"

    def test_load_invalid_yaml(self, tmp_path):
        """Test handling of invalid YAML"""
        config_file = tmp_path / "invalid.yaml"

        # Write invalid YAML
        with open(config_file, "w") as f:
            f.write("invalid: yaml: content: [")

        # Should raise error
        with pytest.raises(yaml.YAMLError):
            load_config(str(config_file))


class TestSaveConfig:
    """Test save_config function"""

    def test_save_config(self, tmp_path):
        """Test saving configuration to YAML"""
        config_file = tmp_path / "save_test.yaml"

        settings = Settings()
        settings.connection.host = "save.test"
        settings.telemetry.interval = 250

        result = save_config(settings, str(config_file))

        assert result is True
        assert config_file.exists()

        # Verify content
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        assert data["connection"]["host"] == "save.test"
        assert data["telemetry"]["interval"] == 250

    def test_save_config_creates_directory(self, tmp_path):
        """Test that save_config creates parent directories"""
        config_file = tmp_path / "subdir" / "config.yaml"

        settings = Settings()
        result = save_config(settings, str(config_file))

        assert result is True
        assert config_file.exists()
        assert config_file.parent.exists()

    def test_save_config_error_handling(self):
        """Test error handling during save"""
        # Try to save to invalid path
        settings = Settings()
        result = save_config(settings, "/invalid/path/config.yaml")

        assert result is False

    def test_save_and_load_roundtrip(self, tmp_path):
        """Test save and load roundtrip"""
        config_file = tmp_path / "roundtrip.yaml"

        # Create settings
        original = Settings()
        original.connection.host = "roundtrip.test"
        original.connection.port = 99999
        original.telemetry.interval = 333
        original.export.format = "json"

        # Save
        save_config(original, str(config_file))

        # Load
        loaded = load_config(str(config_file))

        # Verify
        assert loaded.connection.host == original.connection.host
        assert loaded.connection.port == original.connection.port
        assert loaded.telemetry.interval == original.telemetry.interval
        assert loaded.export.format == original.export.format


class TestCreateDefaultConfig:
    """Test create_default_config function"""

    def test_create_default_config(self, tmp_path):
        """Test creating default configuration file"""
        config_file = tmp_path / "default.yaml"

        settings = create_default_config(str(config_file))

        assert isinstance(settings, Settings)
        assert config_file.exists()

        # Verify it's the default settings
        assert settings.connection.host == "127.0.0.1"
        assert settings.telemetry.interval == 100

    def test_default_config_is_loadable(self, tmp_path):
        """Test that default config can be loaded back"""
        config_file = tmp_path / "default_loadable.yaml"

        # Create default
        create_default_config(str(config_file))

        # Load it back
        loaded = load_config(str(config_file))

        assert loaded.connection.host == "127.0.0.1"
        assert loaded.telemetry.interval == 100


class TestDatabaseSettings:
    """Test DatabaseSettings dataclass"""

    def test_default_values(self):
        """Test default database settings"""
        settings = DatabaseSettings()
        assert settings.url == "sqlite:///telemetry.db"

    def test_custom_values(self):
        """Test custom database settings"""
        settings = DatabaseSettings(url="postgresql://localhost/testdb")
        assert settings.url == "postgresql://localhost/testdb"

    def test_settings_includes_database(self):
        """Test that Settings includes database configuration"""
        settings = Settings()
        assert isinstance(settings.database, DatabaseSettings)
        assert settings.database.url == "sqlite:///telemetry.db"

    def test_settings_to_dict_includes_database(self):
        """Test that Settings.to_dict includes database"""
        settings = Settings()
        settings.database.url = "postgresql://localhost/db"

        data = settings.to_dict()
        assert "database" in data
        assert data["database"]["url"] == "postgresql://localhost/db"

    def test_settings_from_dict_includes_database(self):
        """Test that Settings.from_dict includes database"""
        data = {
            "connection": {"host": "localhost"},
            "database": {"url": "mysql://localhost/testdb"},
        }

        settings = Settings.from_dict(data)
        assert settings.database.url == "mysql://localhost/testdb"


class TestGetDatabaseUrl:
    """Test get_database_url function"""

    def test_default_database_url(self, monkeypatch):
        """Test default database URL when env var not set"""
        monkeypatch.delenv("DATABASE_URL", raising=False)

        url = get_database_url()
        assert url == "sqlite:///telemetry.db"

    def test_environment_variable_override(self, monkeypatch):
        """Test DATABASE_URL environment variable override"""
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/testdb")

        url = get_database_url()
        assert url == "postgresql://localhost/testdb"

    def test_mysql_url(self, monkeypatch):
        """Test MySQL database URL"""
        monkeypatch.setenv("DATABASE_URL", "mysql://user:pass@localhost:3306/lfs_db")

        url = get_database_url()
        assert url == "mysql://user:pass@localhost:3306/lfs_db"

    def test_sqlite_custom_path(self, monkeypatch):
        """Test SQLite with custom path"""
        monkeypatch.setenv("DATABASE_URL", "sqlite:////tmp/custom.db")

        url = get_database_url()
        assert url == "sqlite:////tmp/custom.db"


class TestEnvironmentVariableOverride:
    """Test environment variable override (if implemented)"""

    def test_environment_variables(self, monkeypatch, tmp_path):
        """Test environment variable override capability"""
        # This is a placeholder for potential env var override feature
        # Currently not implemented in settings.py

        # Example of how it could work:
        # monkeypatch.setenv('LFS_HOST', '192.168.1.1')
        # monkeypatch.setenv('LFS_PORT', '30000')
        # settings = load_config_with_env()
        # assert settings.connection.host == '192.168.1.1'

        # For now, just verify normal behavior
        config_file = tmp_path / "env_test.yaml"
        create_default_config(str(config_file))
        settings = load_config(str(config_file))

        assert settings.connection.host == "127.0.0.1"
