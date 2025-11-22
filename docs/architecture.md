# LFS-Ayats System Architecture

This documentation describes the internal architecture of the LFS-Ayats system, its main components, design patterns used, and data flow.

## Overview

LFS-Ayats is a modular telemetry system for Live for Speed built with Python. It uses a layered architecture that separates responsibilities and facilitates maintenance and extension.

```
┌─────────────────────────────────────────────────────┐
│                   Presentation                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Dashboard   │  │   REST API   │  │   CLI    │  │
│  │   (Dash)     │  │  (FastAPI)   │  │  Tools   │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                  Business Logic                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Analysis    │  │Visualization │  │  Export  │  │
│  │    Module    │  │    Module    │  │  Module  │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                    Data Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Telemetry   │  │   Database   │  │  Config  │  │
│  │  Collector   │  │  Repository  │  │  Manager │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                 Connection Layer                     │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  InSim       │  │   Packet     │                 │
│  │  Client      │  │   Handler    │                 │
│  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Live for Speed     │
              │  (InSim Protocol)   │
              └─────────────────────┘
```

## Main Components

### 1. Connection Module (`src/connection/`)

**Responsibility**: Manages communication with the LFS server through the InSim protocol.

#### `InSimClient`

```python
class InSimClient:
    """Client to connect with LFS via InSim."""
    
    def __init__(self, host, port, admin_password, app_name):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # ...
    
    def connect(self):
        """Establishes TCP connection with LFS."""
        
    def initialize(self):
        """Sends IS_ISI packet to initialize InSim."""
        
    def send_packet(self, packet):
        """Sends binary packet to the server."""
        
    def receive_packet(self):
        """Receives and parses packet from the server."""
```

**Dependencies**:
- `socket` - TCP/UDP communication
- `struct` - Binary packet serialization

**Interactions**:
- Receives packets from LFS
- Sends control packets to LFS
- Notifies `PacketHandler` of new packets

#### `PacketHandler`

```python
class PacketHandler:
    """Parses received InSim packets."""
    
    def handle_packet(self, raw_data):
        """Determines packet type and calls appropriate handler."""
        
    def parse_is_mci(self, data):
        """Parses Multi Car Info packet (telemetry)."""
        
    def parse_is_lap(self, data):
        """Parses completed lap packet."""
```

**Pattern**: Strategy Pattern for handling different packet types

### 2. Telemetry Module (`src/telemetry/`)

**Responsibility**: Collection, validation, and processing of telemetry data.

#### `TelemetryCollector`

```python
class TelemetryCollector:
    """Collects and stores telemetry in real-time."""
    
    def __init__(self, client: InSimClient, max_history: int = 10000):
        self.client = client
        self.callbacks = {}
        self.telemetry_history = defaultdict(list)
        
    def start(self):
        """Starts collection in background thread."""
        
    def stop(self):
        """Stops collection."""
        
    def register_callback(self, event_type, callback):
        """Registers callback for event type."""
```

**Pattern**: Observer Pattern for callbacks

**Telemetry Buffer**:
```python
class TelemetryBuffer:
    """Circular buffer with auto-flush."""
    
    def __init__(self, max_size=1000, auto_flush=True):
        self.buffer = deque(maxlen=max_size)
        
    def add(self, data):
        """Adds data to buffer."""
        
    def flush(self):
        """Empties buffer and calls callbacks."""
```

#### `TelemetryProcessor`

```python
class TelemetryProcessor:
    """Validates and processes telemetry data."""
    
    def validate_speed(self, speed: float) -> bool:
        """Validates speed range."""
        
    def validate_rpm(self, rpm: int) -> bool:
        """Validates RPM range."""
        
    def calculate_derived_values(self, telemetry):
        """Calculates derived values (acceleration, etc)."""
```

**Validations**:
- Valid ranges for each variable
- Anomalous value detection
- Derived metrics calculation

### 3. Analysis Module (`src/analysis/`)

**Responsibility**: Advanced analysis of telemetry data.

```python
class TelemetryAnalyzer:
    """Analyzes telemetry data."""
    
    def detect_anomalies(self, data):
        """Detects anomalies using Isolation Forest."""
        
    def predict_lap_time(self, features):
        """Predicts lap time using ML."""
        
    def analyze_sectors(self, lap_data):
        """Analyzes sectors of a lap."""
```

**Algorithms**:
- Isolation Forest for anomalies
- Linear Regression for predictions
- Clustering with K-means

### 4. Visualization Module (`src/visualization/`)

**Responsibility**: Generation of charts and interactive dashboards.

