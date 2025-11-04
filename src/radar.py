"""ASCII radar visualisation for OutSim telemetry."""

from __future__ import annotations

import sys
import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence, TextIO

from .outsim_client import OutSimFrame


NEAR_CONTACT_TOLERANCE = 0.5


@dataclass(frozen=True)
class RadarTarget:
    """Representation of a single radar contact relative to the player."""

    distance: float
    bearing: float
    offset_x: float
    offset_y: float


def _normalise_angle(angle: float) -> float:
    wrapped = math.fmod(angle + math.pi, 2 * math.pi)
    if wrapped < 0:
        wrapped += 2 * math.pi
    return wrapped - math.pi


def compute_radar_targets(
    player_position: Sequence[float],
    heading: float,
    other_positions: Iterable[Sequence[float]],
    *,
    max_range: float = 140.0,
) -> List[RadarTarget]:
    """Compute radar contacts ordered by increasing distance.

    Parameters
    ----------
    player_position:
        Iterable containing the player's ``x`` and ``y`` coordinates in metres.
    heading:
        Player heading expressed in radians, using the same convention as
        :meth:`OutSimFrame.yaw_pitch_roll`.
    other_positions:
        Iterable of iterable pairs describing the ``x`` and ``y`` coordinates of
        other vehicles.
    max_range:
        Maximum detection distance in metres. Contacts beyond this radius are
        discarded. Defaults to ``140.0`` which matches the overlay renderer.
        Contacts closer than ``NEAR_CONTACT_TOLERANCE`` metres are ignored to
        avoid rendering jitter from overlapping with the player's position.
    """

    if max_range <= 0:
        raise ValueError("max_range must be positive")

    try:
        player_x, player_y = float(player_position[0]), float(player_position[1])
    except (IndexError, TypeError, ValueError) as exc:  # pragma: no cover - defensive
        raise ValueError("player_position must contain at least two numeric entries") from exc

    if not (math.isfinite(player_x) and math.isfinite(player_y)):
        raise ValueError("player_position must contain finite coordinates")

    targets: List[RadarTarget] = []

    for pos in other_positions:
        try:
            other_x, other_y = float(pos[0]), float(pos[1])
        except (IndexError, TypeError, ValueError):
            continue

        if not (math.isfinite(other_x) and math.isfinite(other_y)):
            continue

        offset_x = other_x - player_x
        offset_y = other_y - player_y
        distance = math.hypot(offset_x, offset_y)

        if distance > max_range or distance <= NEAR_CONTACT_TOLERANCE:
            continue

        bearing_world = math.atan2(offset_x, offset_y)
        relative_bearing = _normalise_angle(bearing_world - heading)
        targets.append(
            RadarTarget(
                distance=distance,
                bearing=relative_bearing,
                offset_x=offset_x,
                offset_y=offset_y,
            )
        )

    targets.sort(key=lambda entry: entry.distance)
    return targets


class RadarRenderer:
    """Render a top down radar using a square ASCII grid."""

    def __init__(self, grid_size: int = 21, radius_m: float = 50.0) -> None:
        if grid_size % 2 == 0:
            raise ValueError("grid_size must be an odd number so that a centre cell exists")
        self._grid_size = grid_size
        self._half = grid_size // 2
        self._scale = radius_m / self._half if self._half else 1.0

    def render(self, frame: OutSimFrame) -> str:
        grid: List[List[str]] = [["."] * self._grid_size for _ in range(self._grid_size)]
        grid[self._half][self._half] = "O"  # origin / player car

        x, y, _ = frame.position
        col = self._half + int(round(x / self._scale))
        row = self._half - int(round(y / self._scale))
        if 0 <= row < self._grid_size and 0 <= col < self._grid_size:
            grid[row][col] = "X"

        yaw_deg, pitch_deg, roll_deg = frame.yaw_pitch_roll_degrees
        lines = [
            "Radar view (O = origin, X = current OutSim position)",
            f"Time: {frame.time_ms / 1000:.2f}s  Speed: {frame.speed * 3.6:.1f} km/h",
            f"Pos: x={x:7.2f}m y={y:7.2f}m z={frame.position[2]:7.2f}m",
            f"Orientation: yaw={yaw_deg:6.1f}° pitch={pitch_deg:6.1f}° roll={roll_deg:6.1f}°",
            "",
        ]
        for row_cells in grid:
            lines.append(" ".join(row_cells))
        return "\n".join(lines)

    def draw(self, frame: OutSimFrame, stream: TextIO = sys.stdout) -> None:
        """Clear the console and draw the radar for ``frame``."""

        stream.write("\x1b[2J\x1b[H")
        stream.write(self.render(frame))
        stream.write("\n")
        stream.flush()


__all__ = ["RadarRenderer", "RadarTarget", "compute_radar_targets"]
