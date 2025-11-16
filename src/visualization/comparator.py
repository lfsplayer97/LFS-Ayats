"""
Lap Comparator Module
System for comparing multiple laps simultaneously.

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
from src.telemetry.collector import CarTelemetry


@dataclass
class LapComparison:
    """
    Results of lap comparison analysis.

    Attributes:
        lap_names: Names/identifiers for each lap
        time_differences: Time differences per segment
        faster_lap: Index of faster lap
        total_time_diff: Total time difference
        sector_diffs: Sector-by-sector differences
    """

    lap_names: List[str]
    time_differences: List[float]
    faster_lap: int
    total_time_diff: float
    sector_diffs: Dict[str, float]


class LapComparator:
    """
    Compare multiple laps for performance analysis.

    This class provides tools to:
    - Compare lap times and sector times
    - Analyze speed differences at specific points
    - Identify where time is gained/lost
    - Visualize lap comparisons

    Example:
        >>> comparator = LapComparator()
        >>> lap1 = collector.get_telemetry_history(plid=1, limit=500)
        >>> lap2 = collector.get_telemetry_history(plid=1, limit=500)
        >>> comparison = comparator.compare_laps(lap1, lap2)
        >>> fig = comparator.create_comparison_plot([lap1, lap2])
        >>> fig.show()
    """

    def __init__(self):
        """Initialize the lap comparator."""
        self.laps: Dict[str, List[CarTelemetry]] = {}

    def add_lap(self, lap_name: str, telemetry_list: List[CarTelemetry]) -> None:
        """
        Add a lap for comparison.

        Args:
            lap_name: Identifier for the lap (e.g., "Lap 1", "Best Lap")
            telemetry_list: Telemetry data for the lap
        """
        self.laps[lap_name] = telemetry_list

    def remove_lap(self, lap_name: str) -> None:
        """
        Remove a lap from comparison.

        Args:
            lap_name: Name of the lap to remove
        """
        if lap_name in self.laps:
            del self.laps[lap_name]

    def clear_laps(self) -> None:
        """Clear all stored laps."""
        self.laps.clear()

    def compare_laps(
        self, lap1: List[CarTelemetry], lap2: List[CarTelemetry]
    ) -> Optional[LapComparison]:
        """
        Compare two laps and calculate differences.

        Args:
            lap1: Telemetry for first lap
            lap2: Telemetry for second lap

        Returns:
            LapComparison object with analysis results, or None if comparison not possible

        Example:
            >>> comparison = comparator.compare_laps(lap1, lap2)
            >>> print(f"Time difference: {comparison.total_time_diff:.2f}s")
        """
        if not lap1 or not lap2:
            return None

        # Calculate lap times
        lap1_time = lap1[-1].timestamp - lap1[0].timestamp if len(lap1) > 1 else 0
        lap2_time = lap2[-1].timestamp - lap2[0].timestamp if len(lap2) > 1 else 0

        total_diff = lap2_time - lap1_time
        faster_lap = 0 if lap1_time < lap2_time else 1

        # Calculate sector differences (simplified - divide lap into 3 sectors)
        sector_diffs = {}
        for sector in range(3):
            start_idx1 = int(len(lap1) * sector / 3)
            end_idx1 = int(len(lap1) * (sector + 1) / 3)
            start_idx2 = int(len(lap2) * sector / 3)
            end_idx2 = int(len(lap2) * (sector + 1) / 3)

            if end_idx1 > start_idx1 and end_idx2 > start_idx2:
                sector1_time = lap1[end_idx1 - 1].timestamp - lap1[start_idx1].timestamp
                sector2_time = lap2[end_idx2 - 1].timestamp - lap2[start_idx2].timestamp
                sector_diffs[f"sector{sector+1}"] = sector2_time - sector1_time

        return LapComparison(
            lap_names=["Lap 1", "Lap 2"],
            time_differences=[0, total_diff],
            faster_lap=faster_lap,
            total_time_diff=abs(total_diff),
            sector_diffs=sector_diffs,
        )

    def create_comparison_plot(
        self,
        laps: Optional[List[List[CarTelemetry]]] = None,
        lap_names: Optional[List[str]] = None,
        title: str = "Lap Comparison - Speed",
    ) -> go.Figure:
        """
        Create a comparison plot showing speed profiles for multiple laps.

        Args:
            laps: List of telemetry lists to compare (None = use stored laps)
            lap_names: Names for each lap (None = auto-generate)
            title: Plot title

        Returns:
            Plotly Figure with comparison

        Example:
            >>> fig = comparator.create_comparison_plot([lap1, lap2], ["Lap 1", "Lap 2"])
            >>> fig.show()
        """
        if laps is None:
            laps = list(self.laps.values())
            lap_names = list(self.laps.keys())
        elif lap_names is None:
            lap_names = [f"Lap {i+1}" for i in range(len(laps))]

        if not laps:
            fig = go.Figure()
            fig.add_annotation(
                text="No laps to compare",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=20, color="gray"),
            )
            fig.update_layout(title=title, height=400)
            return fig

        fig = go.Figure()
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]

        for idx, (lap, name) in enumerate(zip(laps, lap_names)):
            if not lap:
                continue

            # Calculate distances
            distances = [0.0]
            speeds_kmh = [lap[0].speed * 3.6]

            for i in range(1, len(lap)):
                if lap[i].position and lap[i - 1].position:
                    dx = lap[i].position.get("x", 0) - lap[i - 1].position.get("x", 0)
                    dy = lap[i].position.get("y", 0) - lap[i - 1].position.get("y", 0)
                    dist = np.sqrt(dx**2 + dy**2)
                    distances.append(distances[-1] + dist)
                else:
                    distances.append(distances[-1])
                speeds_kmh.append(lap[i].speed * 3.6)

            fig.add_trace(
                go.Scatter(
                    x=distances,
                    y=speeds_kmh,
                    mode="lines",
                    name=name,
                    line=dict(color=colors[idx % len(colors)], width=2),
                )
            )

        fig.update_layout(
            title=title,
            xaxis_title="Distance (m)",
            yaxis_title="Speed (km/h)",
            height=450,
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=60, r=30, t=60, b=60),
            legend=dict(x=0.02, y=0.98),
        )

        return fig

    def create_time_delta_plot(
        self,
        lap1: List[CarTelemetry],
        lap2: List[CarTelemetry],
        title: str = "Time Delta",
    ) -> go.Figure:
        """
        Create a plot showing cumulative time difference between two laps.

        Args:
            lap1: Reference lap (baseline)
            lap2: Comparison lap
            title: Plot title

        Returns:
            Plotly Figure showing time delta

        Example:
            >>> fig = comparator.create_time_delta_plot(best_lap, current_lap)
            >>> fig.show()
        """
        if not lap1 or not lap2:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for time delta",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=20, color="gray"),
            )
            fig.update_layout(title=title, height=400)
            return fig

        # Normalize both laps to same number of points for comparison
        num_points = min(len(lap1), len(lap2))

        # Calculate distances for lap1
        distances = [0.0]
        for i in range(1, num_points):
            if lap1[i].position and lap1[i - 1].position:
                dx = lap1[i].position.get("x", 0) - lap1[i - 1].position.get("x", 0)
                dy = lap1[i].position.get("y", 0) - lap1[i - 1].position.get("y", 0)
                dist = np.sqrt(dx**2 + dy**2)
                distances.append(distances[-1] + dist)
            else:
                distances.append(distances[-1])

        # Calculate time deltas
        time_deltas = []
        for i in range(num_points):
            # Time elapsed at this point
            time1 = lap1[i].timestamp - lap1[0].timestamp
            time2 = lap2[i].timestamp - lap2[0].timestamp
            delta = time2 - time1  # Positive = lap2 is slower
            time_deltas.append(delta)

        fig = go.Figure()

        # Create time delta trace with color based on sign
        ["red" if d > 0 else "green" for d in time_deltas]

        fig.add_trace(
            go.Scatter(
                x=distances[:num_points],
                y=time_deltas,
                mode="lines",
                name="Time Delta",
                line=dict(color="blue", width=2),
                fill="tozeroy",
                fillcolor="rgba(65, 105, 225, 0.3)",
            )
        )

        # Add zero line
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="black",
            annotation_text="Even",
            annotation_position="right",
        )

        fig.update_layout(
            title=title,
            xaxis_title="Distance (m)",
            yaxis_title="Time Delta (s)",
            height=400,
            hovermode="x unified",
            template="plotly_white",
            margin=dict(l=60, r=30, t=60, b=60),
            annotations=[
                dict(
                    text="<b>Green</b>: Lap 1 faster | <b>Red</b>: Lap 2 faster",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=-0.15,
                    showarrow=False,
                    font=dict(size=12),
                )
            ],
        )

        return fig

    def create_sector_comparison(
        self, laps: Optional[Dict[str, List[CarTelemetry]]] = None
    ) -> go.Figure:
        """
        Create a bar chart comparing sector times across laps.

        Args:
            laps: Dict of lap names to telemetry (None = use stored laps)

        Returns:
            Plotly Figure with sector comparison

        Example:
            >>> laps = {"Lap 1": lap1_data, "Lap 2": lap2_data}
            >>> fig = comparator.create_sector_comparison(laps)
            >>> fig.show()
        """
        if laps is None:
            laps = self.laps

        if not laps:
            fig = go.Figure()
            fig.add_annotation(
                text="No laps for sector comparison",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=20, color="gray"),
            )
            fig.update_layout(title="Sector Comparison", height=400)
            return fig

        fig = go.Figure()

        # Calculate sector times for each lap (divide into 3 sectors)
        sector_data = []
        for lap_name, telemetry in laps.items():
            if not telemetry or len(telemetry) < 3:
                continue

            for sector in range(3):
                start_idx = int(len(telemetry) * sector / 3)
                end_idx = int(len(telemetry) * (sector + 1) / 3)

                if end_idx > start_idx:
                    sector_time = (
                        telemetry[end_idx - 1].timestamp
                        - telemetry[start_idx].timestamp
                    )
                    sector_data.append(
                        {
                            "lap": lap_name,
                            "sector": f"Sector {sector+1}",
                            "time": sector_time,
                        }
                    )

        if not sector_data:
            fig.add_annotation(
                text="Insufficient data for sector comparison",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=20, color="gray"),
            )
            fig.update_layout(title="Sector Comparison", height=400)
            return fig

        df = pd.DataFrame(sector_data)

        # Create grouped bar chart
        for sector in ["Sector 1", "Sector 2", "Sector 3"]:
            sector_df = df[df["sector"] == sector]
            fig.add_trace(
                go.Bar(
                    x=sector_df["lap"],
                    y=sector_df["time"],
                    name=sector,
                    text=sector_df["time"].round(2),
                    textposition="outside",
                )
            )

        fig.update_layout(
            title="Sector Time Comparison",
            xaxis_title="Lap",
            yaxis_title="Time (s)",
            height=400,
            barmode="group",
            template="plotly_white",
            margin=dict(l=60, r=30, t=60, b=60),
        )

        return fig

    def create_trajectory_overlay(
        self,
        laps: Optional[List[List[CarTelemetry]]] = None,
        lap_names: Optional[List[str]] = None,
    ) -> go.Figure:
        """
        Create an overlay of multiple lap trajectories.

        Args:
            laps: List of telemetry lists (None = use stored laps)
            lap_names: Names for each lap (None = auto-generate)

        Returns:
            Plotly Figure with overlaid trajectories

        Example:
            >>> fig = comparator.create_trajectory_overlay([lap1, lap2], ["Best", "Current"])
            >>> fig.show()
        """
        if laps is None:
            laps = list(self.laps.values())
            lap_names = list(self.laps.keys())
        elif lap_names is None:
            lap_names = [f"Lap {i+1}" for i in range(len(laps))]

        if not laps:
            fig = go.Figure()
            fig.add_annotation(
                text="No laps to overlay",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=20, color="gray"),
            )
            fig.update_layout(title="Trajectory Overlay", height=500)
            return fig

        fig = go.Figure()
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]

        for idx, (lap, name) in enumerate(zip(laps, lap_names)):
            if not lap:
                continue

            x_coords = []
            y_coords = []
            for t in lap:
                if t.position:
                    x_coords.append(t.position.get("x", 0))
                    y_coords.append(t.position.get("y", 0))

            if x_coords:
                fig.add_trace(
                    go.Scatter(
                        x=x_coords,
                        y=y_coords,
                        mode="lines",
                        name=name,
                        line=dict(color=colors[idx % len(colors)], width=2),
                    )
                )

        fig.update_layout(
            title="Trajectory Overlay",
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            height=500,
            template="plotly_white",
            margin=dict(l=60, r=30, t=60, b=60),
            yaxis=dict(scaleanchor="x", scaleratio=1),
            legend=dict(x=0.02, y=0.98),
        )

        return fig

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored laps.

        Returns:
            Dict with statistics

        Example:
            >>> stats = comparator.get_statistics()
            >>> print(f"Laps stored: {stats['num_laps']}")
        """
        stats = {
            "num_laps": len(self.laps),
            "lap_names": list(self.laps.keys()),
            "lap_lengths": {
                name: len(telemetry) for name, telemetry in self.laps.items()
            },
        }

        # Calculate lap times if available
        lap_times = {}
        for name, telemetry in self.laps.items():
            if len(telemetry) > 1:
                lap_time = telemetry[-1].timestamp - telemetry[0].timestamp
                lap_times[name] = lap_time

        if lap_times:
            stats["lap_times"] = lap_times
            stats["fastest_lap"] = min(lap_times, key=lap_times.get)
            stats["slowest_lap"] = max(lap_times, key=lap_times.get)

        return stats
