"""
Visualization Module
Telemetry data visualization

This module provides comprehensive visualization capabilities for LFS telemetry data:
- Real-time dashboard with live gauges and charts
- Analysis plots for lap comparison and performance review
- Track map visualization with vehicle positions
- Lap comparison tools for detailed analysis

Example:
    >>> from src.visualization import TelemetryDashboard
    >>> dashboard = TelemetryDashboard(host="127.0.0.1", port=29999)
    >>> dashboard.run(debug=True, port=8050)
"""

__version__ = "0.1.0"

from .dashboard import TelemetryDashboard
from .plots import (
    create_speed_vs_distance_plot,
    create_trajectory_comparison_plot,
    create_braking_analysis_plot,
    create_heatmap_plot,
    create_sector_times_plot,
    create_g_force_plot,
)
from .map_view import (
    create_track_map,
    create_live_position_map,
    create_racing_line_map,
    create_corner_analysis_map,
    create_3d_track_map,
)
from .comparator import LapComparator, LapComparison

__all__ = [
    # Dashboard
    "TelemetryDashboard",
    # Plots
    "create_speed_vs_distance_plot",
    "create_trajectory_comparison_plot",
    "create_braking_analysis_plot",
    "create_heatmap_plot",
    "create_sector_times_plot",
    "create_g_force_plot",
    # Map views
    "create_track_map",
    "create_live_position_map",
    "create_racing_line_map",
    "create_corner_analysis_map",
    "create_3d_track_map",
    # Comparator
    "LapComparator",
    "LapComparison",
]
