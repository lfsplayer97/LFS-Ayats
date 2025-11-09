"""
Unit tests for map view module.
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict
from src.visualization.map_view import (
    create_track_map,
    create_live_position_map,
    create_racing_line_map,
    create_corner_analysis_map,
    create_3d_track_map,
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


class TestMapView:
    """Test cases for map view functions."""

    @pytest.fixture
    def sample_telemetry(self):
        """Create sample telemetry data forming a simple track."""
        telemetry = []
        # Create a circular track pattern
        import math

        for i in range(20):
            angle = 2 * math.pi * i / 20
            t = MockCarTelemetry(
                timestamp=float(i),
                position={
                    "x": 100 * math.cos(angle),
                    "y": 100 * math.sin(angle),
                    "z": i * 2,
                },
                speed=15.0 + 5 * math.sin(angle),
            )
            telemetry.append(t)
        return telemetry

    def test_create_track_map_with_data(self, sample_telemetry):
        """Test track map with valid data."""
        fig = create_track_map(sample_telemetry)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_track_map_with_speed_colors(self, sample_telemetry):
        """Test track map with speed colors enabled."""
        fig = create_track_map(sample_telemetry, show_speed_colors=True)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_track_map_without_speed_colors(self, sample_telemetry):
        """Test track map without speed colors."""
        fig = create_track_map(sample_telemetry, show_speed_colors=False)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_track_map_empty(self):
        """Test track map with empty data."""
        fig = create_track_map([])
        assert fig is not None

    def test_create_track_map_no_position(self):
        """Test track map with no position data."""
        telemetry = [MockCarTelemetry(position=None) for _ in range(5)]
        fig = create_track_map(telemetry)
        assert fig is not None

    def test_create_live_position_map_with_data(self, sample_telemetry):
        """Test live position map with valid data."""
        positions = {
            1: sample_telemetry[0],
            2: sample_telemetry[5],
            3: sample_telemetry[10],
        }
        fig = create_live_position_map(positions)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_live_position_map_with_track(self, sample_telemetry):
        """Test live position map with track outline."""
        positions = {1: sample_telemetry[0]}
        fig = create_live_position_map(positions, track_data=sample_telemetry)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_live_position_map_empty(self):
        """Test live position map with no vehicles."""
        fig = create_live_position_map({})
        assert fig is not None

    def test_create_racing_line_map_with_data(self, sample_telemetry):
        """Test racing line map with valid data."""
        ideal = sample_telemetry[:10]
        current = sample_telemetry[10:]
        fig = create_racing_line_map(ideal, current)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_racing_line_map_empty(self):
        """Test racing line map with empty data."""
        fig = create_racing_line_map([], [])
        assert fig is not None

    def test_create_corner_analysis_map_with_data(self, sample_telemetry):
        """Test corner analysis map with valid data."""
        fig = create_corner_analysis_map(sample_telemetry)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_corner_analysis_map_insufficient_data(self):
        """Test corner analysis map with insufficient data."""
        telemetry = [MockCarTelemetry() for _ in range(2)]
        fig = create_corner_analysis_map(telemetry)
        assert fig is not None

    def test_create_3d_track_map_with_data(self, sample_telemetry):
        """Test 3D track map with valid data."""
        fig = create_3d_track_map(sample_telemetry)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_3d_track_map_empty(self):
        """Test 3D track map with empty data."""
        fig = create_3d_track_map([])
        assert fig is not None

    def test_map_custom_heights(self, sample_telemetry):
        """Test maps with custom heights."""
        fig1 = create_track_map(sample_telemetry, height=800)
        assert fig1 is not None
        assert fig1.layout.height == 800

        fig2 = create_3d_track_map(sample_telemetry, height=700)
        assert fig2 is not None
        assert fig2.layout.height == 700