#### Components

```python
# Main dashboard (Dash)
class TelemetryDashboard:
    """Real-time web dashboard."""
    
    def __init__(self, collector):
        self.app = dash.Dash(__name__)
        self.collector = collector
        
    def create_layout(self):
        """Creates dashboard layout."""
        
    def run(self, port=8050):
        """Runs web server."""


# Lap comparator
class LapComparator:
    """Compares multiple laps."""
    
    def add_lap(self, name, data):
        """Adds lap for comparison."""
        
    def create_comparison_plot(self):
        """Generates comparison chart."""


# Specific charts
def create_speed_vs_distance_plot(telemetry):
    """Creates speed vs distance chart."""

def create_track_map(telemetry, show_speed_colors=True):
    """Creates track map with speeds."""
```

**Technologies**:
- Plotly for interactive charts
- Dash for web dashboard
- Matplotlib for static charts

### 5. Export Module (`src/export/`)

**Responsibility**: Data export to various formats.

```python
class CSVExporter:
    """Exports telemetry to CSV."""
    
    def export(self, data, filepath):
        """Exports data to CSV."""


class JSONExporter:
    """Exports telemetry to JSON."""
    
    def export(self, data, filepath):
        """Exports data to JSON."""


class DatabaseExporter:
    """Exports telemetry to database."""
    
    def export(self, data, session_info):
        """Stores data in DB."""
```

**Pattern**: Factory Pattern for creating exporters

### 6. Database Module (`src/database/`)

**Responsibility**: Data persistence with ORM.

```python
# SQLAlchemy Models
class Session(Base):
    __tablename__ = 'sessions'
    # ...

class Lap(Base):
    __tablename__ = 'laps'
    # ...

class TelemetryPoint(Base):
    __tablename__ = 'telemetry_points'
    # ...


# Repository for data access
class TelemetryRepository:
    """Data access layer."""
    
    def create_session(self, **kwargs):
        """Creates new session."""
        
    def get_best_laps(self, track=None, limit=10):
        """Gets best laps."""
        
    def query_telemetry(self, filters):
        """Queries telemetry with filters."""
```

**Pattern**: Repository Pattern for DB abstraction

### 7. REST API (`src/api/`)

**Responsibility**: Provides programmatic access via HTTP.

```python
# FastAPI application
app = FastAPI(title="LFS-Ayats API")

# Routers
@app.get("/api/v1/sessions")
def list_sessions():
    """Lists sessions."""

@app.get("/api/v1/{lap_id}/telemetry")
def get_lap_telemetry(lap_id: int):
    """Gets telemetry for a lap."""

@app.websocket("/api/v1/telemetry/live")
async def telemetry_stream(websocket):
    """Real-time telemetry streaming."""
```

**Features**:
- RESTful endpoints
- WebSocket for streaming
- Automatic documentation (Swagger)
- CORS and authentication

### 8. Configuration (`src/config/`)

**Responsibility**: Centralized configuration management.

```python
class Settings:
    """Application configuration."""
    
    def __init__(self, config_file="config.yaml"):
        self.config = self._load_config(config_file)
        
    def get(self, key, default=None):
        """Gets configuration value."""
```

**Pattern**: Singleton Pattern for global configuration

## Data Flow

### 1. Telemetry Collection

```
LFS Server
    │
    │ (1) InSim Packets via TCP
    ▼
InSimClient
    │
    │ (2) Raw Binary Data
    ▼
PacketHandler
    │
    │ (3) Parsed Packet Data
    ▼
TelemetryCollector
    │
    ├─► (4a) Callbacks notified
    │
    ├─► (4b) Buffer updated
    │
    └─► (4c) History saved
```

### 2. Real-Time Visualization

```
TelemetryCollector
    │
    │ (1) get_latest_telemetry()
    ▼
Dashboard (Dash)
    │
    │ (2) Update callbacks
    ▼
Plotly Graphs
    │
    │ (3) JSON data
    ▼
Web Browser
```

### 3. Analysis and Export

```
TelemetryCollector
    │
    │ (1) get_telemetry_history()
    ▼
TelemetryAnalyzer
    │
    │ (2) Processed data
    ▼
Exporter
    │
    ├─► (3a) CSV File
    ├─► (3b) JSON File
    └─► (3c) Database
```

## Design Patterns Used

### 1. Observer Pattern (Callbacks)

```python
# TelemetryCollector acts as Subject
collector.register_callback("telemetry", my_callback)

# When data arrives, notifies observers
def _trigger_callbacks(self, event_type, data):
    for callback in self.callbacks.get(event_type, []):
        callback(data)
```

