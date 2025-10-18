"""ASCII radar visualisation for OutSim telemetry."""
from __future__ import annotations

import sys
from typing import List, TextIO

from .outsim_client import OutSimFrame


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


__all__ = ["RadarRenderer"]
