# Use Case: League Racing

Complete guide for using LFS-Ayats in a league racing environment with multiple drivers.

## Scenario

**League Racing Team** organizes a racing league with:
- 20 participating drivers
- Weekly races
- Qualifying and race sessions
- Need to analyze driver performance
- Comparisons between drivers
- Progress tracking

## Objectives

1. Collect telemetry from all drivers during sessions
2. Analyze individual performance and compare drivers
3. Identify best laps and strategies
4. Generate automatic post-race reports
5. Maintain history for the entire season

## Proposed Architecture

```
┌─────────────────┐
│   LFS Server    │  Port 29999 (InSim)
│   (Dedicated)   │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ LFS-Ayats│  Central server
    │  Server  │  PostgreSQL DB
    └────┬─────┘
         │
    ┌────▼──────────────────┐
    │   Web Dashboard       │
    │  (Dash) Port 8050     │
    └───────────────────────┘
    ┌───────────────────────┐
    │   REST API            │
    │  (FastAPI) Port 8000  │
    └───────────────────────┘
```

## Step 1: Server Configuration

### 1.1 Configure Database

```bash
# Install PostgreSQL
sudo apt install postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE league_telemetry;
CREATE USER league_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE league_telemetry TO league_user;
```

### 1.2 Configure LFS-Ayats

