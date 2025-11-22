# Tutorial 3: Real-Time Dashboard

This tutorial will teach you how to create and customize an interactive web dashboard to visualize telemetry in real-time.

## Objectives

- ✅ Create a web dashboard with Dash
- ✅ Display real-time graphs
- ✅ Customize widgets and indicators
- ✅ Add custom alerts
- ✅ Configure automatic updates

## Prerequisites

- Tutorials 1 and 2 completed
- LFS running with InSim active

## Estimated Time: 30-45 minutes

## Step 1: Basic Dashboard Structure

```python
"""
Real-Time Dashboard
Tutorial for creating an interactive dashboard with Dash.
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime
import numpy as np

from src.connection import InSimClient
from src.telemetry import TelemetryCollector
from src.utils import setup_logger

logger = setup_logger("dashboard", "INFO")

# Initialize Dash application
app = dash.Dash(__name__)

# Configure InSim
client = InSimClient(host="127.0.0.1", port=29999)
collector = TelemetryCollector(client)
```

## Step 2: Dashboard Layout

```python
app.layout = html.Div([
    html.H1("LFS Real-Time Telemetry", 
            style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        # Main indicators
        html.Div([
            html.H3("Speed", style={'textAlign': 'center'}),
            html.H2(id='speed-indicator', 
                   children='0 km/h',
                   style={'textAlign': 'center', 'color': '#e74c3c'})
        ], className='four columns'),
        
        html.Div([
            html.H3("RPM", style={'textAlign': 'center'}),
            html.H2(id='rpm-indicator',
                   children='0',
                   style={'textAlign': 'center', 'color': '#3498db'})
        ], className='four columns'),
        
        html.Div([
            html.H3("Gear", style={'textAlign': 'center'}),
            html.H2(id='gear-indicator',
                   children='N',
                   style={'textAlign': 'center', 'color': '#2ecc71'})
        ], className='four columns'),
    ], className='row'),
    
    # Graphs
    html.Div([
        dcc.Graph(id='speed-graph'),
        dcc.Graph(id='rpm-graph'),
    ]),
    
    html.Div([
        dcc.Graph(id='track-map'),
    ]),
    
    # Interval for updates
    dcc.Interval(
        id='interval-component',
        interval=100,  # milliseconds
        n_intervals=0
    )
])
```

## Step 3: Callbacks for Updates

```python
@app.callback(
    [Output('speed-indicator', 'children'),
     Output('rpm-indicator', 'children'),
     Output('gear-indicator', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_indicators(n):
    """Update main indicators."""
    telemetry = collector.get_latest_telemetry()
    
    if not telemetry:
        return "0 km/h", "0", "N"
    
    latest = telemetry[0] if isinstance(telemetry, list) else telemetry
    
    speed = f"{latest.get('speed', 0):.1f} km/h"
    rpm = f"{latest.get('rpm', 0)}"
    gear = latest.get('gear', 0)
    gear_str = "N" if gear == 0 else str(gear)
    
    return speed, rpm, gear_str


@app.callback(
    Output('speed-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_speed_graph(n):
    """Update speed graph."""
    history = collector.get_telemetry_history(limit=300)
    
    if not history:
        return go.Figure()
    
    times = [datetime.fromisoformat(h['timestamp']) for h in history]
    speeds = [h.get('speed', 0) for h in history]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=speeds,
        mode='lines',
        name='Speed',
        line=dict(color='#e74c3c', width=2)
    ))
    
    fig.update_layout(
        title='Speed over time',
        xaxis_title='Time',
        yaxis_title='Speed (km/h)',
        hovermode='x unified'
    )
    
    return fig


@app.callback(
    Output('track-map', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_track_map(n):
    """Update track map."""
    history = collector.get_telemetry_history(limit=500)
    
    if not history:
        return go.Figure()
    
    x_pos = [h.get('pos_x', 0) for h in history]
    y_pos = [h.get('pos_y', 0) for h in history]
    speeds = [h.get('speed', 0) for h in history]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_pos,
        y=y_pos,
        mode='markers+lines',
        marker=dict(
            size=4,
            color=speeds,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="km/h")
        ),
        line=dict(width=1),
        name='Trajectory'
    ))
    
    fig.update_layout(
        title='Track Map',
        xaxis_title='Position X',
        yaxis_title='Position Y',
        hovermode='closest'
    )
    
    return fig
```

## Step 4: Run the Dashboard

```python
def main():
    """Main function."""
    logger.info("Starting dashboard...")
    
    # Connect to LFS
    try:
        client.connect()
        client.initialize()
        logger.info("✓ Connected to LFS")
    except Exception as e:
        logger.error(f"✗ Connection error: {e}")
        return
    
    # Start collection
    collector.start()
    logger.info("✓ Telemetry collection started")
    
    # Run dashboard
    logger.info("Dashboard available at: http://localhost:8050")
    app.run_server(debug=True, port=8050)


if __name__ == '__main__':
    main()
```

## Advanced Features

### Custom Alerts

```python
def check_alerts(telemetry):
    """Check alert conditions."""
    alerts = []
    
    speed = telemetry.get('speed', 0)
    rpm = telemetry.get('rpm', 0)
    
    if speed > 200:
        alerts.append("⚠️ High speed!")
    
    if rpm > 7500:
        alerts.append("🔴 High RPM - shift gear!")
    
    return alerts
```

### Performance Graph

```python
@app.callback(
    Output('performance-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_performance(n):
    """Display comparative performance."""
    history = collector.get_telemetry_history(limit=100)
    
    # Calculate efficiency
    efficiency = [
        h.get('speed', 0) / max(h.get('rpm', 1), 1) * 1000
        for h in history
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=np.mean(efficiency) if efficiency else 0,
        title={'text': "Efficiency"},
        gauge={'axis': {'range': [None, 50]}}
    ))
    
    return fig
```

## Theme Customization

```python
app.layout = html.Div([
    # ... previous content ...
], style={
    'backgroundColor': '#ecf0f1',
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
})
```

## Run

```bash
python dashboard_realtime.py
```

Open your browser at: **http://localhost:8050**

## Tips

- Adjust `interval` as needed (100-500ms recommended)
- Limit history to avoid memory issues
- Use `dcc.Store` to share data between callbacks
- Consider `dash-bootstrap-components` for better design

## Next Steps

- **[Tutorial 4: Advanced Analysis](04-advanced-analysis.md)**
- **[Visualization Documentation](../visualization.md)**

---

Now you have a professional dashboard! 📊
