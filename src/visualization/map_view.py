"""
Map View Module
2D/3D track map visualization with vehicle positions.

Reference: https://plotly.com/python/
"""

import plotly.graph_objects as go
from typing import List, Dict, Optional
import numpy as np
from src.telemetry.collector import CarTelemetry


def create_track_map(
    telemetry_list: List[CarTelemetry],
    title: str = "Track Map",
    show_speed_colors: bool = True,
    height: int = 600,
) -> go.Figure:
    """
    Create a 2D track map from telemetry data.

    Args:
        telemetry_list: List of CarTelemetry objects defining the track
        title: Map title
        show_speed_colors: Color the track by speed
        height: Map height in pixels

    Returns:
        Plotly Figure with track map

    Example:
        >>> telemetry = collector.get_telemetry_history(plid=1)
        >>> fig = create_track_map(telemetry)
        >>> fig.show()
    """
    if not telemetry_list:
        fig = go.Figure()
        fig.add_annotation(
            text="No telemetry data for track map",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=height)
        return fig

    # Extract positions
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
        fig.update_layout(title=title, height=height)
        return fig

    fig = go.Figure()

    if show_speed_colors:
        # Color-coded track line by speed
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_coords,
                mode="lines+markers",
                marker=dict(
                    size=4,
                    color=speeds_kmh,
                    colorscale="Jet",
                    showscale=True,
                    colorbar=dict(title="Speed<br>(km/h)", x=1.02),
                    line=dict(width=0.5, color="white"),
                ),
                line=dict(width=0, color="rgba(0,0,0,0)"),
                text=[f"{s:.1f} km/h" for s in speeds_kmh],
                hovertemplate="X: %{x:.0f}<br>Y: %{y:.0f}<br>%{text}<extra></extra>",
                name="Track",
            )
        )
    else:
        # Simple track line
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_coords,
                mode="lines",
                line=dict(color="darkblue", width=3),
                name="Track",
            )
        )

    # Mark start/finish
    if len(x_coords) > 0:
        fig.add_trace(
            go.Scatter(
                x=[x_coords[0]],
                y=[y_coords[0]],
                mode="markers+text",
                marker=dict(size=15, color="green", symbol="square"),
                text=["START"],
                textposition="top center",
                name="Start/Finish",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="X Position (m)",
        yaxis_title="Y Position (m)",
        height=height,
        template="plotly_white",
        margin=dict(l=60, r=100, t=60, b=60),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        hovermode="closest",
    )

    return fig


def create_live_position_map(
    vehicle_positions: Dict[int, CarTelemetry],
    track_data: Optional[List[CarTelemetry]] = None,
    title: str = "Live Vehicle Positions",
    height: int = 600,
) -> go.Figure:
    """
    Create a live map showing current vehicle positions.

    Args:
        vehicle_positions: Dict mapping player IDs to current CarTelemetry
        track_data: Optional track outline from previous lap
        title: Map title
        height: Map height in pixels

    Returns:
        Plotly Figure with live positions

    Example:
        >>> positions = collector.get_latest_telemetry()
        >>> fig = create_live_position_map(positions)
        >>> fig.show()
    """
    fig = go.Figure()

    # Draw track outline if provided
    if track_data:
        x_coords = []
        y_coords = []
        for t in track_data:
            if t.position:
                x_coords.append(t.position.get("x", 0))
                y_coords.append(t.position.get("y", 0))

        if x_coords:
            fig.add_trace(
                go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode="lines",
                    line=dict(color="lightgray", width=2, dash="dash"),
                    name="Track",
                    showlegend=True,
                )
            )

    # Plot vehicle positions
    if vehicle_positions:
        for plid, telemetry in vehicle_positions.items():
            if telemetry.position:
                x = telemetry.position.get("x", 0)
                y = telemetry.position.get("y", 0)
                speed_kmh = telemetry.speed * 3.6

                fig.add_trace(
                    go.Scatter(
                        x=[x],
                        y=[y],
                        mode="markers+text",
                        marker=dict(
                            size=15,
                            color=speed_kmh,
                            colorscale="Viridis",
                            showscale=True,
                            colorbar=dict(title="Speed<br>(km/h)", x=1.02),
                            line=dict(width=2, color="white"),
                        ),
                        text=[f"P{plid}"],
                        textposition="top center",
                        name=f"Player {plid}",
                        hovertemplate=(
                            f"Player {plid}<br>X: {x:.0f}<br>Y: {y:.0f}<br>"
                            f"Speed: {speed_kmh:.1f} km/h<extra></extra>"
                        ),
                    )
                )
    else:
        fig.add_annotation(
            text="No vehicles detected",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )

    fig.update_layout(
        title=title,
        xaxis_title="X Position (m)",
        yaxis_title="Y Position (m)",
        height=height,
        template="plotly_white",
        margin=dict(l=60, r=100, t=60, b=60),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        hovermode="closest",
    )

    return fig


