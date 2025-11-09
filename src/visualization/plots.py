"""
Plots Module
Functions for creating telemetry analysis plots.

Reference: https://plotly.com/python/
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from src.telemetry.collector import CarTelemetry


def create_speed_vs_distance_plot(
    telemetry_list: List[CarTelemetry], title: str = "Speed vs Distance"
) -> go.Figure:
    """
    Create a plot of speed versus distance traveled.

    Args:
        telemetry_list: List of CarTelemetry objects
        title: Plot title

    Returns:
        Plotly Figure

    Example:
        >>> from src.telemetry import TelemetryCollector
        >>> collector = TelemetryCollector(client)
        >>> telemetry = collector.get_telemetry_history(plid=1)
        >>> fig = create_speed_vs_distance_plot(telemetry)
        >>> fig.show()
    """
    if not telemetry_list:
        fig = go.Figure()
        fig.add_annotation(
            text="No telemetry data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=400)
        return fig

    # Calculate cumulative distance
    distances = [0.0]
    speeds_kmh = [telemetry_list[0].speed * 3.6]

    for i in range(1, len(telemetry_list)):
        prev = telemetry_list[i - 1]
        curr = telemetry_list[i]

        # Calculate distance between points
        if prev.position and curr.position:
            dx = curr.position.get("x", 0) - prev.position.get("x", 0)
            dy = curr.position.get("y", 0) - prev.position.get("y", 0)
            distance = np.sqrt(dx**2 + dy**2)
            distances.append(distances[-1] + distance)
            speeds_kmh.append(curr.speed * 3.6)
        else:
            distances.append(distances[-1])
            speeds_kmh.append(curr.speed * 3.6)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=distances,
            y=speeds_kmh,
            mode="lines",
            name="Speed",
            line=dict(color="royalblue", width=2),
            fill="tozeroy",
            fillcolor="rgba(65, 105, 225, 0.3)",
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
    )

    return fig


def create_trajectory_comparison_plot(
    trajectories: Dict[str, List[CarTelemetry]], title: str = "Trajectory Comparison"
) -> go.Figure:
    """
    Create a plot comparing multiple vehicle trajectories.

    Args:
        trajectories: Dict mapping names to lists of CarTelemetry
        title: Plot title

    Returns:
        Plotly Figure

    Example:
        >>> trajectories = {
        ...     "Lap 1": collector.get_telemetry_history(plid=1, limit=100),
        ...     "Lap 2": collector.get_telemetry_history(plid=1, limit=100)
        ... }
        >>> fig = create_trajectory_comparison_plot(trajectories)
        >>> fig.show()
    """
    if not trajectories:
        fig = go.Figure()
        fig.add_annotation(
            text="No trajectory data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=500)
        return fig

    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, (name, telemetry_list) in enumerate(trajectories.items()):
        if not telemetry_list:
            continue

        x_coords = []
        y_coords = []
        for t in telemetry_list:
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

            # Mark start point
            fig.add_trace(
                go.Scatter(
                    x=[x_coords[0]],
                    y=[y_coords[0]],
                    mode="markers",
                    name=f"{name} Start",
                    marker=dict(
                        size=10, color=colors[idx % len(colors)], symbol="circle"
                    ),
                    showlegend=False,
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="X Position",
        yaxis_title="Y Position",
        height=500,
        template="plotly_white",
        margin=dict(l=60, r=30, t=60, b=60),
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    return fig


def create_braking_analysis_plot(
    telemetry_list: List[CarTelemetry], title: str = "Braking Analysis"
) -> go.Figure:
    """
    Create a plot analyzing braking zones based on speed changes.

    Args:
        telemetry_list: List of CarTelemetry objects
        title: Plot title

    Returns:
        Plotly Figure

    Example:
        >>> telemetry = collector.get_telemetry_history(plid=1)
        >>> fig = create_braking_analysis_plot(telemetry)
        >>> fig.show()
    """
    if not telemetry_list or len(telemetry_list) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for braking analysis",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=400)
        return fig

    # Calculate acceleration/deceleration
    times = [t.timestamp for t in telemetry_list]
    speeds_kmh = [t.speed * 3.6 for t in telemetry_list]

    # Calculate acceleration (change in speed per second)
    accelerations = []
    for i in range(1, len(telemetry_list)):
        dt = times[i] - times[i - 1]
        if dt > 0:
            dv = speeds_kmh[i] - speeds_kmh[i - 1]
            accel = dv / dt  # km/h per second
            accelerations.append(accel)
        else:
            accelerations.append(0)
    accelerations.insert(0, 0)  # First point has no acceleration

    # Create figure with secondary y-axis
    fig = go.Figure()

    # Speed trace
    fig.add_trace(
        go.Scatter(
            x=times,
            y=speeds_kmh,
            mode="lines",
            name="Speed",
            line=dict(color="blue", width=2),
            yaxis="y1",
        )
    )

    # Acceleration trace with color based on braking/accelerating
    colors = ["red" if a < -5 else "green" if a > 5 else "gray" for a in accelerations]

    fig.add_trace(
        go.Bar(
            x=times,
            y=accelerations,
            name="Acceleration",
            marker_color=colors,
            yaxis="y2",
            opacity=0.6,
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis=dict(title="Speed (km/h)", side="left"),
        yaxis2=dict(
            title="Acceleration (km/h/s)",
            side="right",
            overlaying="y",
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=1,
        ),
        height=450,
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=60, r=60, t=60, b=60),
        legend=dict(x=0.02, y=0.98),
    )

    return fig


def create_heatmap_plot(
    telemetry_list: List[CarTelemetry], title: str = "Track Speed Heatmap"
) -> go.Figure:
    """
    Create a heatmap of speed over the track surface.

    Args:
        telemetry_list: List of CarTelemetry objects
        title: Plot title

    Returns:
        Plotly Figure

    Example:
        >>> telemetry = collector.get_telemetry_history(plid=1)
        >>> fig = create_heatmap_plot(telemetry)
        >>> fig.show()
    """
    if not telemetry_list:
        fig = go.Figure()
        fig.add_annotation(
            text="No data for heatmap",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=500)
        return fig

    # Extract position and speed data
    x_coords = []
    y_coords = []
    speeds_kmh = []

    for t in telemetry_list:
        if t.position:
            x_coords.append(t.position.get("x", 0))
            y_coords.append(t.position.get("y", 0))
            speeds_kmh.append(t.speed * 3.6)

    if not x_coords:
        fig = go.Figure()
        fig.add_annotation(
            text="No position data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=500)
        return fig

    fig = go.Figure()

    # Create scatter plot with color based on speed
    fig.add_trace(
        go.Scatter(
            x=x_coords,
            y=y_coords,
            mode="markers",
            marker=dict(
                size=8,
                color=speeds_kmh,
                colorscale="Jet",  # Blue (slow) to red (fast)
                showscale=True,
                colorbar=dict(title="Speed<br>(km/h)", x=1.02),
                line=dict(width=0.5, color="white"),
            ),
            text=[f"{s:.1f} km/h" for s in speeds_kmh],
            hovertemplate="X: %{x}<br>Y: %{y}<br>%{text}<extra></extra>",
            name="Speed",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="X Position",
        yaxis_title="Y Position",
        height=500,
        template="plotly_white",
        margin=dict(l=60, r=100, t=60, b=60),
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    return fig


def create_sector_times_plot(
    lap_data: List[Dict[str, Any]], title: str = "Sector Times"
) -> go.Figure:
    """
    Create a grouped bar chart for sector times comparison.

    Args:
        lap_data: List of dicts with lap and sector time data
        title: Plot title

    Returns:
        Plotly Figure

    Example:
        >>> lap_data = [
        ...     {'lap': 1, 'sector1': 20.5, 'sector2': 18.3, 'sector3': 22.1},
        ...     {'lap': 2, 'sector1': 19.8, 'sector2': 18.5, 'sector3': 21.9}
        ... ]
        >>> fig = create_sector_times_plot(lap_data)
        >>> fig.show()
    """
    if not lap_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No sector data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=400)
        return fig

    df = pd.DataFrame(lap_data)
    fig = go.Figure()

    # Find sector columns
    sector_cols = [col for col in df.columns if col.startswith("sector")]
    colors = ["#3498db", "#2ecc71", "#e74c3c"]

    for idx, sector in enumerate(sector_cols):
        if sector in df.columns:
            fig.add_trace(
                go.Bar(
                    x=df["lap"] if "lap" in df else df.index,
                    y=df[sector],
                    name=sector.replace("sector", "Sector "),
                    marker_color=colors[idx % len(colors)],
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="Lap",
        yaxis_title="Time (s)",
        height=400,
        barmode="group",
        template="plotly_white",
        margin=dict(l=60, r=30, t=60, b=60),
    )

    return fig


def create_g_force_plot(
    telemetry_list: List[CarTelemetry], title: str = "G-Force Analysis"
) -> go.Figure:
    """
    Create a plot showing estimated G-forces during a lap.

    Args:
        telemetry_list: List of CarTelemetry objects
        title: Plot title

    Returns:
        Plotly Figure

    Note:
        This is an approximation based on speed changes and direction changes.
        Actual G-force would require acceleration data from IS_MCI packet.

    Example:
        >>> telemetry = collector.get_telemetry_history(plid=1)
        >>> fig = create_g_force_plot(telemetry)
        >>> fig.show()
    """
    if not telemetry_list or len(telemetry_list) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for G-force analysis",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=400)
        return fig

    # Approximate G-force calculation
    times = [t.timestamp for t in telemetry_list]
    lateral_g = []
    longitudinal_g = []

    for i in range(1, len(telemetry_list)):
        dt = times[i] - times[i - 1]
        if dt > 0:
            # Longitudinal G (acceleration/braking)
            dv = telemetry_list[i].speed - telemetry_list[i - 1].speed
            long_g = (dv / dt) / 9.81  # Convert to G units
            longitudinal_g.append(long_g)

            # Lateral G (cornering) - simplified using direction change
            # This is a rough approximation
            lateral_g.append(
                0
            )  # Would need proper calculation from actual acceleration data
        else:
            longitudinal_g.append(0)
            lateral_g.append(0)

    longitudinal_g.insert(0, 0)
    lateral_g.insert(0, 0)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=times,
            y=longitudinal_g,
            mode="lines",
            name="Longitudinal G",
            line=dict(color="blue", width=2),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title="G-Force",
        height=400,
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=60, r=30, t=60, b=60),
        shapes=[
            # Add reference lines for G-force limits
            dict(
                type="line",
                x0=min(times),
                x1=max(times),
                y0=0,
                y1=0,
                line=dict(color="black", width=1, dash="dash"),
            )
        ],
    )

    return fig
