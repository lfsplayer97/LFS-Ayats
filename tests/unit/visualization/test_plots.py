"""
Unit tests for visualization plots module.
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict
from src.visualization.plots import (
    create_speed_vs_distance_plot,
    create_trajectory_comparison_plot,
    create_braking_analysis_plot,
    create_heatmap_plot,
    create_sector_times_plot,
    create_g_force_plot,
)


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


class TestPlots:
    """Test cases for plot functions."""

    @pytest.fixture
    def sample_telemetry(self):
        """Create sample telemetry data."""
        telemetry = []
        for i in range(10):
            t = MockCarTelemetry(
                timestamp=float(i),
                position={"x": i * 10, "y": i * 5, "z": 0},
                speed=10.0 + i * 2,  # Increasing speed
            )
            telemetry.append(t)
        return telemetry

    def test_create_speed_vs_distance_plot_with_data(self, sample_telemetry):
        """Test speed vs distance plot with valid data."""
        fig = create_speed_vs_distance_plot(sample_telemetry)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_speed_vs_distance_plot_empty(self):
        """Test speed vs distance plot with empty data."""
        fig = create_speed_vs_distance_plot([])
        assert fig is not None

    def test_create_trajectory_comparison_plot_with_data(self, sample_telemetry):
        """Test trajectory comparison plot with valid data."""
        trajectories = {
            "Lap 1": sample_telemetry[:5],
            "Lap 2": sample_telemetry[5:],
        }
        fig = create_trajectory_comparison_plot(trajectories)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_trajectory_comparison_plot_empty(self):
        """Test trajectory comparison plot with empty data."""
        fig = create_trajectory_comparison_plot({})
        assert fig is not None

    def test_create_braking_analysis_plot_with_data(self, sample_telemetry):
        """Test braking analysis plot with valid data."""
        fig = create_braking_analysis_plot(sample_telemetry)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_braking_analysis_plot_insufficient_data(self):
        """Test braking analysis plot with insufficient data."""
        fig = create_braking_analysis_plot([MockCarTelemetry()])
        assert fig is not None

    def test_create_heatmap_plot_with_data(self, sample_telemetry):
        """Test heatmap plot with valid data."""
        fig = create_heatmap_plot(sample_telemetry)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_heatmap_plot_empty(self):
        """Test heatmap plot with empty data."""
        fig = create_heatmap_plot([])
        assert fig is not None

    def test_create_heatmap_plot_no_position(self):
        """Test heatmap plot with no position data."""
        telemetry = [MockCarTelemetry(position=None) for _ in range(5)]
        fig = create_heatmap_plot(telemetry)
        assert fig is not None

    def test_create_sector_times_plot_with_data(self):
        """Test sector times plot with valid data."""
        lap_data = [
            {"lap": 1, "sector1": 20.5, "sector2": 18.3, "sector3": 22.1},
            {"lap": 2, "sector1": 19.8, "sector2": 18.5, "sector3": 21.9},
        ]
        fig = create_sector_times_plot(lap_data)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_sector_times_plot_empty(self):
        """Test sector times plot with empty data."""
        fig = create_sector_times_plot([])
        assert fig is not None

    def test_create_g_force_plot_with_data(self, sample_telemetry):
        """Test G-force plot with valid data."""
        fig = create_g_force_plot(sample_telemetry)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_g_force_plot_insufficient_data(self):
        """Test G-force plot with insufficient data."""
        fig = create_g_force_plot([MockCarTelemetry()])
        assert fig is not None

    def test_plots_with_custom_titles(self, sample_telemetry):
        """Test plots with custom titles."""
        fig1 = create_speed_vs_distance_plot(sample_telemetry, title="Custom Title 1")
        assert fig1 is not None
        assert "Custom Title 1" in fig1.layout.title.text

        fig2 = create_heatmap_plot(sample_telemetry, title="Custom Title 2")
        assert fig2 is not None
        assert "Custom Title 2" in fig2.layout.title.text