def create_racing_line_map(
    ideal_line: List[CarTelemetry],
    current_line: List[CarTelemetry],
    title: str = "Racing Line Comparison",
    height: int = 600,
) -> go.Figure:
    """
    Compare ideal racing line vs current trajectory.

    Args:
        ideal_line: Telemetry for ideal/reference lap
        current_line: Telemetry for current lap
        title: Map title
        height: Map height in pixels

    Returns:
        Plotly Figure comparing racing lines

    Example:
        >>> ideal = collector.get_telemetry_history(plid=1, limit=500)
        >>> current = collector.get_telemetry_history(plid=2, limit=500)
        >>> fig = create_racing_line_map(ideal, current)
        >>> fig.show()
    """
    fig = go.Figure()

    # Plot ideal line
    if ideal_line:
        x_coords = []
        y_coords = []
        for t in ideal_line:
            if t.position:
                x_coords.append(t.position.get("x", 0))
                y_coords.append(t.position.get("y", 0))

        if x_coords:
            fig.add_trace(
                go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode="lines",
                    line=dict(color="green", width=3, dash="dot"),
                    name="Ideal Line",
                )
            )

    # Plot current line
    if current_line:
        x_coords = []
        y_coords = []
        for t in current_line:
            if t.position:
                x_coords.append(t.position.get("x", 0))
                y_coords.append(t.position.get("y", 0))

        if x_coords:
            fig.add_trace(
                go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode="lines",
                    line=dict(color="red", width=2),
                    name="Current Line",
                )
            )

    if not ideal_line and not current_line:
        fig.add_annotation(
            text="No racing line data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )

    fig.update_layout(
        title=title,
        xaxis_title="X Position (m)",
        yaxis_title="Y Position (m)",
        height=height,
        template="plotly_white",
        margin=dict(l=60, r=30, t=60, b=60),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        hovermode="closest",
    )

    return fig


def create_corner_analysis_map(
    telemetry_list: List[CarTelemetry],
    corner_threshold: float = 0.3,
    title: str = "Corner Analysis",
    height: int = 600,
) -> go.Figure:
    """
    Create a map highlighting corners and braking zones.

    Args:
        telemetry_list: List of CarTelemetry objects
        corner_threshold: Threshold for detecting corners (based on direction change)
        title: Map title
        height: Map height in pixels

    Returns:
        Plotly Figure with corner analysis

    Example:
        >>> telemetry = collector.get_telemetry_history(plid=1)
        >>> fig = create_corner_analysis_map(telemetry)
        >>> fig.show()
    """
    if not telemetry_list or len(telemetry_list) < 3:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for corner analysis",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=height)
        return fig

    # Extract data
    x_coords = []
    y_coords = []
    speeds_kmh = []
    is_braking = []

    for i in range(len(telemetry_list)):
        t = telemetry_list[i]
        if t.position:
            x_coords.append(t.position.get("x", 0))
            y_coords.append(t.position.get("y", 0))
            speeds_kmh.append(t.speed * 3.6)

            # Detect braking (speed decreasing)
            if i > 0:
                prev_speed = telemetry_list[i - 1].speed * 3.6
                curr_speed = t.speed * 3.6
                is_braking.append(curr_speed < prev_speed - 2)  # 2 km/h threshold
            else:
                is_braking.append(False)

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
        fig.update_layout(title=title, height=height)
        return fig

    fig = go.Figure()

    # Draw base track
    fig.add_trace(
        go.Scatter(
            x=x_coords,
            y=y_coords,
            mode="lines",
            line=dict(color="lightgray", width=5),
            name="Track",
            showlegend=False,
        )
    )

    # Highlight braking zones
    braking_x = [x_coords[i] for i in range(len(is_braking)) if is_braking[i]]
    braking_y = [y_coords[i] for i in range(len(is_braking)) if is_braking[i]]

    if braking_x:
        fig.add_trace(
            go.Scatter(
                x=braking_x,
                y=braking_y,
                mode="markers",
                marker=dict(size=8, color="red", symbol="circle"),
                name="Braking Zones",
            )
        )

    # Highlight slow corners (speed < threshold)
    speed_threshold = np.mean(speeds_kmh) * 0.6  # 60% of average speed
    corner_x = [
        x_coords[i] for i in range(len(speeds_kmh)) if speeds_kmh[i] < speed_threshold
    ]
    corner_y = [
        y_coords[i] for i in range(len(speeds_kmh)) if speeds_kmh[i] < speed_threshold
    ]

    if corner_x:
        fig.add_trace(
            go.Scatter(
                x=corner_x,
                y=corner_y,
                mode="markers",
                marker=dict(size=6, color="orange", symbol="circle", opacity=0.6),
                name="Slow Corners",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="X Position (m)",
        yaxis_title="Y Position (m)",
        height=height,
        template="plotly_white",
        margin=dict(l=60, r=30, t=60, b=60),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        hovermode="closest",
    )

    return fig


def create_3d_track_map(
    telemetry_list: List[CarTelemetry],
    title: str = "3D Track Map",
    height: int = 700,
) -> go.Figure:
    """
    Create a 3D track map (if Z-coordinate data is available).

    Args:
        telemetry_list: List of CarTelemetry objects
        title: Map title
        height: Map height in pixels

    Returns:
        Plotly Figure with 3D track map

    Example:
        >>> telemetry = collector.get_telemetry_history(plid=1)
        >>> fig = create_3d_track_map(telemetry)
        >>> fig.show()
    """
    if not telemetry_list:
        fig = go.Figure()
        fig.add_annotation(
            text="No telemetry data for 3D map",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(title=title, height=height)
        return fig

    # Extract 3D positions
    x_coords = []
    y_coords = []
    z_coords = []
    speeds_kmh = []

    for t in telemetry_list:
        if t.position:
            x_coords.append(t.position.get("x", 0))
            y_coords.append(t.position.get("y", 0))
            z_coords.append(t.position.get("z", 0))
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
        fig.update_layout(title=title, height=height)
        return fig

    fig = go.Figure()

    # 3D scatter plot colored by speed
    fig.add_trace(
        go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode="lines+markers",
            marker=dict(
                size=3,
                color=speeds_kmh,
                colorscale="Jet",
                showscale=True,
                colorbar=dict(title="Speed<br>(km/h)", x=1.02),
            ),
            line=dict(color="darkblue", width=2),
            text=[f"{s:.1f} km/h" for s in speeds_kmh],
            hovertemplate="X: %{x:.0f}<br>Y: %{y:.0f}<br>Z: %{z:.0f}<br>%{text}<extra></extra>",
            name="Track",
        )
    )

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            zaxis_title="Z Position (m)",
            aspectmode="data",
        ),
        height=height,
        margin=dict(l=0, r=0, t=50, b=0),
    )

    return fig
