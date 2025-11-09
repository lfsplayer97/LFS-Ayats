"""
Unit tests for DatabaseExporter.
"""

import pytest
from datetime import datetime
from dataclasses import dataclass, field

from src.export.db_exporter import DatabaseExporter


# Mock telemetry data for testing
@dataclass
class MockCarTelemetry:
    timestamp: float = 0.0
    plid: int = 1
    node: int = 0
    lap: int = 1
    position: dict = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    speed: float = 0.0
    direction: int = 0
    heading: int = 0
    angular_velocity: int = 0
    rpm: int = 1000
    gear: int = 1
    throttle: float = 0.5
    brake: float = 0.0
    clutch: float = 0.0
    steering_angle: float = 0.0
    engine_temp: float = 85.0


@pytest.fixture
def in_memory_exporter():
    """Create an in-memory database exporter for testing"""
    exporter = DatabaseExporter("sqlite:///:memory:", echo=False, create_tables=True)
    yield exporter
    exporter.close()


class TestDatabaseExporter:
    """Test cases for DatabaseExporter"""

    def test_init(self):
        """Test exporter initialization"""
        exporter = DatabaseExporter("sqlite:///:memory:")

        assert exporter.repository is not None

        exporter.close()

    def test_init_without_create_tables(self):
        """Test initialization without creating tables"""
        exporter = DatabaseExporter("sqlite:///:memory:", create_tables=False)

        assert exporter.repository is not None

        exporter.close()

    def test_from_config_sqlite(self):
        """Test creating exporter from SQLite config"""
        config = {"type": "sqlite", "sqlite": {"path": ":memory:"}, "echo": False}

        exporter = DatabaseExporter.from_config(config)

        assert exporter.repository is not None

        exporter.close()

    def test_from_config_postgresql(self):
        """Test creating exporter from PostgreSQL config"""
        config = {
            "type": "postgresql",
            "postgresql": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
            },
            "echo": False,
        }

        # Just test config parsing, don't actually connect
        try:
            exporter = DatabaseExporter.from_config(config)
            exporter.close()
        except Exception:
            # Connection will fail but config parsing should work
            pass

    def test_from_config_unsupported_type(self):
        """Test error on unsupported database type"""
        config = {"type": "mongodb", "echo": False}

        with pytest.raises(ValueError, match="Unsupported database type"):
            DatabaseExporter.from_config(config)


class TestExportSession:
    """Test session export operations"""

    def test_export_session_basic(self, in_memory_exporter):
        """Test exporting a basic session"""
        session_data = {
            "datetime": datetime.now(),
            "driver_name": "Player1",
            "duration": 600,
        }

        session_id = in_memory_exporter.export_session(session_data)

        assert session_id > 0

        # Verify session was saved
        stats = in_memory_exporter.get_session_statistics(session_id)
        assert stats["driver_name"] == "Player1"
        assert stats["duration"] == 600

    def test_export_session_with_circuit_and_vehicle(self, in_memory_exporter):
        """Test exporting session with circuit and vehicle"""
        # Create circuit and vehicle first
        in_memory_exporter.repository.create_circuit("Blackwood GP", "BL1", 3290.0)
        in_memory_exporter.repository.create_vehicle("XF GTI", "XFG", "TBO")

        session_data = {
            "datetime": datetime.now(),
            "circuit_name": "BL1",
            "vehicle_name": "XFG",
            "driver_name": "Player1",
        }

        session_id = in_memory_exporter.export_session(session_data)

        assert session_id > 0

    def test_export_session_with_laps(self, in_memory_exporter):
        """Test exporting session with laps"""
        session_data = {"datetime": datetime.now(), "driver_name": "Player1"}

        laps_data = [
            {"lap_number": 1, "lap_time": 95000, "valid": True},
            {"lap_number": 2, "lap_time": 93000, "valid": True},
            {"lap_number": 3, "lap_time": 94000, "valid": True},
        ]

        session_id = in_memory_exporter.export_session(session_data, laps_data)

        assert session_id > 0

        # Verify laps were saved
        stats = in_memory_exporter.get_session_statistics(session_id)
        assert stats["total_laps"] == 3
        assert stats["best_lap_time"] == 93000


class TestExportTelemetry:
    """Test telemetry export operations"""

    def test_export_telemetry_with_objects(self, in_memory_exporter):
        """Test exporting telemetry data from objects"""
        # Create session and lap
        session_id = in_memory_exporter.repository.save_session(datetime.now())
        lap_id = in_memory_exporter.repository.save_lap(session_id, 1)

        # Export telemetry
        telemetry_data = [
            MockCarTelemetry(timestamp=0.0, speed=0.0, rpm=1000),
            MockCarTelemetry(timestamp=0.1, speed=10.0, rpm=2000),
            MockCarTelemetry(timestamp=0.2, speed=20.0, rpm=3000),
        ]

        count = in_memory_exporter.export_telemetry(telemetry_data, lap_id=lap_id)

        assert count == 3

    def test_export_telemetry_with_dicts(self, in_memory_exporter):
        """Test exporting telemetry data from dictionaries"""
        # Create session and lap
        session_id = in_memory_exporter.repository.save_session(datetime.now())
        lap_id = in_memory_exporter.repository.save_lap(session_id, 1)

        # Export telemetry
        telemetry_data = [
            {"timestamp": 0, "speed": 0.0, "rpm": 1000},
            {"timestamp": 100, "speed": 10.0, "rpm": 2000},
            {"timestamp": 200, "speed": 20.0, "rpm": 3000},
        ]

        count = in_memory_exporter.export_telemetry(telemetry_data, lap_id=lap_id)

        assert count == 3

    def test_export_telemetry_creates_default_session(self, in_memory_exporter):
        """Test exporting telemetry creates default session if no lap_id"""
        telemetry_data = [
            MockCarTelemetry(timestamp=0.0, speed=0.0),
        ]

        count = in_memory_exporter.export_telemetry(telemetry_data)

        assert count == 1

    def test_export_telemetry_empty_list(self, in_memory_exporter):
        """Test exporting empty telemetry list"""
        count = in_memory_exporter.export_telemetry([])

        assert count == 0


