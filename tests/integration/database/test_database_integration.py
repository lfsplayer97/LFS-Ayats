"""
Integration tests for database system.

These tests use a real SQLite database file to test the complete
database workflow end-to-end.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.export.db_exporter import DatabaseExporter
from src.database.repository import TelemetryRepository


@pytest.fixture
def temp_db_file():
    """Create a temporary database file"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)
    Path(db_path + "-journal").unlink(missing_ok=True)


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for complete database workflow"""

    def test_complete_workflow(self, temp_db_file):
        """Test complete workflow: export, query, and analyze"""
        # Create exporter
        connection_string = f"sqlite:///{temp_db_file}"
        exporter = DatabaseExporter(connection_string)

        try:
            # Step 1: Setup circuits and vehicles
            circuits = [
                {"name": "Blackwood GP", "short_name": "BL1", "length": 3290.0},
            ]
            vehicles = [
                {"name": "XF GTI", "short_name": "XFG", "class_type": "TBO"},
            ]
            exporter.setup_circuits_and_vehicles(circuits, vehicles)

            # Step 2: Export a complete session
            session_data = {
                "datetime": datetime.now(),
                "circuit_name": "BL1",
                "vehicle_name": "XFG",
                "driver_name": "Integration Test",
                "duration": 300,
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
                        {
                            "timestamp": i * 100,
                            "speed": float(i * 5),
                            "rpm": 1000 + i * 100,
                            "gear": min(i // 10, 4),
                            "throttle": min(i * 0.1, 1.0),
                        }
                        for i in range(20)
                    ],
                },
                {
                    "lap_metadata": {
                        "lap_number": 2,
                        "lap_time": 93000,
                        "sector1_time": 29500,
                        "sector2_time": 31500,
                        "sector3_time": 32000,
                        "valid": True,
                    },
                    "telemetry_points": [
                        {
                            "timestamp": i * 100,
                            "speed": float(i * 5 + 5),
                            "rpm": 1000 + i * 100 + 200,
                        }
                        for i in range(20)
                    ],
                },
            ]

            session_id = exporter.export_complete_session(
                session_data, laps_with_telemetry
            )

            assert session_id > 0

            # Step 3: Query and verify
            stats = exporter.get_session_statistics(session_id)
            assert stats["driver_name"] == "Integration Test"
            assert stats["total_laps"] == 2
            assert stats["valid_laps"] == 2
            assert stats["best_lap_time"] == 93000
            assert stats["telemetry_points"] == 40  # 20 points per lap

            # Step 4: Query best lap
            best_lap = exporter.repository.get_best_lap(session_id)
            assert best_lap is not None
            assert best_lap.lap_number == 2
            assert best_lap.lap_time == 93000

            # Step 5: Get telemetry for best lap
            telemetry = exporter.repository.get_telemetry_points(best_lap.id)
            assert len(telemetry) == 20

            # Verify telemetry is ordered by timestamp
            for i, point in enumerate(telemetry):
                assert point.timestamp == i * 100
                assert point.speed == float(i * 5 + 5)

            # Step 6: Compare laps
            session = exporter.repository.get_session(session_id)
            lap_ids = [lap.id for lap in session.laps]
            comparison = exporter.repository.compare_laps(lap_ids)

            assert len(comparison["laps"]) == 2
            assert comparison["fastest_lap_id"] == best_lap.id
            assert comparison["average_time"] == (95000 + 93000) / 2

        finally:
            exporter.close()

    def test_multiple_sessions(self, temp_db_file):
        """Test handling multiple sessions"""
        connection_string = f"sqlite:///{temp_db_file}"
        exporter = DatabaseExporter(connection_string)

        try:
            # Create multiple sessions
            session_ids = []
            for i in range(3):
                session_data = {
                    "datetime": datetime.now(),
                    "driver_name": f"Driver{i}",
                    "duration": 300 + i * 60,
                }
                session_id = exporter.export_session(session_data)
                session_ids.append(session_id)

            # Verify all sessions exist
            for session_id in session_ids:
                session = exporter.repository.get_session(session_id)
                assert session is not None

        finally:
            exporter.close()

    def test_persistence(self, temp_db_file):
        """Test that data persists across connections"""
        connection_string = f"sqlite:///{temp_db_file}"

        # First connection: create data
        exporter1 = DatabaseExporter(connection_string)
        try:
            session_data = {
                "datetime": datetime.now(),
                "driver_name": "Persistence Test",
            }
            session_id = exporter1.export_session(session_data)
        finally:
            exporter1.close()

        # Second connection: verify data exists
        exporter2 = DatabaseExporter(connection_string, create_tables=False)
        try:
            session = exporter2.repository.get_session(session_id)
            assert session is not None
            assert session.driver_name == "Persistence Test"
        finally:
            exporter2.close()

    def test_large_telemetry_dataset(self, temp_db_file):
        """Test handling large telemetry datasets"""
        connection_string = f"sqlite:///{temp_db_file}"
        exporter = DatabaseExporter(connection_string)

        try:
            # Create session and lap
            session_id = exporter.repository.save_session(datetime.now())
            lap_id = exporter.repository.save_lap(session_id, 1, lap_time=120000)

            # Generate large dataset (simulating 120 seconds at 10Hz = 1200 points)
            telemetry_points = [
                {
                    "timestamp": i * 100,
                    "speed": float(30 + (i % 50)),
                    "rpm": 2000 + (i * 10 % 3000),
                    "gear": min((i // 100) + 1, 5),
                    "throttle": 0.8 if i > 100 else float(i) / 100,
                }
                for i in range(1200)
            ]

            # Save in batch
            count = exporter.repository.save_telemetry_points(lap_id, telemetry_points)
            assert count == 1200

            # Verify retrieval
            retrieved = exporter.repository.get_telemetry_points(lap_id)
            assert len(retrieved) == 1200

            # Verify data integrity
            for i, point in enumerate(retrieved):
                assert point.timestamp == i * 100
                assert point.speed == float(30 + (i % 50))

        finally:
            exporter.close()

    def test_repository_create_and_drop_tables(self, temp_db_file):
        """Test creating and dropping tables"""
        connection_string = f"sqlite:///{temp_db_file}"
        repo = TelemetryRepository(connection_string, echo=False)

        try:
            # Create tables
            repo.create_tables()

            # Verify tables exist by trying to save data
            session_id = repo.save_session(datetime.now())
            assert session_id > 0

            # Drop tables
            repo.drop_tables()

            # Verify tables are gone by attempting to save (should fail)
            with pytest.raises(Exception):  # SQLAlchemy will raise OperationalError
                repo.save_session(datetime.now())

        finally:
            repo.close()
