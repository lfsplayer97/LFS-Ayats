"""
Layout Component
Dash layout components and utilities.

Reference: https://dash.plotly.com/layout
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import List, Dict, Any, Optional


def create_main_layout(
    title: str = "LFS Telemetry Dashboard", children: Optional[List] = None
) -> html.Div:
    """
    Create the main dashboard layout structure.

    Args:
        title: Dashboard title
        children: List of child components

    Returns:
        Dash html.Div with layout structure

    Example:
        >>> layout = create_main_layout("My Dashboard")
    """
    if children is None:
        children = []

    return html.Div(
        [
            # Header
            html.Div(
                [
                    html.H1(
                        title,
                        style={
                            "textAlign": "center",
                            "color": "#2c3e50",
                            "marginBottom": "10px",
                        },
                    ),
                    html.Hr(style={"borderTop": "2px solid #3498db"}),
                ],
                style={"padding": "20px", "backgroundColor": "#ecf0f1"},
            ),
            # Main content
            html.Div(
                children,
                style={
                    "padding": "20px",
                    "backgroundColor": "#ffffff",
                    "minHeight": "calc(100vh - 150px)",
                },
            ),
            # Footer
            html.Div(
                [
                    html.Hr(style={"borderTop": "1px solid #bdc3c7"}),
                    html.P(
                        "LFS-Ayats Telemetry System © 2024",
                        style={"textAlign": "center", "color": "#7f8c8d"},
                    ),
                ],
                style={"padding": "10px", "backgroundColor": "#ecf0f1"},
            ),
        ],
        style={"fontFamily": "Arial, sans-serif"},
    )


def create_telemetry_card(
    title: str,
    content: Any,
    card_id: Optional[str] = None,
    color: str = "#3498db",
) -> html.Div:
    """
    Create a card component for displaying telemetry data.

    Args:
        title: Card title
        content: Card content (can be graphs, text, etc.)
        card_id: Optional ID for the card
        color: Header color

    Returns:
        Dash html.Div representing a card

    Example:
        >>> card = create_telemetry_card("Speed", html.Div("150 km/h"))
    """
    return html.Div(
        [
            html.Div(
                html.H3(
                    title,
                    style={
                        "margin": "0",
                        "padding": "15px",
                        "color": "white",
                        "backgroundColor": color,
                        "borderRadius": "8px 8px 0 0",
                    },
                ),
            ),
            html.Div(
                content,
                style={
                    "padding": "20px",
                    "backgroundColor": "white",
                    "borderRadius": "0 0 8px 8px",
                    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                },
            ),
        ],
        id=card_id,
        style={
            "marginBottom": "20px",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "overflow": "hidden",
        },
    )


def create_gauge_row(gauge_configs: List[Dict[str, Any]]) -> html.Div:
    """
    Create a row of gauges with equal spacing.

    Args:
        gauge_configs: List of dicts with gauge configuration
            Each dict should have: 'id', 'title', 'value', 'max_value', 'unit'

    Returns:
        Dash html.Div with gauges in a row

    Example:
        >>> configs = [
        ...     {'id': 'speed', 'title': 'Speed', 'value': 120, 'max_value': 300, 'unit': 'km/h'},
        ...     {'id': 'rpm', 'title': 'RPM', 'value': 6500, 'max_value': 10000, 'unit': 'RPM'}
        ... ]
        >>> row = create_gauge_row(configs)
    """
    num_gauges = len(gauge_configs)
    if num_gauges == 0:
        return html.Div()

    width = f"{100 / num_gauges}%"

    gauge_divs = []
    for config in gauge_configs:
        gauge_divs.append(
            html.Div(
                dcc.Graph(
                    id=config.get("id", "gauge"),
                    config={"displayModeBar": False},
                    style={"height": "100%"},
                ),
                style={
                    "width": width,
                    "display": "inline-block",
                    "verticalAlign": "top",
                    "padding": "10px",
                },
            )
        )

    return html.Div(
        gauge_divs,
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "justifyContent": "space-around",
            "marginBottom": "20px",
        },
    )


def create_two_column_layout(left_content: Any, right_content: Any) -> html.Div:
    """
    Create a two-column layout.

    Args:
        left_content: Content for left column
        right_content: Content for right column

    Returns:
        Dash html.Div with two-column layout

    Example:
        >>> layout = create_two_column_layout(
        ...     html.Div("Left content"),
        ...     html.Div("Right content")
        ... )
    """
    return html.Div(
        [
            html.Div(
                left_content,
                style={
                    "width": "48%",
                    "display": "inline-block",
                    "verticalAlign": "top",
                    "padding": "10px",
                },
            ),
            html.Div(
                right_content,
                style={
                    "width": "48%",
                    "display": "inline-block",
                    "verticalAlign": "top",
                    "padding": "10px",
                },
            ),
        ],
        style={"display": "flex", "justifyContent": "space-between"},
    )


def create_tabs(tab_configs: List[Dict[str, Any]]) -> dcc.Tabs:
    """
    Create a tabbed interface.

    Args:
        tab_configs: List of dicts with 'label' and 'content'

    Returns:
        Dash dcc.Tabs component

    Example:
        >>> tabs = create_tabs([
        ...     {'label': 'Live', 'content': html.Div("Live data")},
        ...     {'label': 'Analysis', 'content': html.Div("Analysis")}
        ... ])
    """
    tabs = []
    for idx, config in enumerate(tab_configs):
        tabs.append(
            dcc.Tab(
                label=config.get("label", f"Tab {idx+1}"),
                children=config.get("content", html.Div()),
                style={
                    "padding": "10px",
                    "backgroundColor": "#ecf0f1",
                    "border": "1px solid #bdc3c7",
                },
                selected_style={
                    "padding": "10px",
                    "backgroundColor": "#3498db",
                    "color": "white",
                    "border": "1px solid #2980b9",
                },
            )
        )

    return dcc.Tabs(
        tabs,
        style={
            "marginBottom": "20px",
        },
    )


def create_control_panel(controls: List[Dict[str, Any]]) -> html.Div:
    """
    Create a control panel with various input controls.

    Args:
        controls: List of dicts defining controls
            Each dict should have: 'type', 'id', 'label', and type-specific options

    Returns:
        Dash html.Div with control panel

    Example:
        >>> controls = [
        ...     {'type': 'dropdown', 'id': 'player-select', 'label': 'Player',
        ...      'options': [{'label': 'Player 1', 'value': 1}]},
        ...     {'type': 'slider', 'id': 'speed-filter', 'label': 'Min Speed',
        ...      'min': 0, 'max': 300, 'value': 50}
        ... ]
        >>> panel = create_control_panel(controls)
    """
    control_elements = []

    for control in controls:
        control_type = control.get("type", "text")
        control_id = control.get("id", "control")
        label = control.get("label", "Control")

        # Create label
        control_elements.append(
            html.Label(label, style={"fontWeight": "bold", "marginTop": "10px"})
        )

        # Create control based on type
        if control_type == "dropdown":
            control_elements.append(
                dcc.Dropdown(
                    id=control_id,
                    options=control.get("options", []),
                    value=control.get("value"),
                    placeholder=control.get("placeholder", "Select..."),
                    style={"marginBottom": "10px"},
                )
            )
        elif control_type == "slider":
            control_elements.append(
                dcc.Slider(
                    id=control_id,
                    min=control.get("min", 0),
                    max=control.get("max", 100),
                    value=control.get("value", 50),
                    marks={
                        control.get("min", 0): str(control.get("min", 0)),
                        control.get("max", 100): str(control.get("max", 100)),
                    },
                    tooltip={"placement": "bottom", "always_visible": True},
                    style={"marginBottom": "20px"},
                )
            )
        elif control_type == "checklist":
            control_elements.append(
                dcc.Checklist(
                    id=control_id,
                    options=control.get("options", []),
                    value=control.get("value", []),
                    style={"marginBottom": "10px"},
                )
            )
        elif control_type == "radio":
            control_elements.append(
                dcc.RadioItems(
                    id=control_id,
                    options=control.get("options", []),
                    value=control.get("value"),
                    style={"marginBottom": "10px"},
                )
            )

    return html.Div(
        control_elements,
        style={
            "padding": "20px",
            "backgroundColor": "#f8f9fa",
            "border": "1px solid #dee2e6",
            "borderRadius": "8px",
            "marginBottom": "20px",
        },
    )


def create_stat_box(label: str, value: str, unit: str = "", color: str = "#3498db") -> html.Div:
    """
    Create a statistics box displaying a single value.

    Args:
        label: Label for the statistic
        value: Value to display
        unit: Unit of measurement
        color: Background color

    Returns:
        Dash html.Div with stat box

    Example:
        >>> box = create_stat_box("Max Speed", "185.2", "km/h")
    """
    return html.Div(
        [
            html.Div(
                label,
                style={
                    "fontSize": "14px",
                    "color": "#7f8c8d",
                    "marginBottom": "5px",
                    "fontWeight": "500",
                },
            ),
            html.Div(
                [
                    html.Span(
                        value,
                        style={
                            "fontSize": "28px",
                            "fontWeight": "bold",
                            "color": color,
                        },
                    ),
                    html.Span(
                        f" {unit}" if unit else "",
                        style={
                            "fontSize": "16px",
                            "color": "#95a5a6",
                            "marginLeft": "5px",
                        },
                    ),
                ],
            ),
        ],
        style={
            "padding": "15px",
            "backgroundColor": "white",
            "border": f"2px solid {color}",
            "borderRadius": "8px",
            "textAlign": "center",
            "minWidth": "150px",
            "marginRight": "10px",
            "marginBottom": "10px",
            "display": "inline-block",
        },
    )