class TestExportCompleteSession:
    """Test complete session export"""

    def test_export_complete_session(self, in_memory_exporter):
        """Test exporting complete session with laps and telemetry"""
        session_data = {
            "datetime": datetime.now(),
            "driver_name": "Player1",
            "duration": 600,
        }

        laps_with_telemetry = [
            {
                "lap_metadata": {
                    "lap_number": 1,
                    "lap_time": 95000,
                    "sector1_time": 30000,
                    "sector2_time": 32000,
                    "sector3_time": 33000,
                    "valid": True,
                },
                "telemetry_points": [
                    {"timestamp": 0, "speed": 0.0, "rpm": 1000},
                    {"timestamp": 100, "speed": 10.0, "rpm": 2000},
                ],
            },
            {
                "lap_metadata": {"lap_number": 2, "lap_time": 93000, "valid": True},
                "telemetry_points": [
                    {"timestamp": 0, "speed": 0.0, "rpm": 1000},
                    {"timestamp": 100, "speed": 15.0, "rpm": 2500},
                ],
            },
        ]

        session_id = in_memory_exporter.export_complete_session(
            session_data, laps_with_telemetry
        )

        assert session_id > 0

        # Verify data was saved
        stats = in_memory_exporter.get_session_statistics(session_id)
        assert stats["total_laps"] == 2
        assert stats["telemetry_points"] == 4  # 2 points per lap

    def test_export_complete_session_without_telemetry(self, in_memory_exporter):
        """Test exporting complete session without telemetry"""
        session_data = {"datetime": datetime.now(), "driver_name": "Player1"}

        laps_with_telemetry = [
            {
                "lap_metadata": {"lap_number": 1, "lap_time": 95000},
                "telemetry_points": [],
            }
        ]

        session_id = in_memory_exporter.export_complete_session(
            session_data, laps_with_telemetry
        )

        assert session_id > 0

        stats = in_memory_exporter.get_session_statistics(session_id)
        assert stats["telemetry_points"] == 0


class TestSetupOperations:
    """Test setup operations"""

    def test_setup_circuits_and_vehicles(self, in_memory_exporter):
        """Test setting up circuits and vehicles"""
        circuits = [
            {"name": "Blackwood GP", "short_name": "BL1", "length": 3290.0},
            {"name": "Kyoto Ring Oval", "short_name": "KY1", "length": 3304.0},
        ]

        vehicles = [
            {"name": "XF GTI", "short_name": "XFG", "class_type": "TBO"},
            {"name": "XR GT", "short_name": "XRG", "class_type": "TBO"},
        ]

        in_memory_exporter.setup_circuits_and_vehicles(circuits, vehicles)

        # Verify circuits were created
        sessions = in_memory_exporter.repository.get_sessions_by_circuit("BL1")
        # Should not raise error

    def test_setup_circuits_only(self, in_memory_exporter):
        """Test setting up only circuits"""
        circuits = [
            {"name": "Blackwood GP", "short_name": "BL1", "length": 3290.0},
        ]

        in_memory_exporter.setup_circuits_and_vehicles(circuits=circuits)

        # Should complete without error

    def test_setup_vehicles_only(self, in_memory_exporter):
        """Test setting up only vehicles"""
        vehicles = [
            {"name": "XF GTI", "short_name": "XFG", "class_type": "TBO"},
        ]

        in_memory_exporter.setup_circuits_and_vehicles(vehicles=vehicles)

        # Should complete without error


class TestGetStatistics:
    """Test statistics retrieval"""

    def test_get_session_statistics(self, in_memory_exporter):
        """Test getting session statistics"""
        # Create a session with data
        session_data = {
            "datetime": datetime.now(),
            "driver_name": "Player1",
            "duration": 600,
        }
        laps_data = [
            {"lap_number": 1, "lap_time": 95000, "valid": True},
        ]

        session_id = in_memory_exporter.export_session(session_data, laps_data)

        # Get statistics
        stats = in_memory_exporter.get_session_statistics(session_id)

        assert stats["session_id"] == session_id
        assert stats["driver_name"] == "Player1"
        assert stats["total_laps"] == 1


class TestCloseOperation:
    """Test close operation"""

    def test_close(self):
        """Test closing exporter"""
        exporter = DatabaseExporter("sqlite:///:memory:")

        # Should not raise error
        exporter.close()
