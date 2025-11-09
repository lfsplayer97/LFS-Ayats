# Visualization Module Documentation

## Overview

The visualization module provides comprehensive tools for visualizing Live for Speed (LFS) telemetry data. It includes real-time dashboards, analysis plots, track maps, and lap comparison tools.

## Table of Contents

1. [Real-Time Dashboard](#real-time-dashboard)
2. [Analysis Plots](#analysis-plots)
3. [Track Maps](#track-maps)
4. [Lap Comparator](#lap-comparator)
5. [Components Library](#components-library)
6. [Usage Examples](#usage-examples)

---

## Real-Time Dashboard

The `TelemetryDashboard` class provides a web-based real-time telemetry dashboard using Dash and Plotly.

### Features

- **Live Gauges**: Speedometer, tachometer, gear indicator
- **Real-time Charts**: Speed and position tracking
- **Multi-Player Support**: Select from multiple active players
- **Connection Management**: Connect/disconnect from LFS server via UI
- **Auto-Refresh**: Configurable update rate (default 100ms)
- **Statistics Display**: Players count, sample count, current speed

### Quick Start

```python
from src.visualization import TelemetryDashboard

# Create dashboard instance
dashboard = TelemetryDashboard(
    host="127.0.0.1",          # LFS server host
    port=29999,                 # InSim port
    app_name="LFS-Ayats",      # Application name
    update_interval=100         # Update every 100ms (10Hz)
)

# Run the dashboard server
dashboard.run(
    debug=True,                 # Enable debug mode
    port=8050,                  # Dashboard port
    host="0.0.0.0"             # Allow external connections
)
```

Then open your browser to `http://localhost:8050`

### Dashboard Interface

#### Header
- Title and connection status indicator
- Connect/Disconnect buttons
- Player selection dropdown

#### Gauges Row
- **Speedometer**: Current speed in km/h with color zones
- **Tachometer**: Engine RPM (requires OutGauge packet)
- **Gear Indicator**: Current gear (R/N/1-6)

#### Charts Row
- **Speed History**: Line chart showing speed over time
- **Track Position**: 2D scatter plot of vehicle trajectory

#### Statistics
- Total players tracked
- Total telemetry samples collected
- Current speed

---

## Analysis Plots

The `plots` module provides functions for creating detailed analysis visualizations.

### Available Plots

#### 1. Speed vs Distance Plot

```python
from src.visualization import create_speed_vs_distance_plot

fig = create_speed_vs_distance_plot(
    telemetry_list,
    title="Speed Analysis - Lap 5"
)
fig.show()  # or fig.write_html("speed_plot.html")
```

**Features:**
- Shows speed profile over track distance
- Calculates cumulative distance from position data
- Filled area under curve
- Interactive hover tooltips

#### 2. Trajectory Comparison Plot

```python
from src.visualization import create_trajectory_comparison_plot

trajectories = {
    "Best Lap": best_lap_telemetry,
    "Current Lap": current_lap_telemetry,
    "Ideal Line": ideal_lap_telemetry
}

fig = create_trajectory_comparison_plot(trajectories)
fig.show()
```

**Features:**
- Overlay multiple lap trajectories
- Color-coded by lap
- Start point markers
- Equal aspect ratio for accuracy

#### 3. Braking Analysis Plot

```python
from src.visualization import create_braking_analysis_plot

fig = create_braking_analysis_plot(telemetry_list)
fig.show()
```

**Features:**
- Dual-axis plot (speed + acceleration)
- Color-coded acceleration bars (red=braking, green=acceleration)
- Identifies braking zones
- Shows acceleration/deceleration rates

#### 4. Track Speed Heatmap

```python
from src.visualization import create_heatmap_plot

fig = create_heatmap_plot(telemetry_list)
fig.show()
```

**Features:**
- Color-coded by speed (blue=slow, red=fast)
- Shows speed distribution across track
- Identifies fast and slow sections
- Interactive hover with speed values

#### 5. Sector Times Plot

```python
from src.visualization import create_sector_times_plot

lap_data = [
    {"lap": 1, "sector1": 20.5, "sector2": 18.3, "sector3": 22.1},
    {"lap": 2, "sector1": 19.8, "sector2": 18.5, "sector3": 21.9},
]

fig = create_sector_times_plot(lap_data)
fig.show()
```

**Features:**
- Grouped bar chart by sector
- Compares sector times across laps
- Highlights best times
- Easy identification of improvement areas

#### 6. G-Force Analysis Plot

```python
from src.visualization import create_g_force_plot

fig = create_g_force_plot(telemetry_list)
fig.show()
```

**Features:**
- Estimates longitudinal G-forces from speed changes
- Shows acceleration/braking forces
- Reference zero line
- Helps identify harsh braking/acceleration

---

## Track Maps

The `map_view` module provides various track map visualizations.

### 1. Basic Track Map

```python
from src.visualization import create_track_map

fig = create_track_map(
    telemetry_list,
    title="Blackwood GP Track",
    show_speed_colors=True,  # Color by speed
    height=600
)
fig.show()
```

**Features:**
- 2D top-down view of track
- Optional speed color-coding
- Start/finish marker
- Equal aspect ratio

### 2. Live Position Map

```python
from src.visualization import create_live_position_map

# Get current positions
positions = collector.get_latest_telemetry()

fig = create_live_position_map(
    vehicle_positions=positions,
    track_data=reference_lap,  # Optional track outline
    title="Live Race Positions"
)
fig.show()
```

**Features:**
- Shows current vehicle positions
- Multiple vehicles simultaneously
- Color-coded by speed
- Player ID labels
- Optional track outline overlay

### 3. Racing Line Comparison

```python
from src.visualization import create_racing_line_map

fig = create_racing_line_map(
    ideal_line=reference_lap,
    current_line=current_lap,
    title="Racing Line Analysis"
)
fig.show()
```

**Features:**
- Compares two racing lines
- Ideal line (dotted green)
- Current line (solid red)
- Helps identify line improvements

### 4. Corner Analysis Map

```python
from src.visualization import create_corner_analysis_map

fig = create_corner_analysis_map(
    telemetry_list,
    corner_threshold=0.3
)
fig.show()
```

**Features:**
- Highlights braking zones (red markers)
- Identifies slow corners (orange markers)
- Shows corner entry/exit points
- Track base line

### 5. 3D Track Map

```python
from src.visualization import create_3d_track_map

fig = create_3d_track_map(
    telemetry_list,
    title="3D Track Elevation",
    height=700
)
fig.show()
```

**Features:**
- 3D visualization with elevation
- Rotatable and zoomable
- Color-coded by speed
- Shows track topology

---

## Lap Comparator

The `LapComparator` class provides comprehensive lap comparison tools.

### Basic Usage

```python
from src.visualization import LapComparator

# Create comparator
comparator = LapComparator()

# Add laps for comparison
comparator.add_lap("Lap 1", lap1_telemetry)
comparator.add_lap("Lap 2", lap2_telemetry)
comparator.add_lap("Best Lap", best_lap_telemetry)

# Create comparison plots
fig = comparator.create_comparison_plot()
fig.show()
```

### Comparison Features

#### Speed Profile Comparison

```python
fig = comparator.create_comparison_plot()
```

Shows speed vs distance for multiple laps overlaid on same plot.

#### Time Delta Plot

```python
fig = comparator.create_time_delta_plot(reference_lap, current_lap)
```

Shows cumulative time gain/loss throughout the lap:
- Above zero line = losing time
- Below zero line = gaining time

#### Sector Comparison

```python
fig = comparator.create_sector_comparison()
```

Grouped bar chart comparing sector times across all stored laps.

#### Trajectory Overlay

```python
fig = comparator.create_trajectory_overlay()
```

Shows racing lines of all laps overlaid on track map.

### Statistical Analysis

```python
# Get lap comparison statistics
comparison = comparator.compare_laps(lap1, lap2)

print(f"Faster lap: {comparison.lap_names[comparison.faster_lap]}")
print(f"Time difference: {comparison.total_time_diff:.3f}s")
print(f"Sector differences: {comparison.sector_diffs}")

# Get overall statistics
stats = comparator.get_statistics()
print(f"Fastest lap: {stats['fastest_lap']}")
print(f"Lap times: {stats['lap_times']}")
```

---

## Components Library

The `components` submodule provides reusable UI components for building custom dashboards.

### Gauges

```python
from src.visualization.components import (
    create_speed_gauge,
    create_rpm_gauge,
    create_temperature_gauge,
    create_gear_indicator
)

# Create speedometer
speed_fig = create_speed_gauge(speed_kmh=142.5, max_speed=300)

# Create tachometer
rpm_fig = create_rpm_gauge(rpm=6500, max_rpm=9000)

# Create temperature gauge
temp_fig = create_temperature_gauge(temperature=85.5, max_temp=120)

# Create gear indicator
gear_fig = create_gear_indicator(gear=3)
```

### Charts

```python
from src.visualization.components import (
    create_speed_chart,
    create_position_chart,
    create_lap_time_chart,
    create_temperature_chart
)

# Speed chart
speed_fig = create_speed_chart(telemetry_data)

# Position chart
position_fig = create_position_chart(telemetry_data)

# Lap times
lap_fig = create_lap_time_chart(lap_data)
```

### Layout Components

```python
from src.visualization.components import (
    create_main_layout,
    create_telemetry_card,
    create_stat_box,
    create_two_column_layout
)

from dash import html

# Create stat boxes
stats = [
    create_stat_box("Max Speed", "185.2", "km/h"),
    create_stat_box("Best Lap", "1:23.456", ""),
]

# Create card
card = create_telemetry_card(
    title="Session Stats",
    content=html.Div(stats),
    card_id="stats-card"
)
```

---

## Usage Examples

### Example 1: Running the Dashboard

```python
# examples/dashboard_example.py
from src.visualization import TelemetryDashboard

dashboard = TelemetryDashboard(
    host="127.0.0.1",
    port=29999,
    update_interval=100
)

dashboard.run(debug=True, port=8050)
```

### Example 2: Generating Analysis Plots

```python
# examples/visualization_example.py
from src.connection import InSimClient
from src.telemetry import TelemetryCollector
from src.visualization import (
    create_speed_vs_distance_plot,
    create_track_map,
    create_heatmap_plot
)

# Connect and collect data
client = InSimClient(host="127.0.0.1", port=29999)
client.connect()

collector = TelemetryCollector(client)
collector.start()

# ... collect data ...

collector.stop()

# Get telemetry
telemetry = collector.get_telemetry_history(plid=1)

# Create plots
fig1 = create_speed_vs_distance_plot(telemetry)
fig1.write_html("speed_plot.html")

fig2 = create_track_map(telemetry, show_speed_colors=True)
fig2.write_html("track_map.html")

fig3 = create_heatmap_plot(telemetry)
fig3.write_html("heatmap.html")

client.disconnect()
```

### Example 3: Lap Comparison

```python
from src.visualization import LapComparator

comparator = LapComparator()

# Add laps
comparator.add_lap("Reference", reference_lap)
comparator.add_lap("Current", current_lap)

# Generate comparison
fig = comparator.create_comparison_plot()
fig.write_html("lap_comparison.html")

# Time delta analysis
delta_fig = comparator.create_time_delta_plot(reference_lap, current_lap)
delta_fig.write_html("time_delta.html")

# Statistics
stats = comparator.get_statistics()
print(f"Fastest: {stats['fastest_lap']} - {stats['lap_times'][stats['fastest_lap']]:.3f}s")
```

---

## Configuration Options

### Dashboard Configuration

- **host**: LFS server address (default: "127.0.0.1")
- **port**: InSim port (default: 29999)
- **app_name**: Application identifier (default: "LFS-Ayats")
- **update_interval**: Dashboard refresh rate in ms (default: 100)

### Plot Customization

Most plot functions accept these common parameters:

- **title**: Custom plot title
- **height**: Plot height in pixels
- **color**: Color scheme or specific colors

### Best Practices

1. **Update Rate**: Keep dashboard update_interval ≥100ms to avoid overwhelming the browser
2. **Data Limits**: Limit history length for real-time charts (e.g., last 100 samples)
3. **Export Format**: Use `fig.write_html()` for interactive plots, `fig.write_image()` for static
4. **Browser Compatibility**: Tested with Chrome, Firefox, Edge (latest versions)
5. **Performance**: Close unused plots/dashboards to free memory

---

## Troubleshooting

### Dashboard won't connect
- Ensure LFS is running
- Enable InSim in LFS: `/insim 29999`
- Check firewall settings for port 29999
- Verify host/port configuration

### No data displayed
- Check that you're driving in LFS (not in pits)
- Verify InSim is receiving packets
- Check console for connection errors
- Ensure player is selected in dropdown

### Plots show "No data available"
- Verify telemetry collection is running
- Check that telemetry_list is not empty
- Ensure position data exists in telemetry

### Dashboard performance issues
- Reduce update_interval (e.g., 200-500ms)
- Limit chart history length
- Close other browser tabs
- Check CPU usage

---

## API Reference

For detailed API documentation, see the docstrings in each module:

- `src/visualization/dashboard.py` - Dashboard class
- `src/visualization/plots.py` - Analysis plot functions
- `src/visualization/map_view.py` - Map visualization functions
- `src/visualization/comparator.py` - Lap comparison tools
- `src/visualization/components/` - Reusable UI components

---

## Contributing

When adding new visualizations:

1. Follow existing code style (Black formatter, type hints)
2. Add comprehensive docstrings with examples
3. Include unit tests in `tests/unit/visualization/`
4. Handle empty data gracefully
5. Add usage example to this documentation

---

## License

Part of the LFS-Ayats project. See LICENSE file for details.
