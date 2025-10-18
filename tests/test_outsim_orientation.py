"""Tests for OutSim orientation calculations."""

import math
import struct
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.outsim_client import OutSimFrame
from src.radar import RadarRenderer


_OUTSIM_STRUCT = struct.Struct("<I3f3f3f3f3f")


def _build_packet(
    time_ms: int,
    ang_vel=(0.0, 0.0, 0.0),
    heading=(0.0, 1.0, 0.0),
    acceleration=(0.0, 0.0, 0.0),
    velocity=(0.0, 0.0, 0.0),
    position=(0.0, 0.0, 0.0),
) -> bytes:
    """Build a binary OutSim packet matching the legacy layout."""

    return _OUTSIM_STRUCT.pack(
        time_ms,
        *ang_vel,
        *heading,
        *acceleration,
        *velocity,
        *position,
    )


def test_heading_vector_converts_to_expected_yaw_pitch_roll() -> None:
    yaw_deg_expected = 45.0
    pitch_deg_expected = 10.0

    yaw_rad = math.radians(yaw_deg_expected)
    pitch_rad = math.radians(pitch_deg_expected)
    cos_pitch = math.cos(pitch_rad)
    heading = (
        math.sin(yaw_rad) * cos_pitch,
        math.cos(yaw_rad) * cos_pitch,
        math.sin(pitch_rad),
    )

    packet = _build_packet(1000, heading=heading)
    frame = OutSimFrame.from_packet(packet)

    yaw_deg, pitch_deg, roll_deg = frame.yaw_pitch_roll_degrees

    assert math.isclose(yaw_deg, yaw_deg_expected, abs_tol=1e-6)
    assert math.isclose(pitch_deg, pitch_deg_expected, abs_tol=1e-6)
    assert math.isclose(roll_deg, 0.0, abs_tol=1e-6)

    renderer = RadarRenderer()
    orientation_line = next(
        line for line in renderer.render(frame).splitlines() if line.startswith("Orientation:")
    )
    expected_line = (
        f"Orientation: yaw={yaw_deg_expected:6.1f}° pitch={pitch_deg_expected:6.1f}° roll={0.0:6.1f}°"
    )
    assert orientation_line == expected_line