`config_league.yaml`:
```yaml
insim:
  host: "YOUR_SERVER_IP"
  port: 29999
  admin_password: "admin_pass"
  app_name: "LeagueMonitor"
  interval: 50  # High frequency for competition

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

### 1.3 Main Script

`league_monitor.py`:
```python
"""
Telemetry monitor for league racing.
Collects data from all drivers and generates reports.
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
    """Telemetry monitor for league racing."""
    
    def __init__(self, config_file="config_league.yaml"):
        """Initialize monitor."""
        self.config = self._load_config(config_file)
        self.db_session = None
        self.client = None
        self.collector = None
        self.race_session_id = None
    
    def _load_config(self, config_file):
        """Load configuration."""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def setup(self):
        """Configure all components."""
        logger.info("=== Setting up League Monitor ===")
        
        # Database
        db_config = self.config['database']
        self.db_session = setup_database(
            f"postgresql://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        logger.info("✓ Database connected")
        
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
        logger.info(f"✓ Connected to server: {insim_config['host']}")
        
        # Collector
        self.collector = TelemetryCollector(self.client)
        self._setup_callbacks()
        logger.info("✓ Collector configured")
    
    def _setup_callbacks(self):
        """Configure callbacks for events."""
        
        def on_race_start(data):
            """Callback when race starts."""
            logger.info("🏁 Race started!")
            repo = TelemetryRepository(self.db_session)
            session = repo.create_session(
                start_time=datetime.now(),
                track=data.get('track', 'Unknown'),
                session_type='race'
            )
            self.race_session_id = session.id
            logger.info(f"   Session ID: {self.race_session_id}")
        
        def on_lap_completed(lap_data):
            """Callback when lap is completed."""
            player = lap_data.get('player_name', 'Unknown')
            lap_time = lap_data.get('lap_time', 0)
            logger.info(f"🏁 {player} - Lap completed: {lap_time:.3f}s")
            
            # Save to DB
            if self.race_session_id:
                repo = TelemetryRepository(self.db_session)
                repo.create_lap(
                    session_id=self.race_session_id,
                    player_name=player,
                    lap_number=lap_data.get('lap_number', 0),
                    lap_time=lap_time
                )
        
        def on_race_end(data):
            """Callback when race ends."""
            logger.info("🏁 Race finished!")
            self.generate_race_report()
        
        self.collector.register_callback('race_start', on_race_start)
        self.collector.register_callback('lap', on_lap_completed)
        self.collector.register_callback('race_end', on_race_end)
    
    def start_monitoring(self):
        """Start monitoring."""
        logger.info("🚀 Starting monitoring...")
        self.collector.start()
        logger.info("✓ Monitoring active")
        
        try:
            # Keep running
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping monitor...")
            self.stop()
    
    def stop(self):
        """Stop monitor."""
        if self.collector:
            self.collector.stop()
        if self.client:
            self.client.disconnect()
        logger.info("✓ Monitor stopped")
    
    def generate_race_report(self):
        """Generate race report."""
        if not self.race_session_id:
            return
        
        logger.info("\n=== Generating Race Report ===")
        
        repo = TelemetryRepository(self.db_session)
        session = repo.get_session(self.race_session_id, include_laps=True)
        
        # Export to CSV
        export_dir = Path(self.config['telemetry']['export_directory'])
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = export_dir / f"race_{self.race_session_id}_{timestamp}.csv"
        
        # Prepare data
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
        
        # Export
        exporter = CSVExporter(str(csv_file))
        exporter.export(data)
        
        logger.info(f"✓ Report exported: {csv_file}")
        
        # Statistics
        lap_times = [lap.lap_time for lap in session.laps]
        if lap_times:
            logger.info(f"\n📊 Race Statistics:")
            logger.info(f"   Total laps: {len(lap_times)}")
            logger.info(f"   Best lap: {min(lap_times):.3f}s")
            logger.info(f"   Average: {sum(lap_times)/len(lap_times):.3f}s")


def main():
    """Main function."""
    monitor = LeagueMonitor("config_league.yaml")
    monitor.setup()
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
```

## Step 2: Post-Race Analysis

`analyze_race.py`:
```python
"""
Analyzes race results and generates comparisons.
"""

from src.database import TelemetryRepository, setup_database
from src.visualization import LapComparator
import pandas as pd


def analyze_race(session_id: int):
    """Analyze a race."""
    db = setup_database("postgresql://...")
    repo = TelemetryRepository(db)
    
    session = repo.get_session(session_id, include_laps=True)
    
    # Group by driver
    pilots = {}
    for lap in session.laps:
        player = lap.player_name
        if player not in pilots:
            pilots[player] = []
        pilots[player].append(lap)
    
    # Best lap for each driver
    print("\n🏆 Best Laps per Driver:")
    for player, laps in pilots.items():
        best_lap = min(laps, key=lambda l: l.lap_time)
        print(f"   {player}: {best_lap.lap_time:.3f}s")
    
    # Compare two best drivers
    sorted_pilots = sorted(
        pilots.items(),
        key=lambda x: min(l.lap_time for l in x[1])
    )
    
    if len(sorted_pilots) >= 2:
        p1_name, p1_laps = sorted_pilots[0]
        p2_name, p2_laps = sorted_pilots[1]
        
        p1_best = min(p1_laps, key=lambda l: l.lap_time)
        p2_best = min(p2_laps, key=lambda l: l.lap_time)
        
        # Visual comparison
        comparator = LapComparator()
        comparator.add_lap(p1_name, p1_best.telemetry_points)
        comparator.add_lap(p2_name, p2_best.telemetry_points)
        
        fig = comparator.create_comparison_plot()
        fig.write_html(f"comparison_{session_id}.html")
        
        print(f"\n📊 Comparison saved: comparison_{session_id}.html")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python analyze_race.py <session_id>")
        sys.exit(1)
    
    analyze_race(int(sys.argv[1]))
```

## Step 3: Public Dashboard

Create a web dashboard accessible to all members:

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
        options=[],  # Fill dynamically
        multi=True
    ),
    
    dcc.Graph(id='live-positions'),
    dcc.Graph(id='speed-comparison'),
    
    dcc.Interval(id='update-interval', interval=1000)
])

# Callbacks for updating...

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
```

## Tips for Leagues

1. **Regular Backups**: Back up the DB after each race
2. **Monitor Performance**: Adequate server for 20+ connections
3. **Documentation**: Guide for drivers on how to interpret data
4. **Privacy**: Consider who can access which data
5. **Automation**: Scripts for automatic reports

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Dash Multi-page Apps](https://dash.plotly.com/urls)

---

Perfect for managing leagues professionally! 🏆
