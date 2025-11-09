"""
Unit tests for TelemetryRepository.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.database.repository import TelemetryRepository
from src.database.models import Base, Session, Lap, TelemetryPoint, Circuit, Vehicle


@pytest.fixture
def in_memory_repo():
    """Create an in-memory repository for testing"""
    repo = TelemetryRepository("sqlite:///:memory:", echo=False)
    repo.create_tables()
    yield repo
    repo.close()


class TestTelemetryRepository:
    """Test cases for TelemetryRepository"""

    def test_init_sqlite(self):
        """Test repository initialization with SQLite"""
        repo = TelemetryRepository("sqlite:///:memory:")
        
        assert repo.engine is not None
        assert repo.SessionLocal is not None
        
        repo.close()

    def test_init_with_echo(self):
        """Test repository initialization with SQL logging"""
        repo = TelemetryRepository("sqlite:///:memory:", echo=True)
        
        assert repo.engine.echo is True
        
        repo.close()

    def test_create_tables(self, in_memory_repo):
        """Test table creation"""
        # Tables should already be created by fixture
        # Verify by checking engine has tables
        from sqlalchemy import inspect
        inspector = inspect(in_memory_repo.engine)
        table_names = inspector.get_table_names()
        
        assert "circuits" in table_names
        assert "vehicles" in table_names
        assert "sessions" in table_names
        assert "laps" in table_names
        assert "telemetry_points" in table_names

    def test_drop_tables(self):
        """Test table dropping"""
        from sqlalchemy import inspect
        repo = TelemetryRepository("sqlite:///:memory:")
        repo.create_tables()
        repo.drop_tables()
        
        # Verify tables are dropped
        inspector = inspect(repo.engine)
        table_names = inspector.get_table_names()
        
        assert len(table_names) == 0
        
        repo.close()


class TestSessionOperations:
    """Test session CRUD operations"""

    def test_save_session_basic(self, in_memory_repo):
        """Test saving a basic session"""
        now = datetime.now()
        
        session_id = in_memory_repo.save_session(
            datetime_start=now,
            driver_name="Player1",
            duration=600
        )
        
        assert session_id > 0
        
        # Verify session was saved
        session = in_memory_repo.get_session(session_id)
        assert session is not None
        assert session.driver_name == "Player1"
        assert session.duration == 600

    def test_save_session_with_circuit(self, in_memory_repo):
        """Test saving session with circuit reference"""
        # Create circuit first
        circuit_id = in_memory_repo.create_circuit("Blackwood GP", "BL1", 3290.0)
        
        # Save session with circuit
        session_id = in_memory_repo.save_session(
            datetime_start=datetime.now(),
            circuit_name="BL1"
        )
        
        # Verify circuit association
        session = in_memory_repo.get_session(session_id)
        assert session.circuit_id == circuit_id

    def test_save_session_with_vehicle(self, in_memory_repo):
        """Test saving session with vehicle reference"""
        # Create vehicle first
        vehicle_id = in_memory_repo.create_vehicle("XF GTI", "XFG", "TBO")
        
        # Save session with vehicle
        session_id = in_memory_repo.save_session(
            datetime_start=datetime.now(),
            vehicle_name="XFG"
        )
        
        # Verify vehicle association
        session = in_memory_repo.get_session(session_id)
        assert session.vehicle_id == vehicle_id

    def test_get_session_not_found(self, in_memory_repo):
        """Test getting non-existent session"""
        session = in_memory_repo.get_session(999)
        
        assert session is None

    def test_get_sessions_by_circuit(self, in_memory_repo):
        """Test getting sessions by circuit"""
        # Create circuit
        circuit_id = in_memory_repo.create_circuit("Blackwood GP", "BL1", 3290.0)
        
        # Create multiple sessions
        session_id1 = in_memory_repo.save_session(datetime.now(), circuit_name="BL1")
        session_id2 = in_memory_repo.save_session(datetime.now(), circuit_name="BL1")
        
        # Get sessions by circuit
        sessions = in_memory_repo.get_sessions_by_circuit("BL1")
        
        assert len(sessions) == 2
        session_ids = [s.id for s in sessions]
        assert session_id1 in session_ids
        assert session_id2 in session_ids

    def test_get_sessions_by_circuit_empty(self, in_memory_repo):
        """Test getting sessions for circuit with no sessions"""
        sessions = in_memory_repo.get_sessions_by_circuit("NONEXISTENT")
        
        assert len(sessions) == 0


class TestLapOperations:
    """Test lap CRUD operations"""

    def test_save_lap(self, in_memory_repo):
        """Test saving a lap"""
        # Create session first
        session_id = in_memory_repo.save_session(datetime.now())
        
        # Save lap
        lap_id = in_memory_repo.save_lap(
            session_id=session_id,
            lap_number=1,
            lap_time=95000,
            sector1_time=30000,
            sector2_time=32000,
            sector3_time=33000,
            valid=True
        )
        
        assert lap_id > 0

    def test_save_lap_updates_total_laps(self, in_memory_repo):
        """Test that saving lap updates session total_laps"""
        # Create session
        session_id = in_memory_repo.save_session(datetime.now())
        
        # Save laps
        in_memory_repo.save_lap(session_id, lap_number=1)
        in_memory_repo.save_lap(session_id, lap_number=2)
        in_memory_repo.save_lap(session_id, lap_number=3)
        
        # Check total laps updated
        session = in_memory_repo.get_session(session_id)
        assert session.total_laps == 3

    def test_get_best_lap(self, in_memory_repo):
        """Test getting best lap"""
        # Create session and laps
        session_id = in_memory_repo.save_session(datetime.now())
        lap1_id = in_memory_repo.save_lap(session_id, 1, lap_time=95000, valid=True)
        lap2_id = in_memory_repo.save_lap(session_id, 2, lap_time=93000, valid=True)
        lap3_id = in_memory_repo.save_lap(session_id, 3, lap_time=94000, valid=True)
        
        # Get best lap
        best_lap = in_memory_repo.get_best_lap(session_id)
        
        assert best_lap is not None
        assert best_lap.id == lap2_id
        assert best_lap.lap_time == 93000

    def test_get_best_lap_ignores_invalid(self, in_memory_repo):
        """Test that best lap ignores invalid laps"""
        # Create session and laps
        session_id = in_memory_repo.save_session(datetime.now())
        in_memory_repo.save_lap(session_id, 1, lap_time=90000, valid=False)  # Invalid but fastest
        lap2_id = in_memory_repo.save_lap(session_id, 2, lap_time=95000, valid=True)
        
        # Get best lap
        best_lap = in_memory_repo.get_best_lap(session_id)
        
        assert best_lap.id == lap2_id
        assert best_lap.lap_time == 95000

    def test_get_best_lap_no_laps(self, in_memory_repo):
        """Test getting best lap when no laps exist"""
        session_id = in_memory_repo.save_session(datetime.now())
        
        best_lap = in_memory_repo.get_best_lap(session_id)
        
        assert best_lap is None


class TestTelemetryPointOperations:
    """Test telemetry point operations"""

    def test_save_telemetry_points(self, in_memory_repo):
        """Test saving telemetry points"""
        # Create session and lap
        session_id = in_memory_repo.save_session(datetime.now())
        lap_id = in_memory_repo.save_lap(session_id, 1)
        
        # Save telemetry points
        points = [
            {"timestamp": 0, "speed": 0.0, "rpm": 1000},
            {"timestamp": 100, "speed": 10.5, "rpm": 2000},
            {"timestamp": 200, "speed": 20.0, "rpm": 3000},
        ]
        
        count = in_memory_repo.save_telemetry_points(lap_id, points)
        
        assert count == 3

    def test_save_telemetry_points_empty(self, in_memory_repo):
        """Test saving empty telemetry points list"""
        session_id = in_memory_repo.save_session(datetime.now())
        lap_id = in_memory_repo.save_lap(session_id, 1)
        
        count = in_memory_repo.save_telemetry_points(lap_id, [])
        
        assert count == 0

    def test_get_telemetry_points(self, in_memory_repo):
        """Test getting telemetry points"""
        # Create session, lap, and points
        session_id = in_memory_repo.save_session(datetime.now())
        lap_id = in_memory_repo.save_lap(session_id, 1)
        
        points = [
            {"timestamp": 0, "speed": 0.0},
            {"timestamp": 100, "speed": 10.5},
            {"timestamp": 200, "speed": 20.0},
        ]
        in_memory_repo.save_telemetry_points(lap_id, points)
        
        # Get points
        retrieved_points = in_memory_repo.get_telemetry_points(lap_id)
        
        assert len(retrieved_points) == 3
        assert retrieved_points[0].timestamp == 0
        assert retrieved_points[1].speed == 10.5
        assert retrieved_points[2].timestamp == 200

    def test_get_telemetry_points_ordered(self, in_memory_repo):
        """Test telemetry points are ordered by timestamp"""
        session_id = in_memory_repo.save_session(datetime.now())
        lap_id = in_memory_repo.save_lap(session_id, 1)
        
        # Save points out of order
        points = [
            {"timestamp": 200, "speed": 20.0},
            {"timestamp": 0, "speed": 0.0},
            {"timestamp": 100, "speed": 10.5},
        ]
        in_memory_repo.save_telemetry_points(lap_id, points)
        
        # Get points
        retrieved_points = in_memory_repo.get_telemetry_points(lap_id)
        
        # Verify ordering
        assert retrieved_points[0].timestamp == 0
        assert retrieved_points[1].timestamp == 100
        assert retrieved_points[2].timestamp == 200


class TestCompareAndStatistics:
    """Test comparison and statistics operations"""

    def test_compare_laps(self, in_memory_repo):
        """Test comparing multiple laps"""
        # Create session and laps
        session_id = in_memory_repo.save_session(datetime.now())
        lap1_id = in_memory_repo.save_lap(session_id, 1, lap_time=95000, valid=True)
        lap2_id = in_memory_repo.save_lap(session_id, 2, lap_time=93000, valid=True)
        lap3_id = in_memory_repo.save_lap(session_id, 3, lap_time=94000, valid=True)
        
        # Compare laps
        comparison = in_memory_repo.compare_laps([lap1_id, lap2_id, lap3_id])
        
        assert len(comparison["laps"]) == 3
        assert comparison["fastest_lap_id"] == lap2_id
        assert comparison["average_time"] == (95000 + 93000 + 94000) / 3

    def test_compare_laps_empty(self, in_memory_repo):
        """Test comparing empty lap list"""
        comparison = in_memory_repo.compare_laps([])
        
        assert comparison["laps"] == []
        assert comparison["fastest_lap_id"] is None

    def test_get_statistics(self, in_memory_repo):
        """Test getting session statistics"""
        # Create session with laps and telemetry
        session_id = in_memory_repo.save_session(
            datetime.now(),
            driver_name="Player1",
            duration=600
        )
        lap1_id = in_memory_repo.save_lap(session_id, 1, lap_time=95000, valid=True)
        lap2_id = in_memory_repo.save_lap(session_id, 2, lap_time=93000, valid=True)
        lap3_id = in_memory_repo.save_lap(session_id, 3, lap_time=94000, valid=False)
        
        # Add telemetry
        points = [{"timestamp": i * 100, "speed": float(i)} for i in range(10)]
        in_memory_repo.save_telemetry_points(lap1_id, points)
        
        # Get statistics
        stats = in_memory_repo.get_statistics(session_id)
        
        assert stats["session_id"] == session_id
        assert stats["driver_name"] == "Player1"
        assert stats["duration"] == 600
        assert stats["total_laps"] == 3
        assert stats["valid_laps"] == 2
        assert stats["best_lap_time"] == 93000
        assert stats["telemetry_points"] == 10

    def test_get_statistics_nonexistent_session(self, in_memory_repo):
        """Test getting statistics for non-existent session"""
        stats = in_memory_repo.get_statistics(999)
        
        assert stats == {}


class TestCircuitAndVehicleOperations:
    """Test circuit and vehicle operations"""

    def test_create_circuit(self, in_memory_repo):
        """Test creating a circuit"""
        circuit_id = in_memory_repo.create_circuit(
            name="Blackwood GP",
            short_name="BL1",
            length=3290.0
        )
        
        assert circuit_id > 0

    def test_create_vehicle(self, in_memory_repo):
        """Test creating a vehicle"""
        vehicle_id = in_memory_repo.create_vehicle(
            name="XF GTI",
            short_name="XFG",
            class_type="TBO"
        )
        
        assert vehicle_id > 0

    def test_create_vehicle_without_class(self, in_memory_repo):
        """Test creating vehicle without class type"""
        vehicle_id = in_memory_repo.create_vehicle(
            name="Formula One",
            short_name="FO8"
        )
        
        assert vehicle_id > 0
