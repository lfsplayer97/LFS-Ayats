"""
Dashboard Module
Real-time telemetry dashboard using Dash and Plotly.

Reference:
    - https://dash.plotly.com/
    - https://en.lfsmanual.net/wiki/InSim.txt
"""

import dash
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List
import time
import threading
from queue import Queue

from src.telemetry.collector import TelemetryCollector, CarTelemetry
from src.connection.insim_client import InSimClient
from src.visualization.components.gauges import (
    create_speed_gauge,
    create_rpm_gauge,
    create_gear_indicator,
)
from src.visualization.components.charts import (
    create_speed_chart,
    create_position_chart,
)
from src.visualization.components.layout import (
    create_main_layout,
    create_telemetry_card,
    create_stat_box,
)


class TelemetryDashboard:
    """
    Real-time telemetry dashboard for Live for Speed.

    This dashboard provides:
    - Live gauges (speed, RPM, gear)
    - Real-time charts (speed, position)
    - Session statistics
    - Auto-refresh at configurable intervals

    Example:
        >>> dashboard = TelemetryDashboard(host="127.0.0.1", port=29999)
        >>> dashboard.run(debug=True, port=8050)

        Then open browser to http://localhost:8050
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 29999,
        app_name: str = "LFS-Ayats",
        update_interval: int = 100,
    ):
        """
        Initialize the telemetry dashboard.

        Args:
            host: LFS server host
            port: LFS InSim port
            app_name: Application name for InSim
            update_interval: Dashboard update interval in milliseconds
        """
        self.host = host
        self.port = port
        self.app_name = app_name
        self.update_interval = update_interval

        # InSim components
        self.client: Optional[InSimClient] = None
        self.collector: Optional[TelemetryCollector] = None
        self.connected = False

        # Dashboard app
        self.app = dash.Dash(
            __name__,
            title="LFS Telemetry Dashboard",
            update_title=None,
        )

        # Data queue for thread-safe updates
        self.data_queue: Queue = Queue(maxsize=1000)

        # Setup layout and callbacks
        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self) -> None:
        """Setup the dashboard layout."""
        self.app.layout = html.Div(
            [
                # Header
                html.Div(
                    [
                        html.H1(
                            "🏁 LFS Telemetry Dashboard",
                            style={
                                "textAlign": "center",
                                "color": "#2c3e50",
                                "marginBottom": "10px",
                                "fontFamily": "Arial, sans-serif",
                            },
                        ),
                        html.Div(
                            id="connection-status",
                            style={
                                "textAlign": "center",
                                "fontSize": "14px",
                                "marginBottom": "10px",
                            },
                        ),
                        html.Hr(style={"borderTop": "2px solid #3498db"}),
                    ],
                    style={"padding": "20px", "backgroundColor": "#ecf0f1"},
                ),
                # Control panel
                html.Div(
                    [
                        html.Button(
                            "Connect",
                            id="connect-button",
                            n_clicks=0,
                            style={
                                "marginRight": "10px",
                                "padding": "10px 20px",
                                "backgroundColor": "#27ae60",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "cursor": "pointer",
                            },
                        ),
                        html.Button(
                            "Disconnect",
                            id="disconnect-button",
                            n_clicks=0,
                            style={
                                "padding": "10px 20px",
                                "backgroundColor": "#e74c3c",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "cursor": "pointer",
                            },
                        ),
                        html.Div(
                            id="player-select-div",
                            children=[
                                html.Label(
                                    "Select Player:",
                                    style={
                                        "marginLeft": "20px",
                                        "marginRight": "10px",
                                        "fontWeight": "bold",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="player-dropdown",
                                    options=[],
                                    value=None,
                                    placeholder="Select a player...",
                                    style={"width": "200px", "display": "inline-block"},
                                ),
                            ],
                            style={"display": "inline-block"},
                        ),
                    ],
                    style={
                        "padding": "20px",
                        "backgroundColor": "#f8f9fa",
                        "textAlign": "center",
                    },
                ),
                # Main content
                html.Div(
                    [
                        # Statistics row
                        html.Div(
                            id="stats-row",
                            style={
                                "display": "flex",
                                "justifyContent": "center",
                                "marginBottom": "20px",
                                "flexWrap": "wrap",
                            },
                        ),
                        # Gauges row
                        html.Div(
                            [
                                html.Div(
                                    dcc.Graph(
                                        id="speed-gauge",
                                        config={"displayModeBar": False},
                                    ),
                                    style={
                                        "width": "33%",
                                        "display": "inline-block",
                                        "verticalAlign": "top",
                                    },
                                ),
                                html.Div(
                                    dcc.Graph(
                                        id="rpm-gauge",
                                        config={"displayModeBar": False},
                                    ),
                                    style={
                                        "width": "33%",
                                        "display": "inline-block",
                                        "verticalAlign": "top",
                                    },
                                ),
                                html.Div(
                                    dcc.Graph(
                                        id="gear-indicator",
                                        config={"displayModeBar": False},
                                    ),
                                    style={
                                        "width": "33%",
                                        "display": "inline-block",
                                        "verticalAlign": "top",
                                    },
                                ),
                            ],
                            style={"marginBottom": "20px"},
                        ),
                        # Charts row
                        html.Div(
                            [
                                html.Div(
                                    dcc.Graph(id="speed-chart"),
                                    style={
                                        "width": "48%",
                                        "display": "inline-block",
                                        "verticalAlign": "top",
                                        "padding": "10px",
                                    },
                                ),
                                html.Div(
                                    dcc.Graph(id="position-chart"),
                                    style={
                                        "width": "48%",
                                        "display": "inline-block",
                                        "verticalAlign": "top",
                                        "padding": "10px",
                                    },
                                ),
                            ],
                        ),
                    ],
                    style={
                        "padding": "20px",
                        "backgroundColor": "#ffffff",
                        "minHeight": "calc(100vh - 300px)",
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
                # Auto-update interval
                dcc.Interval(
                    id="interval-component",
                    interval=self.update_interval,  # milliseconds
                    n_intervals=0,
                ),
                # Hidden div to store connection state
                html.Div(id="connection-state", style={"display": "none"}),
            ],
            style={"fontFamily": "Arial, sans-serif"},
        )

    def _setup_callbacks(self) -> None:
        """Setup dashboard callbacks."""

        @self.app.callback(
            [
                Output("connection-status", "children"),
                Output("connection-state", "children"),
            ],
            [Input("connect-button", "n_clicks"), Input("disconnect-button", "n_clicks")],
            prevent_initial_call=True,
        )
        def handle_connection(connect_clicks, disconnect_clicks):
            """Handle connect/disconnect buttons."""
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if button_id == "connect-button":
                success = self.connect()
                if success:
                    return (
                        html.Span(
                            "✓ Connected to LFS",
                            style={"color": "green", "fontWeight": "bold"},
                        ),
                        "connected",
                    )
                else:
                    return (
                        html.Span(
                            "✗ Connection failed",
                            style={"color": "red", "fontWeight": "bold"},
                        ),
                        "disconnected",
                    )
            elif button_id == "disconnect-button":
                self.disconnect()
                return (
                    html.Span(
                        "○ Disconnected",
                        style={"color": "gray", "fontWeight": "bold"},
                    ),
                    "disconnected",
                )

            raise PreventUpdate

        @self.app.callback(
            [
                Output("speed-gauge", "figure"),
                Output("rpm-gauge", "figure"),
                Output("gear-indicator", "figure"),
                Output("speed-chart", "figure"),
                Output("position-chart", "figure"),
                Output("stats-row", "children"),
                Output("player-dropdown", "options"),
            ],
            [Input("interval-component", "n_intervals"), Input("player-dropdown", "value")],
            [State("connection-state", "children")],
        )
        def update_dashboard(n_intervals, selected_player, connection_state):
            """Update all dashboard components."""
            if connection_state != "connected" or not self.collector:
                # Return empty figures
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="Not connected",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=20, color="gray"),
                )

                return (
                    create_speed_gauge(0),
                    create_rpm_gauge(0),
                    create_gear_indicator(0),
                    empty_fig,
                    empty_fig,
                    [],
                    [],
                )

            # Get latest telemetry
            latest = self.collector.get_latest_telemetry()

            # Update player dropdown options
            player_options = [
                {"label": f"Player {plid}", "value": plid} for plid in latest.keys()
            ]

            # If no player selected and players available, select first
            if selected_player is None and player_options:
                selected_player = player_options[0]["value"]

            # Get telemetry for selected player
            if selected_player and selected_player in latest:
                telemetry = latest[selected_player]
                speed_kmh = telemetry.speed * 3.6
                # Note: RPM and gear would come from OutGauge or other packets
                # For now, we'll show placeholder values
                rpm = 0  # Would need OutGauge packet
                gear = 0  # Would need OutGauge packet

                # Get history for charts
                history = self.collector.get_telemetry_history(selected_player, limit=100)

                # Convert history to dict format for charts
                history_dicts = [
                    {
                        "timestamp": t.timestamp,
                        "speed": t.speed,
                        "position": t.position,
                    }
                    for t in history
                ]

                # Create figures
                speed_gauge_fig = create_speed_gauge(speed_kmh)
                rpm_gauge_fig = create_rpm_gauge(rpm)
                gear_indicator_fig = create_gear_indicator(gear)
                speed_chart_fig = create_speed_chart(history_dicts, title="Speed History")
                position_chart_fig = create_position_chart(
                    history_dicts, title="Track Position"
                )

                # Statistics
                stats = self.collector.get_statistics()
                stats_boxes = [
                    create_stat_box("Players", str(stats.get("total_players", 0))),
                    create_stat_box("Samples", str(stats.get("total_samples", 0))),
                    create_stat_box("Speed", f"{speed_kmh:.1f}", "km/h", "#3498db"),
                ]

                return (
                    speed_gauge_fig,
                    rpm_gauge_fig,
                    gear_indicator_fig,
                    speed_chart_fig,
                    position_chart_fig,
                    stats_boxes,
                    player_options,
                )
            else:
                # No player data available
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="No player data",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=20, color="gray"),
                )

                stats = self.collector.get_statistics()
                stats_boxes = [
                    create_stat_box("Players", str(stats.get("total_players", 0))),
                    create_stat_box("Samples", str(stats.get("total_samples", 0))),
                ]

                return (
                    create_speed_gauge(0),
                    create_rpm_gauge(0),
                    create_gear_indicator(0),
                    empty_fig,
                    empty_fig,
                    stats_boxes,
                    player_options,
                )

    def connect(self) -> bool:
        """
        Connect to LFS server.

        Returns:
            bool: True if connection successful
        """
        try:
            self.client = InSimClient(
                host=self.host, port=self.port, app_name=self.app_name
            )
            self.client.connect()

            self.collector = TelemetryCollector(self.client)
            self.collector.start(interval=self.update_interval)

            self.connected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from LFS server."""
        if self.collector:
            self.collector.stop()
            self.collector = None

        if self.client:
            self.client.disconnect()
            self.client = None

        self.connected = False

    def run(self, debug: bool = False, port: int = 8050, host: str = "127.0.0.1") -> None:
        """
        Run the dashboard server.

        Args:
            debug: Enable debug mode
            port: Port to run dashboard on
            host: Host to bind to

        Example:
            >>> dashboard = TelemetryDashboard()
            >>> dashboard.run(debug=True, port=8050)
        """
        print(f"Starting dashboard on http://{host}:{port}")
        print(f"Dashboard will connect to LFS at {self.host}:{self.port}")
        print("Press Connect button in the dashboard to start data collection")

        self.app.run_server(debug=debug, port=port, host=host)

    def shutdown(self) -> None:
        """Shutdown the dashboard and cleanup resources."""
        self.disconnect()
