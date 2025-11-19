"""
Unit tests for analysis.utils module.

Tests for data classes and utility functions used in analysis.
"""

import pytest
from src.analysis.utils import (
    AlertLevel,
    Alert,
    SectorComparison,
    LapComparison,
    BrakingPoint,
    ThrottleAnalysis,
    TimeDelta,
    RacingLine,
    Sector,
    calculate_percentage_difference,
    moving_average,
)


class TestAlertLevel:
    """Test cases for AlertLevel enum."""

    def test_alert_levels_exist(self):
        """Test all alert levels are defined."""
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.ERROR.value == "error"
        assert AlertLevel.CRITICAL.value == "critical"


class TestAlert:
    """Test cases for Alert dataclass."""

    def test_init_with_required_fields(self):
        """Test Alert initialization with required fields."""
        alert = Alert(level=AlertLevel.INFO, message="Test message")
        assert alert.level == AlertLevel.INFO
        assert alert.message == "Test message"
        assert isinstance(alert.timestamp, float)
        assert alert.data == {}

    def test_init_with_data(self):
        """Test Alert initialization with additional data."""
        data = {"key": "value", "number": 42}
        alert = Alert(level=AlertLevel.WARNING, message="Warning", data=data)
        assert alert.data == data

    def test_str_representation(self):
        """Test string representation of Alert."""
        alert = Alert(level=AlertLevel.ERROR, message="Error occurred")
        assert str(alert) == "[ERROR] Error occurred"

    def test_timestamp_is_generated(self):
        """Test that timestamp is automatically generated."""
        alert1 = Alert(level=AlertLevel.INFO, message="First")
        alert2 = Alert(level=AlertLevel.INFO, message="Second")
        # Timestamps should be different (assuming enough time passes)
        assert isinstance(alert1.timestamp, float)
        assert isinstance(alert2.timestamp, float)


class TestSectorComparison:
    """Test cases for SectorComparison dataclass."""

    def test_init(self):
        """Test SectorComparison initialization."""
        comparison = SectorComparison(
            sector_number=1,
            lap1_time=25.5,
            lap2_time=25.3,
            difference=0.2,
            percentage_diff=0.79,
        )
        assert comparison.sector_number == 1
        assert comparison.lap1_time == 25.5
        assert comparison.lap2_time == 25.3
        assert comparison.difference == 0.2
        assert comparison.percentage_diff == 0.79


class TestLapComparison:
    """Test cases for LapComparison dataclass."""

    def test_init_with_defaults(self):
        """Test LapComparison initialization with default values."""
        comparison = LapComparison(lap1_id=1, lap2_id=2, time_difference=0.5)
        assert comparison.lap1_id == 1
        assert comparison.lap2_id == 2
        assert comparison.time_difference == 0.5
        assert comparison.sector_comparisons == []
        assert comparison.speed_trace_comparison == {}
        assert comparison.racing_line_difference == 0.0
        assert comparison.suggestions == []

    def test_init_with_all_fields(self):
        """Test LapComparison initialization with all fields."""
        sector_comp = SectorComparison(1, 25.5, 25.3, 0.2, 0.79)
        comparison = LapComparison(
            lap1_id=1,
            lap2_id=2,
            time_difference=0.5,
            sector_comparisons=[sector_comp],
            speed_trace_comparison={"avg_speed": 120.5},
            racing_line_difference=2.5,
            suggestions=["Brake later in turn 1"],
        )
        assert len(comparison.sector_comparisons) == 1
        assert comparison.speed_trace_comparison["avg_speed"] == 120.5
        assert comparison.racing_line_difference == 2.5
        assert len(comparison.suggestions) == 1


class TestBrakingPoint:
    """Test cases for BrakingPoint dataclass."""

    def test_init_with_defaults(self):
        """Test BrakingPoint initialization with default values."""
        point = BrakingPoint(
            position={"x": 100.0, "y": 50.0},
            lap=1,
            distance=150.0,
            speed_before=180.0,
            speed_after=90.0,
            brake_duration=1.5,
        )
        assert point.position == {"x": 100.0, "y": 50.0}
        assert point.lap == 1
        assert point.distance == 150.0
        assert point.speed_before == 180.0
        assert point.speed_after == 90.0
        assert point.brake_duration == 1.5
        assert point.consistency_score == 1.0

    def test_init_with_custom_consistency(self):
        """Test BrakingPoint initialization with custom consistency score."""
        point = BrakingPoint(
            position={"x": 100.0, "y": 50.0},
            lap=1,
            distance=150.0,
            speed_before=180.0,
            speed_after=90.0,
            brake_duration=1.5,
            consistency_score=0.85,
        )
        assert point.consistency_score == 0.85


class TestThrottleAnalysis:
    """Test cases for ThrottleAnalysis dataclass."""

    def test_init(self):
        """Test ThrottleAnalysis initialization."""
        analysis = ThrottleAnalysis(
            corner_id=1,
            entry_speed=120.0,
            apex_speed=80.0,
            exit_speed=150.0,
            throttle_application_point=0.5,
            full_throttle_point=0.8,
            time_in_corner=3.5,
        )
        assert analysis.corner_id == 1
        assert analysis.entry_speed == 120.0
        assert analysis.apex_speed == 80.0
        assert analysis.exit_speed == 150.0
        assert analysis.throttle_application_point == 0.5
        assert analysis.full_throttle_point == 0.8
        assert analysis.time_in_corner == 3.5


