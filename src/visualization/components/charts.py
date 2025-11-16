"""
Charts Component
Standardized charts for telemetry data visualization.

Reference: https://plotly.com/python/
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import pandas as pd


def create_speed_chart(
    telemetry_data: List[Dict[str, Any]],
    title: str = "Speed Over Time",
    height: int = 400,
) -> go.Figure:
    """
    Create a line chart showing speed over time.

    Args:
        telemetry_data: List of telemetry dicts with 'timestamp' and 'speed'
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure with speed chart

    Example:
        >>> data = [{'timestamp': 1.0, 'speed': 50}, {'timestamp': 2.0, 'speed': 75}]
        >>> fig = create_speed_chart(data)
        >>> fig.show()
    """
    if not telemetry_data:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(height=height, title=title)
        return fig

    df = pd.DataFrame(telemetry_data)

    # Convert speed from m/s to km/h if needed
    if "speed" in df.columns:
        # Assume speed is in m/s, convert to km/h
        df["speed_kmh"] = df["speed"] * 3.6

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"] if "timestamp" in df else df.index,
            y=df["speed_kmh"] if "speed_kmh" in df else df["speed"],
            mode="lines",
            name="Speed",
            line=dict(color="royalblue", width=2),
            fill="tozeroy",
            fillcolor="rgba(65, 105, 225, 0.2)",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title="Speed (km/h)",
        height=height,
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=50, r=20, t=50, b=50),
    )

    return fig


def create_position_chart(
    telemetry_data: List[Dict[str, Any]],
    title: str = "Track Position",
    height: int = 500,
) -> go.Figure:
    """
    Create a 2D scatter plot showing vehicle position on track.

    Args:
        telemetry_data: List of telemetry dicts with 'position' containing x, y
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure with position chart

    Example:
        >>> data = [{'position': {'x': 100, 'y': 200}}, {'position': {'x': 110, 'y': 210}}]
        >>> fig = create_position_chart(data)
        >>> fig.show()
    """
    if not telemetry_data:
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
        fig.update_layout(height=height, title=title)
        return fig

    # Extract positions
    x_coords = []
    y_coords = []
    for data in telemetry_data:
        if "position" in data and isinstance(data["position"], dict):
            x_coords.append(data["position"].get("x", 0))
            y_coords.append(data["position"].get("y", 0))

    if not x_coords:
        fig = go.Figure()
        fig.add_annotation(
            text="No valid position data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(height=height, title=title)
        return fig

    fig = go.Figure()

    # Plot trajectory line
    fig.add_trace(
        go.Scatter(
            x=x_coords,
            y=y_coords,
            mode="lines+markers",
            name="Trajectory",
            line=dict(color="green", width=2),
            marker=dict(size=4, color="darkgreen"),
        )
    )

    # Mark start and end points
    if len(x_coords) > 0:
        fig.add_trace(
            go.Scatter(
                x=[x_coords[0]],
                y=[y_coords[0]],
                mode="markers",
                name="Start",
                marker=dict(size=12, color="blue", symbol="circle"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[x_coords[-1]],
                y=[y_coords[-1]],
                mode="markers",
                name="Current",
                marker=dict(size=12, color="red", symbol="circle"),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="X Position",
        yaxis_title="Y Position",
        height=height,
        template="plotly_white",
        margin=dict(l=50, r=20, t=50, b=50),
        yaxis=dict(scaleanchor="x", scaleratio=1),  # Equal aspect ratio
    )

    return fig


def create_lap_time_chart(
    lap_data: List[Dict[str, Any]],
    title: str = "Lap Times",
    height: int = 400,
) -> go.Figure:
    """
    Create a bar chart showing lap times.

    Args:
        lap_data: List of dicts with 'lap' and 'lap_time' in milliseconds
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure with lap time chart

    Example:
        >>> data = [{'lap': 1, 'lap_time': 65000}, {'lap': 2, 'lap_time': 63500}]
        >>> fig = create_lap_time_chart(data)
        >>> fig.show()
    """
    if not lap_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No lap data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(height=height, title=title)
        return fig

    df = pd.DataFrame(lap_data)

    # Convert lap time from ms to seconds
    if "lap_time" in df.columns:
        df["lap_time_s"] = df["lap_time"] / 1000.0

    # Find best lap
    if "lap_time_s" in df.columns:
        best_lap_idx = df["lap_time_s"].idxmin()
        colors = ["gold" if i == best_lap_idx else "lightblue" for i in range(len(df))]
    else:
        colors = "lightblue"

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["lap"] if "lap" in df else df.index,
            y=df["lap_time_s"] if "lap_time_s" in df else df["lap_time"],
            name="Lap Time",
            marker_color=colors,
            text=df["lap_time_s"].round(2) if "lap_time_s" in df else None,
            textposition="outside",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Lap",
        yaxis_title="Time (s)",
        height=height,
        template="plotly_white",
        margin=dict(l=50, r=20, t=50, b=50),
        showlegend=False,
    )

    return fig


def create_temperature_chart(
    telemetry_data: List[Dict[str, Any]],
    title: str = "Temperature Over Time",
    height: int = 400,
) -> go.Figure:
    """
    Create a multi-line chart for different temperature readings.

    Args:
        telemetry_data: List of telemetry dicts with temperature data
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure with temperature chart

    Example:
        >>> data = [
        ...     {'timestamp': 1.0, 'engine_temp': 85, 'tire_temp_fl': 70},
        ...     {'timestamp': 2.0, 'engine_temp': 87, 'tire_temp_fl': 72}
        ... ]
        >>> fig = create_temperature_chart(data)
        >>> fig.show()
    """
    if not telemetry_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No temperature data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(height=height, title=title)
        return fig

    df = pd.DataFrame(telemetry_data)
    fig = go.Figure()

    # Temperature fields to plot (if they exist)
    temp_fields = {
        "engine_temp": {"name": "Engine", "color": "red"},
        "tire_temp_fl": {"name": "Tire FL", "color": "orange"},
        "tire_temp_fr": {"name": "Tire FR", "color": "yellow"},
        "tire_temp_rl": {"name": "Tire RL", "color": "green"},
        "tire_temp_rr": {"name": "Tire RR", "color": "blue"},
    }

    for field, config in temp_fields.items():
        if field in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"] if "timestamp" in df else df.index,
                    y=df[field],
                    mode="lines",
                    name=config["name"],
                    line=dict(color=config["color"], width=2),
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title="Temperature (°C)",
        height=height,
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=50, r=20, t=50, b=50),
    )

    return fig


def create_comparison_chart(
    data_sets: List[Dict[str, Any]],
    title: str = "Lap Comparison",
    height: int = 400,
) -> go.Figure:
    """
    Create a chart comparing multiple laps or drivers.

    Args:
        data_sets: List of dicts with 'name', 'x', 'y' data
        title: Chart title
        height: Chart height in pixels

    Returns:
        Plotly Figure with comparison chart

    Example:
        >>> data = [
        ...     {'name': 'Lap 1', 'x': [0, 1, 2], 'y': [0, 50, 100]},
        ...     {'name': 'Lap 2', 'x': [0, 1, 2], 'y': [0, 55, 105]}
        ... ]
        >>> fig = create_comparison_chart(data)
        >>> fig.show()
    """
    if not data_sets:
        fig = go.Figure()
        fig.add_annotation(
            text="No data to compare",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray"),
        )
        fig.update_layout(height=height, title=title)
        return fig

    fig = go.Figure()

    colors = px.colors.qualitative.Plotly

    for idx, dataset in enumerate(data_sets):
        fig.add_trace(
            go.Scatter(
                x=dataset.get("x", []),
                y=dataset.get("y", []),
                mode="lines",
                name=dataset.get("name", f"Dataset {idx+1}"),
                line=dict(color=colors[idx % len(colors)], width=2),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Distance/Time",
        yaxis_title="Value",
        height=height,
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=50, r=20, t=50, b=50),
    )

    return fig
