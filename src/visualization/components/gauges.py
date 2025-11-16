"""
Gauges Component
Visual gauges for telemetry display (speedometer, tachometer, etc.).

Reference: https://plotly.com/python/indicator/
"""

import plotly.graph_objects as go
from typing import Optional


def create_gauge(
    value: float,
    max_value: float,
    title: str,
    unit: str = "",
    color_zones: Optional[list] = None,
    height: int = 250,
) -> go.Figure:
    """
    Create a generic gauge indicator.

    Args:
        value: Current value to display
        max_value: Maximum value for the gauge
        title: Title of the gauge
        unit: Unit of measurement (e.g., "km/h", "RPM")
        color_zones: List of color zones [(threshold, color), ...]
        height: Height of the gauge in pixels

    Returns:
        Plotly Figure object with the gauge

    Example:
        >>> fig = create_gauge(120, 300, "Speed", "km/h")
        >>> fig.show()
    """
    if color_zones is None:
        # Default color zones: green -> yellow -> red
        color_zones = [
            (max_value * 0.6, "green"),
            (max_value * 0.8, "yellow"),
            (max_value, "red"),
        ]

    # Build steps for gauge colors
    steps = []
    prev_threshold = 0
    for threshold, color in color_zones:
        steps.append({"range": [prev_threshold, threshold], "color": color})
        prev_threshold = threshold

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": f"{title} ({unit})" if unit else title,
                "font": {"size": 18},
            },
            number={"suffix": f" {unit}" if unit else "", "font": {"size": 24}},
            gauge={
                "axis": {
                    "range": [0, max_value],
                    "tickwidth": 1,
                    "tickcolor": "darkblue",
                },
                "bar": {"color": "darkblue", "thickness": 0.75},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": steps,
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": max_value * 0.9,
                },
            },
        )
    )

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        font={"family": "Arial, sans-serif"},
    )

    return fig


def create_speed_gauge(speed_kmh: float, max_speed: int = 300) -> go.Figure:
    """
    Create a speedometer gauge.

    Args:
        speed_kmh: Current speed in km/h
        max_speed: Maximum speed to display (default 300 km/h)

    Returns:
        Plotly Figure with speedometer

    Example:
        >>> fig = create_speed_gauge(142.5)
        >>> fig.show()
    """
    color_zones = [
        (max_speed * 0.5, "lightgreen"),
        (max_speed * 0.7, "yellow"),
        (max_speed * 0.85, "orange"),
        (max_speed, "red"),
    ]

    return create_gauge(
        value=speed_kmh,
        max_value=max_speed,
        title="Speed",
        unit="km/h",
        color_zones=color_zones,
        height=280,
    )


def create_rpm_gauge(rpm: float, max_rpm: int = 10000) -> go.Figure:
    """
    Create an RPM tachometer gauge.

    Args:
        rpm: Current RPM
        max_rpm: Maximum RPM to display (default 10000)

    Returns:
        Plotly Figure with tachometer

    Example:
        >>> fig = create_rpm_gauge(6500, max_rpm=9000)
        >>> fig.show()
    """
    # RPM color zones - green zone, yellow zone, red zone
    color_zones = [
        (max_rpm * 0.6, "lightgreen"),
        (max_rpm * 0.75, "yellow"),
        (max_rpm * 0.85, "orange"),
        (max_rpm, "red"),
    ]

    return create_gauge(
        value=rpm,
        max_value=max_rpm,
        title="Engine RPM",
        unit="RPM",
        color_zones=color_zones,
        height=280,
    )


def create_temperature_gauge(
    temperature: float, max_temp: int = 120, unit: str = "°C"
) -> go.Figure:
    """
    Create a temperature gauge for engine/tire temperature.

    Args:
        temperature: Current temperature
        max_temp: Maximum temperature to display (default 120°C)
        unit: Temperature unit (default °C)

    Returns:
        Plotly Figure with temperature gauge

    Example:
        >>> fig = create_temperature_gauge(85.5)
        >>> fig.show()
    """
    # Temperature zones - cool -> warm -> hot -> critical
    color_zones = [
        (max_temp * 0.5, "lightblue"),
        (max_temp * 0.7, "lightgreen"),
        (max_temp * 0.85, "orange"),
        (max_temp, "red"),
    ]

    return create_gauge(
        value=temperature,
        max_value=max_temp,
        title="Temperature",
        unit=unit,
        color_zones=color_zones,
        height=250,
    )


def create_gear_indicator(gear: int) -> go.Figure:
    """
    Create a simple gear indicator display.

    Args:
        gear: Current gear (-1=R, 0=N, 1-6=gears)

    Returns:
        Plotly Figure with gear indicator

    Example:
        >>> fig = create_gear_indicator(3)
        >>> fig.show()
    """
    # Convert gear number to display
    if gear == -1:
        display_gear = "R"
        color = "orange"
    elif gear == 0:
        display_gear = "N"
        color = "gray"
    else:
        display_gear = str(gear)
        color = "lightblue"

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=gear,
            number={
                "font": {"size": 72, "color": color, "family": "Arial Black"},
                "prefix": "",
                "suffix": "",
            },
            title={"text": "GEAR", "font": {"size": 18}},
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )

    # Override number with text display
    fig.update_traces(number={"valueformat": ""})
    fig.add_annotation(
        text=display_gear,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=72, color=color, family="Arial Black"),
    )

    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        font={"family": "Arial, sans-serif"},
    )

    return fig