class TestTimeDelta:
    """Test cases for TimeDelta dataclass."""

    def test_init_with_defaults(self):
        """Test TimeDelta initialization with default values."""
        delta = TimeDelta()
        assert delta.distance_points == []
        assert delta.time_deltas == []
        assert delta.max_gain == 0.0
        assert delta.max_loss == 0.0
        assert delta.average_delta == 0.0

    def test_init_with_data(self):
        """Test TimeDelta initialization with data."""
        delta = TimeDelta(
            distance_points=[0.0, 100.0, 200.0],
            time_deltas=[0.0, 0.2, -0.1],
            max_gain=0.2,
            max_loss=-0.1,
            average_delta=0.033,
        )
        assert len(delta.distance_points) == 3
        assert len(delta.time_deltas) == 3
        assert delta.max_gain == 0.2
        assert delta.max_loss == -0.1
        assert delta.average_delta == 0.033


class TestRacingLine:
    """Test cases for RacingLine dataclass."""

    def test_init_with_defaults(self):
        """Test RacingLine initialization with default values."""
        line = RacingLine()
        assert line.points == []
        assert line.speeds == []
        assert line.sector is None
        assert line.lap_time is None

    def test_init_with_data(self):
        """Test RacingLine initialization with data."""
        line = RacingLine(
            points=[{"x": 0.0, "y": 0.0}, {"x": 10.0, "y": 5.0}],
            speeds=[100.0, 120.0],
            sector=1,
            lap_time=85.5,
        )
        assert len(line.points) == 2
        assert len(line.speeds) == 2
        assert line.sector == 1
        assert line.lap_time == 85.5


class TestSector:
    """Test cases for Sector dataclass."""

    def test_init_with_defaults(self):
        """Test Sector initialization with default values."""
        sector = Sector(number=1, time=25.5)
        assert sector.number == 1
        assert sector.time == 25.5
        assert sector.time_lost == 0.0
        assert sector.consistency == 1.0
        assert sector.best_time is None

    def test_init_with_all_fields(self):
        """Test Sector initialization with all fields."""
        sector = Sector(
            number=2,
            time=26.3,
            time_lost=0.8,
            consistency=0.92,
            best_time=25.5,
        )
        assert sector.number == 2
        assert sector.time == 26.3
        assert sector.time_lost == 0.8
        assert sector.consistency == 0.92
        assert sector.best_time == 25.5


class TestCalculatePercentageDifference:
    """Test cases for calculate_percentage_difference function."""

    def test_positive_difference(self):
        """Test percentage difference with positive result."""
        result = calculate_percentage_difference(110.0, 100.0)
        assert result == 10.0

    def test_negative_difference(self):
        """Test percentage difference with negative result."""
        result = calculate_percentage_difference(90.0, 100.0)
        assert result == -10.0

    def test_zero_difference(self):
        """Test percentage difference when values are equal."""
        result = calculate_percentage_difference(100.0, 100.0)
        assert result == 0.0

    def test_zero_reference_value(self):
        """Test percentage difference when reference value is zero."""
        result = calculate_percentage_difference(50.0, 0.0)
        assert result == 0.0

    def test_small_difference(self):
        """Test percentage difference with small values."""
        result = calculate_percentage_difference(100.5, 100.0)
        assert pytest.approx(result, rel=1e-2) == 0.5

    def test_large_difference(self):
        """Test percentage difference with large values."""
        result = calculate_percentage_difference(200.0, 100.0)
        assert result == 100.0


class TestMovingAverage:
    """Test cases for moving_average function."""

    def test_basic_moving_average(self):
        """Test basic moving average calculation."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = moving_average(data, 3)
        expected = [1.0, 1.5, 2.0, 3.0, 4.0]
        assert result == expected

    def test_window_size_one(self):
        """Test moving average with window size of 1."""
        data = [1.0, 2.0, 3.0]
        result = moving_average(data, 1)
        assert result == data

    def test_window_size_equals_data_length(self):
        """Test moving average when window size equals data length."""
        data = [1.0, 2.0, 3.0]
        result = moving_average(data, 3)
        expected = [1.0, 1.5, 2.0]
        assert result == expected

    def test_window_size_larger_than_data(self):
        """Test moving average when window size is larger than data."""
        data = [1.0, 2.0, 3.0]
        result = moving_average(data, 5)
        assert result == data

    def test_zero_window_size(self):
        """Test moving average with zero window size."""
        data = [1.0, 2.0, 3.0]
        result = moving_average(data, 0)
        assert result == data

    def test_negative_window_size(self):
        """Test moving average with negative window size."""
        data = [1.0, 2.0, 3.0]
        result = moving_average(data, -1)
        assert result == data

    def test_empty_data(self):
        """Test moving average with empty data."""
        data = []
        result = moving_average(data, 3)
        assert result == []

    def test_single_element(self):
        """Test moving average with single element."""
        data = [5.0]
        result = moving_average(data, 3)
        assert result == [5.0]

    def test_floating_point_precision(self):
        """Test moving average with floating point values."""
        data = [1.1, 2.2, 3.3, 4.4, 5.5]
        result = moving_average(data, 2)
        expected = [1.1, 1.65, 2.75, 3.85, 4.95]
        for i in range(len(result)):
            assert pytest.approx(result[i], rel=1e-2) == expected[i]
