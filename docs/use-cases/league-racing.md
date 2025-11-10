# Cas d'Ús: Carreres de Lliga

Guia completa per utilitzar LFS-Ayats en un entorn de carreres de lliga amb múltiples pilots.

## Escenari

**League Racing Team** organitza una lliga de carreres amb:
- 20 pilots participants
- Carreres setmanals
- Classificació i cursa
- Necessitat d'analitzar rendiment de pilots
- Comparacions entre pilots
- Seguiment de progressió

## Objectius

1. Recollir telemetria de tots els pilots durant les sessions
2. Analitzar rendiment individual i comparar pilots
3. Identificar millors voltes i estratègies
4. Generar reports automàtics post-carrera
5. Mantenir històric de tota la temporada

## Arquitectura Proposada

```
┌─────────────────┐
│  Servidor LFS   │  Port 29999 (InSim)
│   (Dedicat)     │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ LFS-Ayats│  Servidor central
    │  Server  │  PostgreSQL DB
    └────┬─────┘
         │
    ┌────▼──────────────────┐
    │   Dashboard Web       │
    │  (Dash) Port 8050     │
    └───────────────────────┘
    ┌───────────────────────┐
    │   REST API            │
    │  (FastAPI) Port 8000  │
    └───────────────────────┘
```

## Pas 1: Configuració del Servidor

### 1.1 Configurar Base de Dades

```bash
# Instal·lar PostgreSQL
sudo apt install postgresql

# Crear base de dades
sudo -u postgres psql
CREATE DATABASE league_telemetry;
CREATE USER league_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE league_telemetry TO league_user;
```

### 1.2 Configurar LFS-Ayats

`config_league.yaml`:
```yaml
insim:
  host: "YOUR_SERVER_IP"
  port: 29999
  admin_password: "admin_pass"
  app_name: "LeagueMonitor"
  interval: 50  # Alta freqüència per competició

database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  database: "league_telemetry"
  user: "league_user"
  password: "secure_password"

telemetry:
  collect_all_players: true
  save_to_database: true
  export_csv: true
  export_directory: "/data/league/races"

api:
  enabled: true
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["*"]

dashboard:
  enabled: true
  port: 8050
  update_interval: 100
```

### 1.3 Script Principal

`league_monitor.py`:
```python
"""
Monitor de telemetria per lliga.
Recull dades de tots els pilots i genera reports.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime

from src.connection import InSimClient
from src.telemetry import TelemetryCollector
from src.database import setup_database, TelemetryRepository
from src.export import CSVExporter
from src.utils import setup_logger

logger = setup_logger("league_monitor", "INFO")


class LeagueMonitor:
    """Monitor de telemetria per lliga."""
    
    def __init__(self, config_file="config_league.yaml"):
        """Inicialitza monitor."""
        self.config = self._load_config(config_file)
        self.db_session = None
        self.client = None
        self.collector = None
        self.race_session_id = None
    
    def _load_config(self, config_file):
        """Carrega configuració."""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def setup(self):
        """Configura tots els components."""
        logger.info("=== Configurant League Monitor ===")
        
        # Base de dades
        db_config = self.config['database']
        self.db_session = setup_database(
            f"postgresql://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        logger.info("✓ Base de dades connectada")
        
        # InSim
        insim_config = self.config['insim']
        self.client = InSimClient(
            host=insim_config['host'],
            port=insim_config['port'],
            admin_password=insim_config['admin_password'],
            app_name=insim_config['app_name']
        )
        self.client.connect()
        self.client.initialize()
        logger.info(f"✓ Connectat a servidor: {insim_config['host']}")
        
        # Col·lector
        self.collector = TelemetryCollector(self.client)
        self._setup_callbacks()
        logger.info("✓ Col·lector configurat")
    
    def _setup_callbacks(self):
        """Configura callbacks per esdeveniments."""
        
        def on_race_start(data):
            """Callback quan comença carrera."""
            logger.info("🏁 Carrera iniciada!")
            repo = TelemetryRepository(self.db_session)
            session = repo.create_session(
                start_time=datetime.now(),
                track=data.get('track', 'Unknown'),
                session_type='race'
            )
            self.race_session_id = session.id
            logger.info(f"   Sessió ID: {self.race_session_id}")
        
        def on_lap_completed(lap_data):
            """Callback quan es completa volta."""
            player = lap_data.get('player_name', 'Unknown')
            lap_time = lap_data.get('lap_time', 0)
            logger.info(f"🏁 {player} - Volta completada: {lap_time:.3f}s")
            
            # Guardar a DB
            if self.race_session_id:
                repo = TelemetryRepository(self.db_session)
                repo.create_lap(
                    session_id=self.race_session_id,
                    player_name=player,
                    lap_number=lap_data.get('lap_number', 0),
                    lap_time=lap_time
                )
        
        def on_race_end(data):
            """Callback quan acaba carrera."""
            logger.info("🏁 Carrera finalitzada!")
            self.generate_race_report()
        
        self.collector.register_callback('race_start', on_race_start)
        self.collector.register_callback('lap', on_lap_completed)
        self.collector.register_callback('race_end', on_race_end)
    
    def start_monitoring(self):
        """Inicia monitorització."""
        logger.info("🚀 Iniciant monitorització...")
        self.collector.start()
        logger.info("✓ Monitorització activa")
        
        try:
            # Mantenir execució
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Aturant monitor...")
            self.stop()
    
    def stop(self):
        """Atura monitor."""
        if self.collector:
            self.collector.stop()
        if self.client:
            self.client.disconnect()
        logger.info("✓ Monitor aturat")
    
    def generate_race_report(self):
        """Genera report de carrera."""
        if not self.race_session_id:
            return
        
        logger.info("\n=== Generant Report de Carrera ===")
        
        repo = TelemetryRepository(self.db_session)
        session = repo.get_session(self.race_session_id, include_laps=True)
        
        # Exportar a CSV
        export_dir = Path(self.config['telemetry']['export_directory'])
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = export_dir / f"race_{self.race_session_id}_{timestamp}.csv"
        
        # Preparar dades
        data = []
        for lap in session.laps:
            for point in lap.telemetry_points:
                data.append({
                    'session_id': session.id,
                    'player': lap.player_name,
                    'lap_number': lap.lap_number,
                    'timestamp': point.timestamp,
                    'speed': point.speed,
                    'rpm': point.rpm,
                    'gear': point.gear,
                    'pos_x': point.pos_x,
                    'pos_y': point.pos_y
                })
        
        # Exportar
        exporter = CSVExporter(str(csv_file))
        exporter.export(data)
        
        logger.info(f"✓ Report exportat: {csv_file}")
        
        # Estadístiques
        lap_times = [lap.lap_time for lap in session.laps]
        if lap_times:
            logger.info(f"\n📊 Estadístiques de Carrera:")
            logger.info(f"   Total voltes: {len(lap_times)}")
            logger.info(f"   Millor volta: {min(lap_times):.3f}s")
            logger.info(f"   Mitjana: {sum(lap_times)/len(lap_times):.3f}s")


def main():
    """Funció principal."""
    monitor = LeagueMonitor("config_league.yaml")
    monitor.setup()
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
```