**Advantages**:
- Decoupling between collection and processing
- Multiple consumers can listen to same event
- Facilitates extension without modifying existing code

### 2. Repository Pattern (Database)

```python
# Data access abstraction
class TelemetryRepository:
    def get_session(self, session_id):
        return self.db_session.query(Session).filter_by(id=session_id).first()
```

**Advantages**:
- Separates business logic from persistence
- Facilitates testing with mock repositories
- Allows changing DB implementation without affecting code

### 3. Factory Pattern (Exporters)

```python
class ExporterFactory:
    @staticmethod
    def create_exporter(format_type):
        if format_type == "csv":
            return CSVExporter()
        elif format_type == "json":
            return JSONExporter()
        # ...
```

**Advantages**:
- Centralized object creation
- Facilitates adding new formats
- Client doesn't need to know implementations

### 4. Strategy Pattern (Packet Handlers)

```python
class PacketHandler:
    def __init__(self):
        self.handlers = {
            PacketType.IS_MCI: self.parse_is_mci,
            PacketType.IS_LAP: self.parse_is_lap,
            # ...
        }
    
    def handle_packet(self, packet_type, data):
        handler = self.handlers.get(packet_type)
        if handler:
            return handler(data)
```

**Advantages**:
- Interchangeable algorithms
- Easy to add new packet types
- Reduction of conditionals

### 5. Singleton Pattern (Configuration)

```python
class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Advantages**:
- Global access point to configuration
- Avoids multiple file loads
- Guarantees single instance

## Threading and Concurrency

### Threading Model

```python
# TelemetryCollector uses separate thread for collection
class TelemetryCollector:
    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._collection_loop)
        self._thread.daemon = True
        self._thread.start()
    
    def _collection_loop(self):
        while self._running:
            packet = self.client.receive_packet()
            self._process_packet(packet)
```

**Synchronization**:
- `threading.Lock()` to protect shared data
- `queue.Queue()` for inter-thread communication
- Daemon threads for automatic cleanup

### Async/Await (API and WebSocket)

```python
# FastAPI uses async for better performance
@app.websocket("/api/v1/telemetry/live")
async def telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await get_latest_telemetry()
        await websocket.send_json(data)
```

## Error Handling

### Error Handling Strategy

1. **Input Validation**:
   ```python
   def validate_speed(self, speed):
       if not 0 <= speed <= 500:
           raise ValueError(f"Invalid speed: {speed}")
   ```

2. **Automatic Recovery**:
   ```python
   def connect(self, max_retries=3):
       for attempt in range(max_retries):
           try:
               self._establish_connection()
               return True
           except ConnectionError:
               time.sleep(1)
       raise ConnectionError("Max retries exceeded")
   ```

3. **Detailed Logging**:
   ```python
   logger.error(f"Failed to process packet: {e}", exc_info=True)
   ```

4. **Fallbacks**:
   ```python
   def get_telemetry(self):
       try:
           return self._get_from_cache()
       except CacheError:
           return self._get_from_database()
   ```

## Performance and Optimization

### Optimization Strategies

1. **Circular Buffer**:
   ```python
   self.buffer = deque(maxlen=1000)  # Prevents indefinite growth
   ```

2. **Batch Operations**:
   ```python
   db_session.bulk_insert_mappings(TelemetryPoint, batch)
   ```

3. **Lazy Loading**:
   ```python
   telemetry_points = relationship("TelemetryPoint", lazy="dynamic")
   ```

4. **Caching**:
   ```python
   @lru_cache(maxsize=128)
   def calculate_statistics(self, lap_id):
       # ...
   ```

5. **Database Indexes**:
   ```python
   Index('idx_lap_time', Lap.lap_time)
   Index('idx_session_track', Session.track)
   ```

## Extensibility

### Adding New Packet Type

1. Define type in `PacketType` enum
2. Create parser method in `PacketHandler`
3. Register handler in dictionary
4. Document packet structure

### Adding New Export Format

1. Create class that inherits from `BaseExporter`
2. Implement `export()` method
3. Add to `ExporterFactory`
4. Write tests

### Adding New Visualization

1. Create function in `src/visualization/plots.py`
2. Follow naming convention `create_*_plot()`
3. Return Plotly figure
4. Document parameters

## References

- [InSim Protocol](insim_protocol.md)
- [API Reference](api_reference.md)
- [Testing Guide](contributing/testing-guide.md)

---

This architecture enables a robust, maintainable, and extensible system. 🏗️
