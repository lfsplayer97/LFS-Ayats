"""
Unit tests for lap comparator module.
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict
from src.visualization.comparator import LapComparator, LapComparison


# Mock CarTelemetry for testing
@dataclass
class MockCarTelemetry:
    timestamp: float = 0.0
    plid: int = 1
    node: int = 0
    lap: int = 1
    position: Dict = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    speed: float = 0.0
    direction: int = 0
    heading: int = 0
    angular_velocity: int = 0


class TestLapComparator:
    """Test cases for LapComparator class."""

    @pytest.fixture
    def comparator(self):
        """Create a lap comparator instance."""
        return LapComparator()

    @pytest.fixture
    def sample_lap1(self):
        """Create sample lap 1 data."""
        telemetry = []
        for i in range(20):
            t = MockCarTelemetry(
                timestamp=float(i),
                position={"x": i * 10, "y": i * 5, "z": 0},
                speed=15.0 + i * 0.5,
            )
            telemetry.append(t)
        return telemetry

    @pytest.fixture
    def sample_lap2(self):
        """Create sample lap 2 data (slightly faster)."""
        telemetry = []
        for i in range(20):
            t = MockCarTelemetry(
                timestamp=float(i) * 0.95,  # 5% faster
                position={"x": i * 10 + 2, "y": i * 5 + 1, "z": 0},
                speed=16.0 + i * 0.5,
            )
            telemetry.append(t)
        return telemetry

    def test_init(self, comparator):
        """Test comparator initialization."""
        assert comparator is not None
        assert len(comparator.laps) == 0

    def test_add_lap(self, comparator, sample_lap1):
        """Test adding a lap."""
        comparator.add_lap("Lap 1", sample_lap1)
        assert "Lap 1" in comparator.laps
        assert len(comparator.laps["Lap 1"]) == len(sample_lap1)

    def test_add_multiple_laps(self, comparator, sample_lap1, sample_lap2):
        """Test adding multiple laps."""
        comparator.add_lap("Lap 1", sample_lap1)
        comparator.add_lap("Lap 2", sample_lap2)
        assert len(comparator.laps) == 2
        assert "Lap 1" in comparator.laps
        assert "Lap 2" in comparator.laps

    def test_remove_lap(self, comparator, sample_lap1):
        """Test removing a lap."""
        comparator.add_lap("Lap 1", sample_lap1)
        comparator.remove_lap("Lap 1")
        assert "Lap 1" not in comparator.laps

    def test_remove_nonexistent_lap(self, comparator):
        """Test removing a lap that doesn't exist."""
        comparator.remove_lap("Nonexistent")  # Should not raise error
        assert len(comparator.laps) == 0

    def test_clear_laps(self, comparator, sample_lap1, sample_lap2):
        """Test clearing all laps."""
        comparator.add_lap("Lap 1", sample_lap1)
        comparator.add_lap("Lap 2", sample_lap2)
        comparator.clear_laps()
        assert len(comparator.laps) == 0

    def test_compare_laps_valid(self, comparator, sample_lap1, sample_lap2):
        """Test comparing two valid laps."""
        comparison = comparator.compare_laps(sample_lap1, sample_lap2)
        assert comparison is not None
        assert isinstance(comparison, LapComparison)
        assert len(comparison.lap_names) == 2
        assert comparison.total_time_diff >= 0

    def test_compare_laps_empty(self, comparator):
        """Test comparing with empty laps."""
        comparison = comparator.compare_laps([], [])
        assert comparison is None

    def test_compare_laps_one_empty(self, comparator, sample_lap1):
        """Test comparing when one lap is empty."""
        comparison = comparator.compare_laps(sample_lap1, [])
        assert comparison is None

    def test_create_comparison_plot_with_data(
        self, comparator, sample_lap1, sample_lap2
    ):
        """Test creating comparison plot with valid data."""
        comparator.add_lap("Lap 1", sample_lap1)
        comparator.add_lap("Lap 2", sample_lap2)
        fig = comparator.create_comparison_plot()
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_comparison_plot_explicit_laps(self, sample_lap1, sample_lap2):
        """Test creating comparison plot with explicit lap data."""
        comparator = LapComparator()
        fig = comparator.create_comparison_plot(
            laps=[sample_lap1, sample_lap2], lap_names=["Lap 1", "Lap 2"]
        )
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_comparison_plot_empty(self, comparator):
        """Test creating comparison plot with no data."""
        fig = comparator.create_comparison_plot()
        assert fig is not None

    def test_create_time_delta_plot_with_data(
        self, comparator, sample_lap1, sample_lap2
    ):
        """Test creating time delta plot with valid data."""
        fig = comparator.create_time_delta_plot(sample_lap1, sample_lap2)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_time_delta_plot_empty(self, comparator):
        """Test creating time delta plot with empty data."""
        fig = comparator.create_time_delta_plot([], [])
        assert fig is not None

    def test_create_sector_comparison_with_data(
        self, comparator, sample_lap1, sample_lap2
    ):
        """Test creating sector comparison with valid data."""
        comparator.add_lap("Lap 1", sample_lap1)
        comparator.add_lap("Lap 2", sample_lap2)
        fig = comparator.create_sector_comparison()
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_sector_comparison_empty(self, comparator):
        """Test creating sector comparison with no data."""
        fig = comparator.create_sector_comparison()
        assert fig is not None

    def test_create_trajectory_overlay_with_data(
        self, comparator, sample_lap1, sample_lap2
    ):
        """Test creating trajectory overlay with valid data."""
        comparator.add_lap("Lap 1", sample_lap1)
        comparator.add_lap("Lap 2", sample_lap2)
        fig = comparator.create_trajectory_overlay()
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_trajectory_overlay_empty(self, comparator):
        """Test creating trajectory overlay with no data."""
        fig = comparator.create_trajectory_overlay()
        assert fig is not None

    def test_get_statistics_with_laps(self, comparator, sample_lap1, sample_lap2):
        """Test getting statistics with stored laps."""
        comparator.add_lap("Lap 1", sample_lap1)
        comparator.add_lap("Lap 2", sample_lap2)
        stats = comparator.get_statistics()

        assert stats is not None
        assert stats["num_laps"] == 2
        assert "Lap 1" in stats["lap_names"]
        assert "Lap 2" in stats["lap_names"]
        assert "lap_lengths" in stats
        assert "lap_times" in stats
        assert "fastest_lap" in stats
        assert "slowest_lap" in stats

    def test_get_statistics_empty(self, comparator):
        """Test getting statistics with no laps."""
        stats = comparator.get_statistics()
        assert stats is not None
        assert stats["num_laps"] == 0
        assert len(stats["lap_names"]) == 0


class TestLapComparison:
    """Test cases for LapComparison dataclass."""

    def test_lap_comparison_creation(self):
        """Test creating a LapComparison object."""
        comparison = LapComparison(
            lap_names=["Lap 1", "Lap 2"],
            time_differences=[0.0, 0.5],
            faster_lap=0,
            total_time_diff=0.5,
            sector_diffs={"sector1": 0.2, "sector2": 0.15, "sector3": 0.15},
        )

        assert comparison is not None
        assert len(comparison.lap_names) == 2
        assert comparison.faster_lap == 0
        assert comparison.total_time_diff == 0.5
        assert len(comparison.sector_diffs) == 3