## Pas 2: Anàlisi Post-Carrera

`analyze_race.py`:
```python
"""
Analitza resultats de carrera i genera comparacions.
"""

from src.database import TelemetryRepository, setup_database
from src.visualization import LapComparator
import pandas as pd


def analyze_race(session_id: int):
    """Analitza una carrera."""
    db = setup_database("postgresql://...")
    repo = TelemetryRepository(db)
    
    session = repo.get_session(session_id, include_laps=True)
    
    # Agrupar per pilot
    pilots = {}
    for lap in session.laps:
        player = lap.player_name
        if player not in pilots:
            pilots[player] = []
        pilots[player].append(lap)
    
    # Millor volta de cada pilot
    print("\n🏆 Millors Voltes per Pilot:")
    for player, laps in pilots.items():
        best_lap = min(laps, key=lambda l: l.lap_time)
        print(f"   {player}: {best_lap.lap_time:.3f}s")
    
    # Comparar dos millors pilots
    sorted_pilots = sorted(
        pilots.items(),
        key=lambda x: min(l.lap_time for l in x[1])
    )
    
    if len(sorted_pilots) >= 2:
        p1_name, p1_laps = sorted_pilots[0]
        p2_name, p2_laps = sorted_pilots[1]
        
        p1_best = min(p1_laps, key=lambda l: l.lap_time)
        p2_best = min(p2_laps, key=lambda l: l.lap_time)
        
        # Comparació visual
        comparator = LapComparator()
        comparator.add_lap(p1_name, p1_best.telemetry_points)
        comparator.add_lap(p2_name, p2_best.telemetry_points)
        
        fig = comparator.create_comparison_plot()
        fig.write_html(f"comparison_{session_id}.html")
        
        print(f"\n📊 Comparació guardada: comparison_{session_id}.html")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Ús: python analyze_race.py <session_id>")
        sys.exit(1)
    
    analyze_race(int(sys.argv[1]))
```

## Pas 3: Dashboard Públic

Crear dashboard web accessible per tots els membres:

```python
# league_dashboard.py
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

app = Dash(__name__)

app.layout = html.Div([
    html.H1("League Racing - Live Telemetry"),
    
    dcc.Dropdown(
        id='driver-selector',
        options=[],  # Omplir dinàmicament
        multi=True
    ),
    
    dcc.Graph(id='live-positions'),
    dcc.Graph(id='speed-comparison'),
    
    dcc.Interval(id='update-interval', interval=1000)
])

# Callbacks per actualitzar...

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
```

## Consells per Lligues

1. **Backups Regulars**: Fes backup de la DB després de cada carrera
2. **Monitoritza Rendiment**: Servidor adequat per 20+ connexions
3. **Documentació**: Guia per pilots sobre com interpretar dades
4. **Privacitat**: Considera qui pot accedir a quines dades
5. **Automatització**: Scripts per reports automàtics

## Recursos

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Dash Multi-page Apps](https://dash.plotly.com/urls)

---

Perfecte per gestionar lligues de forma professional! 🏆
