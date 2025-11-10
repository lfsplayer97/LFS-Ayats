# Tutorial 3: Dashboard en Temps Real

Aquest tutorial t'ensenyarà a crear i personalitzar un dashboard web interactiu per visualitzar telemetria en temps real.

## Objectius

- ✅ Crear un dashboard web amb Dash
- ✅ Mostrar gràfics en temps real
- ✅ Personalitzar widgets i indicadors
- ✅ Afegir alertes personalitzades
- ✅ Configurar actualitzacions automàtiques

## Prerequisits

- Tutorials 1 i 2 completats
- LFS en execució amb InSim actiu

## Temps Estimat: 30-45 minuts

## Pas 1: Estructura Bàsica del Dashboard

```python
"""
Dashboard en Temps Real
Tutorial per crear un dashboard interactiu amb Dash.
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

# Inicialitzar aplicació Dash
app = dash.Dash(__name__)

# Configurar InSim
client = InSimClient(host="127.0.0.1", port=29999)
collector = TelemetryCollector(client)
```

## Pas 2: Layout del Dashboard

```python
app.layout = html.Div([
    html.H1("LFS Telemetria en Temps Real", 
            style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        # Indicadors principals
        html.Div([
            html.H3("Velocitat", style={'textAlign': 'center'}),
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
            html.H3("Marxa", style={'textAlign': 'center'}),
            html.H2(id='gear-indicator',
                   children='N',
                   style={'textAlign': 'center', 'color': '#2ecc71'})
        ], className='four columns'),
    ], className='row'),
    
    # Gràfics
    html.Div([
        dcc.Graph(id='speed-graph'),
        dcc.Graph(id='rpm-graph'),
    ]),
    
    html.Div([
        dcc.Graph(id='track-map'),
    ]),
    
    # Interval per actualitzacions
    dcc.Interval(
        id='interval-component',
        interval=100,  # milliseconds
        n_intervals=0
    )
])
```

## Pas 3: Callbacks per Actualitzacions

```python
@app.callback(
    [Output('speed-indicator', 'children'),
     Output('rpm-indicator', 'children'),
     Output('gear-indicator', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_indicators(n):
    """Actualitza indicadors principals."""
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
    """Actualitza gràfic de velocitat."""
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
        name='Velocitat',
        line=dict(color='#e74c3c', width=2)
    ))
    
    fig.update_layout(
        title='Velocitat al llarg del temps',
        xaxis_title='Temps',
        yaxis_title='Velocitat (km/h)',
        hovermode='x unified'
    )
    
    return fig


@app.callback(
    Output('track-map', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_track_map(n):
    """Actualitza mapa del circuit."""
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
        name='Traçada'
    ))
    
    fig.update_layout(
        title='Mapa del Circuit',
        xaxis_title='Posició X',
        yaxis_title='Posició Y',
        hovermode='closest'
    )
    
    return fig
```

## Pas 4: Executar el Dashboard

```python
def main():
    """Funció principal."""
    logger.info("Iniciant dashboard...")
    
    # Connectar a LFS
    try:
        client.connect()
        client.initialize()
        logger.info("✓ Connectat a LFS")
    except Exception as e:
        logger.error(f"✗ Error de connexió: {e}")
        return
    
    # Iniciar recollida
    collector.start()
    logger.info("✓ Recollida de telemetria iniciada")
    
    # Executar dashboard
    logger.info("Dashboard disponible a: http://localhost:8050")
    app.run_server(debug=True, port=8050)


if __name__ == '__main__':
    main()
```

## Funcionalitats Avançades

### Alertes Personalitzades

```python
def check_alerts(telemetry):
    """Comprova condicions d'alerta."""
    alerts = []
    
    speed = telemetry.get('speed', 0)
    rpm = telemetry.get('rpm', 0)
    
    if speed > 200:
        alerts.append("⚠️ Velocitat alta!")
    
    if rpm > 7500:
        alerts.append("🔴 RPM alt - canvia de marxa!")
    
    return alerts
```

### Gràfic de Rendiment

```python
@app.callback(
    Output('performance-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_performance(n):
    """Mostra rendiment comparatiu."""
    history = collector.get_telemetry_history(limit=100)
    
    # Calcular eficiència
    efficiency = [
        h.get('speed', 0) / max(h.get('rpm', 1), 1) * 1000
        for h in history
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=np.mean(efficiency) if efficiency else 0,
        title={'text': "Eficiència"},
        gauge={'axis': {'range': [None, 50]}}
    ))
    
    return fig
```

## Personalització de Temes

```python
app.layout = html.Div([
    # ... contingut anterior ...
], style={
    'backgroundColor': '#ecf0f1',
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
})
```

## Executar

```bash
python dashboard_realtime.py
```

Obre el navegador a: **http://localhost:8050**

## Consells

- Ajusta `interval` segons necessitat (100-500ms recomanat)
- Limita històric per evitar problemes de memòria
- Utilitza `dcc.Store` per compartir dades entre callbacks
- Considera `dash-bootstrap-components` per millor disseny

## Pròxims Passos

- **[Tutorial 4: Anàlisi Avançada](04-advanced-analysis.md)**
- **[Documentació de Visualització](../visualization.md)**

---

Ara tens un dashboard professional! 📊
