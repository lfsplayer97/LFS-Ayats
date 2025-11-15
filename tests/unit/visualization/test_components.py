"""
Unit tests for visualization components (gauges, charts, layout).
"""

from src.visualization.components.gauges import (
    create_gauge,
    create_speed_gauge,
    create_rpm_gauge,
    create_temperature_gauge,
    create_gear_indicator,
)
from src.visualization.components.charts import (
    create_speed_chart,
    create_position_chart,
    create_lap_time_chart,
    create_temperature_chart,
    create_comparison_chart,
)
from src.visualization.components.layout import (
    create_main_layout,
    create_telemetry_card,
    create_gauge_row,
    create_two_column_layout,
    create_tabs,
    create_control_panel,
    create_stat_box,
)


class TestGauges:
    """Test cases for gauge components."""

    def test_create_gauge_basic(self):
        """Test basic gauge creation."""
        fig = create_gauge(value=120, max_value=300, title="Test Gauge", unit="km/h")
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_speed_gauge(self):
        """Test speed gauge creation."""
        fig = create_speed_gauge(speed_kmh=150.5, max_speed=300)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_rpm_gauge(self):
        """Test RPM gauge creation."""
        fig = create_rpm_gauge(rpm=6500, max_rpm=10000)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_temperature_gauge(self):
        """Test temperature gauge creation."""
        fig = create_temperature_gauge(temperature=85.5, max_temp=120)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_gear_indicator(self):
        """Test gear indicator creation."""
        # Test forward gear
        fig = create_gear_indicator(gear=3)
        assert fig is not None

        # Test neutral
        fig = create_gear_indicator(gear=0)
        assert fig is not None

        # Test reverse
        fig = create_gear_indicator(gear=-1)
        assert fig is not None

    def test_gauge_with_custom_colors(self):
        """Test gauge with custom color zones."""
        color_zones = [(100, "green"), (200, "yellow"), (300, "red")]
        fig = create_gauge(
            value=150, max_value=300, title="Custom", color_zones=color_zones
        )
        assert fig is not None


class TestCharts:
    """Test cases for chart components."""

    def test_create_speed_chart_with_data(self):
        """Test speed chart with valid data."""
        data = [
            {"timestamp": 0.0, "speed": 10.0},
            {"timestamp": 1.0, "speed": 15.0},
            {"timestamp": 2.0, "speed": 20.0},
        ]
        fig = create_speed_chart(data)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_speed_chart_empty(self):
        """Test speed chart with empty data."""
        fig = create_speed_chart([])
        assert fig is not None

    def test_create_position_chart_with_data(self):
        """Test position chart with valid data."""
        data = [
            {"position": {"x": 100, "y": 200}},
            {"position": {"x": 110, "y": 210}},
            {"position": {"x": 120, "y": 220}},
        ]
        fig = create_position_chart(data)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_position_chart_empty(self):
        """Test position chart with empty data."""
        fig = create_position_chart([])
        assert fig is not None

    def test_create_lap_time_chart_with_data(self):
        """Test lap time chart with valid data."""
        data = [
            {"lap": 1, "lap_time": 65000},
            {"lap": 2, "lap_time": 63500},
            {"lap": 3, "lap_time": 64000},
        ]
        fig = create_lap_time_chart(data)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_lap_time_chart_empty(self):
        """Test lap time chart with empty data."""
        fig = create_lap_time_chart([])
        assert fig is not None

    def test_create_temperature_chart_with_data(self):
        """Test temperature chart with valid data."""
        data = [
            {"timestamp": 0.0, "engine_temp": 85, "tire_temp_fl": 70},
            {"timestamp": 1.0, "engine_temp": 87, "tire_temp_fl": 72},
            {"timestamp": 2.0, "engine_temp": 89, "tire_temp_fl": 74},
        ]
        fig = create_temperature_chart(data)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_temperature_chart_empty(self):
        """Test temperature chart with empty data."""
        fig = create_temperature_chart([])
        assert fig is not None

    def test_create_comparison_chart_with_data(self):
        """Test comparison chart with valid data."""
        data = [
            {"name": "Lap 1", "x": [0, 1, 2], "y": [0, 50, 100]},
            {"name": "Lap 2", "x": [0, 1, 2], "y": [0, 55, 105]},
        ]
        fig = create_comparison_chart(data)
        assert fig is not None
        assert len(fig.data) > 0

    def test_create_comparison_chart_empty(self):
        """Test comparison chart with empty data."""
        fig = create_comparison_chart([])
        assert fig is not None


class TestLayout:
    """Test cases for layout components."""

    def test_create_main_layout(self):
        """Test main layout creation."""
        layout = create_main_layout(title="Test Dashboard")
        assert layout is not None

    def test_create_telemetry_card(self):
        """Test telemetry card creation."""
        from dash import html

        card = create_telemetry_card(
            title="Test Card", content=html.Div("Test content"), card_id="test-card"
        )
        assert card is not None

    def test_create_gauge_row(self):
        """Test gauge row creation."""
        configs = [
            {
                "id": "speed",
                "title": "Speed",
                "value": 120,
                "max_value": 300,
                "unit": "km/h",
            },
            {
                "id": "rpm",
                "title": "RPM",
                "value": 6500,
                "max_value": 10000,
                "unit": "RPM",
            },
        ]
        row = create_gauge_row(configs)
        assert row is not None

    def test_create_gauge_row_empty(self):
        """Test gauge row with no gauges."""
        row = create_gauge_row([])
        assert row is not None

    def test_create_two_column_layout(self):
        """Test two column layout creation."""
        from dash import html

        layout = create_two_column_layout(html.Div("Left"), html.Div("Right"))
        assert layout is not None

    def test_create_tabs(self):
        """Test tabs creation."""
        from dash import html

        tabs = create_tabs(
            [
                {"label": "Tab 1", "content": html.Div("Content 1")},
                {"label": "Tab 2", "content": html.Div("Content 2")},
            ]
        )
        assert tabs is not None

    def test_create_control_panel(self):
        """Test control panel creation."""
        controls = [
            {
                "type": "dropdown",
                "id": "test-dropdown",
                "label": "Select",
                "options": [{"label": "Option 1", "value": 1}],
            },
            {
                "type": "slider",
                "id": "test-slider",
                "label": "Slider",
                "min": 0,
                "max": 100,
                "value": 50,
            },
        ]
        panel = create_control_panel(controls)
        assert panel is not None

    def test_create_stat_box(self):
        """Test stat box creation."""
        box = create_stat_box(label="Speed", value="150.5", unit="km/h")
        assert box is not None

    def test_create_stat_box_no_unit(self):
        """Test stat box without unit."""
        box = create_stat_box(label="Count", value="42")
        assert box is not None
