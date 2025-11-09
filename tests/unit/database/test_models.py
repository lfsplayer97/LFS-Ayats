"""
Unit tests for SQLAlchemy models.
"""

import pytest
from datetime import datetime

from src.database.models import Base, Circuit, Vehicle, Session, Lap, TelemetryPoint


class TestCircuitModel:
    """Test cases for Circuit model"""

    def test_circuit_creation(self):
        """Test creating a circuit"""
        circuit = Circuit(
            name="Blackwood GP", short_name="BL1", length=3290.0, sector_count=3
        )

        assert circuit.name == "Blackwood GP"
        assert circuit.short_name == "BL1"
        assert circuit.length == 3290.0
        assert circuit.sector_count == 3

    def test_circuit_repr(self):
        """Test circuit string representation"""
        circuit = Circuit(id=1, name="Blackwood GP", short_name="BL1")

        repr_str = repr(circuit)

        assert "Circuit" in repr_str
        assert "BL1" in repr_str

    def test_circuit_default_sector_count(self):
        """Test default sector count"""
        circuit = Circuit(name="Test Circuit", short_name="TC1")

        # Default is only set when inserted into database
        # Check the default value in the column definition
        assert Circuit.sector_count.default.arg == 3


class TestVehicleModel:
    """Test cases for Vehicle model"""

    def test_vehicle_creation(self):
        """Test creating a vehicle"""
        vehicle = Vehicle(name="XF GTI", short_name="XFG", class_type="TBO")

        assert vehicle.name == "XF GTI"
        assert vehicle.short_name == "XFG"
        assert vehicle.class_type == "TBO"

    def test_vehicle_repr(self):
        """Test vehicle string representation"""
        vehicle = Vehicle(id=1, name="XF GTI", short_name="XFG")

        repr_str = repr(vehicle)

        assert "Vehicle" in repr_str
        assert "XFG" in repr_str


class TestSessionModel:
    """Test cases for Session model"""

    def test_session_creation(self):
        """Test creating a session"""
        now = datetime.now()
        session = Session(
            datetime=now, driver_name="Player1", duration=600, total_laps=10
        )

        assert session.datetime == now
        assert session.driver_name == "Player1"
        assert session.duration == 600
        assert session.total_laps == 10

    def test_session_repr(self):
        """Test session string representation"""
        session = Session(id=1, datetime=datetime.now(), driver_name="Player1")

        repr_str = repr(session)

        assert "Session" in repr_str
        assert "Player1" in repr_str

    def test_session_default_total_laps(self):
        """Test default total laps"""
        session = Session(datetime=datetime.now())

        # Default is only set when inserted into database
        # Check the default value in the column definition
        assert Session.total_laps.default.arg == 0


class TestLapModel:
    """Test cases for Lap model"""

    def test_lap_creation(self):
        """Test creating a lap"""
        lap = Lap(
            session_id=1,
            lap_number=1,
            lap_time=95000,
            sector1_time=30000,
            sector2_time=32000,
            sector3_time=33000,
            valid=True,
        )

        assert lap.session_id == 1
        assert lap.lap_number == 1
        assert lap.lap_time == 95000
        assert lap.sector1_time == 30000
        assert lap.sector2_time == 32000
        assert lap.sector3_time == 33000
        assert lap.valid is True

    def test_lap_repr(self):
        """Test lap string representation"""
        lap = Lap(id=1, session_id=1, lap_number=2, lap_time=95000)

        repr_str = repr(lap)

        assert "Lap" in repr_str
        assert "95000" in repr_str

    def test_lap_default_valid(self):
        """Test default valid flag"""
        lap = Lap(session_id=1, lap_number=1)

        # Default is only set when inserted into database
        # Check the default value in the column definition
        assert Lap.valid.default.arg is True


class TestTelemetryPointModel:
    """Test cases for TelemetryPoint model"""

    def test_telemetry_point_creation(self):
        """Test creating a telemetry point"""
        point = TelemetryPoint(
            lap_id=1,
            timestamp=1000,
            speed=50.5,
            rpm=3000,
            gear=3,
            throttle=0.8,
            brake=0.0,
            clutch=0.0,
            steering_angle=15.5,
            position_x=100.0,
            position_y=200.0,
            position_z=10.0,
            engine_temp=85.5,
        )

        assert point.lap_id == 1
        assert point.timestamp == 1000
        assert point.speed == 50.5
        assert point.rpm == 3000
        assert point.gear == 3
        assert point.throttle == 0.8
        assert point.brake == 0.0
        assert point.clutch == 0.0
        assert point.steering_angle == 15.5
        assert point.position_x == 100.0
        assert point.position_y == 200.0
        assert point.position_z == 10.0
        assert point.engine_temp == 85.5

    def test_telemetry_point_repr(self):
        """Test telemetry point string representation"""
        point = TelemetryPoint(id=1, lap_id=1, timestamp=1000, speed=50.5)

        repr_str = repr(point)

        assert "TelemetryPoint" in repr_str
        assert "50.5" in repr_str

    def test_telemetry_point_minimal(self):
        """Test creating telemetry point with minimal data"""
        point = TelemetryPoint(lap_id=1, timestamp=0, speed=0.0)

        assert point.lap_id == 1
        assert point.timestamp == 0
        assert point.speed == 0.0
        assert point.rpm is None
        assert point.gear is None


class TestModelRelationships:
    """Test cases for model relationships"""

    def test_base_metadata(self):
        """Test Base metadata contains all tables"""
        table_names = [table.name for table in Base.metadata.sorted_tables]

        assert "circuits" in table_names
        assert "vehicles" in table_names
        assert "sessions" in table_names
        assert "laps" in table_names
        assert "telemetry_points" in table_names

    def test_session_relationships_defined(self):
        """Test Session relationships are defined"""
        session = Session(datetime=datetime.now())

        # Check relationship attributes exist
        assert hasattr(session, "circuit")
        assert hasattr(session, "vehicle")
        assert hasattr(session, "laps")

    def test_lap_relationships_defined(self):
        """Test Lap relationships are defined"""
        lap = Lap(session_id=1, lap_number=1)

        # Check relationship attributes exist
        assert hasattr(lap, "session")
        assert hasattr(lap, "telemetry_points")

    def test_telemetry_point_relationships_defined(self):
        """Test TelemetryPoint relationships are defined"""
        point = TelemetryPoint(lap_id=1, timestamp=0, speed=0.0)

        # Check relationship attributes exist
        assert hasattr(point, "lap")
