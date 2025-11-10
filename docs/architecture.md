# Arquitectura del Sistema LFS-Ayats

Aquesta documentació descriu l'arquitectura interna del sistema LFS-Ayats, els seus components principals, patrons de disseny utilitzats i el flux de dades.

## Visió General

LFS-Ayats és un sistema modular de telemetria per Live for Speed construït amb Python. Utilitza una arquitectura en capes que separa responsabilitats i facilita el manteniment i extensió.

```
┌─────────────────────────────────────────────────────┐
│                   Presentació                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Dashboard   │  │   REST API   │  │   CLI    │  │
│  │   (Dash)     │  │  (FastAPI)   │  │  Tools   │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                  Lògica de Negoci                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Analysis    │  │Visualization │  │  Export  │  │
│  │    Module    │  │    Module    │  │  Module  │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                  Capa de Dades                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Telemetry   │  │   Database   │  │  Config  │  │
│  │  Collector   │  │  Repository  │  │  Manager │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                  Capa de Connexió                    │
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

## Components Principals

### 1. Mòdul de Connexió (`src/connection/`)

**Responsabilitat**: Gestió de la comunicació amb el servidor LFS mitjançant el protocol InSim.

#### `InSimClient`

```python
class InSimClient:
    """Client per connectar amb LFS via InSim."""
    
    def __init__(self, host, port, admin_password, app_name):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # ...
    
    def connect(self):
        """Estableix connexió TCP amb LFS."""
        
    def initialize(self):
        """Envia paquet IS_ISI per inicialitzar InSim."""
        
    def send_packet(self, packet):
        """Envia paquet binari al servidor."""
        
    def receive_packet(self):
        """Rep i parseja paquet del servidor."""
```

**Dependències**:
- `socket` - Comunicació TCP/UDP
- `struct` - Serialització binària de paquets

**Interaccions**:
- Rep paquets de LFS
- Envia paquets de control a LFS
- Notifica `PacketHandler` de nous paquets

#### `PacketHandler`

```python
class PacketHandler:
    """Parseja paquets InSim rebuts."""
    
    def handle_packet(self, raw_data):
        """Determina tipus de paquet i crida handler apropiat."""
        
    def parse_is_mci(self, data):
        """Parseja paquet Multi Car Info (telemetria)."""
        
    def parse_is_lap(self, data):
        """Parseja paquet de volta completada."""
```

**Patró**: Strategy Pattern per gestió de diferents tipus de paquets

### 2. Mòdul de Telemetria (`src/telemetry/`)

**Responsabilitat**: Recollida, validació i processament de dades telemètriques.

#### `TelemetryCollector`

```python
class TelemetryCollector:
    """Recull i emmagatzema telemetria en temps real."""
    
    def __init__(self, client: InSimClient, max_history: int = 10000):
        self.client = client
        self.callbacks = {}
        self.telemetry_history = defaultdict(list)
        
    def start(self):
        """Inicia recollida en background thread."""
        
    def stop(self):
        """Atura recollida."""
        
    def register_callback(self, event_type, callback):
        """Registra callback per tipus d'esdeveniment."""
```

**Patró**: Observer Pattern per callbacks

**Buffer de Telemetria**:
```python
class TelemetryBuffer:
    """Buffer circular amb auto-flush."""
    
    def __init__(self, max_size=1000, auto_flush=True):
        self.buffer = deque(maxlen=max_size)
        
    def add(self, data):
        """Afegeix dada al buffer."""
        
    def flush(self):
        """Buida buffer i crida callbacks."""
```

#### `TelemetryProcessor`

```python
class TelemetryProcessor:
    """Valida i processa dades telemètriques."""
    
    def validate_speed(self, speed: float) -> bool:
        """Valida rang de velocitat."""
        
    def validate_rpm(self, rpm: int) -> bool:
        """Valida rang de RPM."""
        
    def calculate_derived_values(self, telemetry):
        """Calcula valors derivats (acceleració, etc)."""
```

**Validacions**:
- Rangs vàlids per cada variable
- Detecció de valors anòmals
- Càlcul de mètriques derivades

### 3. Mòdul d'Anàlisi (`src/analysis/`)

**Responsabilitat**: Anàlisi avançada de dades telemètriques.

```python
class TelemetryAnalyzer:
    """Analitza dades telemètriques."""
    
    def detect_anomalies(self, data):
        """Detecta anomalies amb Isolation Forest."""
        
    def predict_lap_time(self, features):
        """Prediu temps de volta amb ML."""
        
    def analyze_sectors(self, lap_data):
        """Analitza sectors d'una volta."""
```

**Algorismes**:
- Isolation Forest per anomalies
- Linear Regression per prediccions
- Clustering amb K-means

### 4. Mòdul de Visualització (`src/visualization/`)

**Responsabilitat**: Generació de gràfics i dashboards interactius.

#### Components

```python
# Dashboard principal (Dash)
class TelemetryDashboard:
    """Dashboard web en temps real."""
    
    def __init__(self, collector):
        self.app = dash.Dash(__name__)
        self.collector = collector
        
    def create_layout(self):
        """Crea layout del dashboard."""
        
    def run(self, port=8050):
        """Executa servidor web."""


# Comparador de voltes
class LapComparator:
    """Compara múltiples voltes."""
    
    def add_lap(self, name, data):
        """Afegeix volta per comparar."""
        
    def create_comparison_plot(self):
        """Genera gràfic de comparació."""


# Gràfics específics
def create_speed_vs_distance_plot(telemetry):
    """Crea gràfic velocitat vs distància."""

def create_track_map(telemetry, show_speed_colors=True):
    """Crea mapa del circuit amb velocitats."""
```

**Tecnologies**:
- Plotly per gràfics interactius
- Dash per dashboard web
- Matplotlib per gràfics estàtics

### 5. Mòdul d'Exportació (`src/export/`)

**Responsabilitat**: Exportació de dades a diversos formats.

```python
class CSVExporter:
    """Exporta telemetria a CSV."""
    
    def export(self, data, filepath):
        """Exporta dades a CSV."""


class JSONExporter:
    """Exporta telemetria a JSON."""
    
    def export(self, data, filepath):
        """Exporta dades a JSON."""


class DatabaseExporter:
    """Exporta telemetria a base de dades."""
    
    def export(self, data, session_info):
        """Emmagatzema dades a DB."""
```

**Patró**: Factory Pattern per crear exporters

### 6. Mòdul de Base de Dades (`src/database/`)

**Responsabilitat**: Persistència de dades amb ORM.

```python
# Models SQLAlchemy
class Session(Base):
    __tablename__ = 'sessions'
    # ...

class Lap(Base):
    __tablename__ = 'laps'
    # ...

class TelemetryPoint(Base):
    __tablename__ = 'telemetry_points'
    # ...


# Repository per accés a dades
class TelemetryRepository:
    """Capa d'accés a dades."""
    
    def create_session(self, **kwargs):
        """Crea nova sessió."""
        
    def get_best_laps(self, track=None, limit=10):
        """Obté millors voltes."""
        
    def query_telemetry(self, filters):
        """Consulta telemetria amb filtres."""
```

**Patró**: Repository Pattern per abstracció de DB

### 7. REST API (`src/api/`)

**Responsabilitat**: Proporcionar accés programàtic via HTTP.

```python
# FastAPI application
app = FastAPI(title="LFS-Ayats API")

# Routers
@app.get("/api/v1/sessions")
def list_sessions():
    """Llista sessions."""

@app.get("/api/v1/{lap_id}/telemetry")
def get_lap_telemetry(lap_id: int):
    """Obté telemetria d'una volta."""

@app.websocket("/api/v1/telemetry/live")
async def telemetry_stream(websocket):
    """Streaming de telemetria en temps real."""
```

**Funcionalitats**:
- Endpoints RESTful
- WebSocket per streaming
- Documentació automàtica (Swagger)
- CORS i autenticació

### 8. Configuració (`src/config/`)

**Responsabilitat**: Gestió centralitzada de configuració.

```python
class Settings:
    """Configuració de l'aplicació."""
    
    def __init__(self, config_file="config.yaml"):
        self.config = self._load_config(config_file)
        
    def get(self, key, default=None):
        """Obté valor de configuració."""
```

**Patró**: Singleton Pattern per configuració global

## Flux de Dades

### 1. Recollida de Telemetria

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
    ├─► (4a) Callbacks notificats
    │
    ├─► (4b) Buffer actualitzat
    │
    └─► (4c) History guardat
```

### 2. Visualització en Temps Real

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

### 3. Anàlisi i Exportació

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

## Patrons de Disseny Utilitzats

### 1. Observer Pattern (Callbacks)

```python
# TelemetryCollector actua com a Subject
collector.register_callback("telemetry", my_callback)

# Quan arriben dades, notifica observers
def _trigger_callbacks(self, event_type, data):
    for callback in self.callbacks.get(event_type, []):
        callback(data)
```

**Avantatges**:
- Desacoblament entre recollida i processament
- Múltiples consumers poden escoltar mateix esdeveniment
- Facilita extensió sense modificar codi existent

### 2. Repository Pattern (Base de Dades)

```python
# Abstracció de l'accés a dades
class TelemetryRepository:
    def get_session(self, session_id):
        return self.db_session.query(Session).filter_by(id=session_id).first()
```

**Avantatges**:
- Separa lògica de negoci de persistència
- Facilita testing amb mock repositories
- Permet canviar implementació de DB sense afectar codi

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

**Avantatges**:
- Creació d'objectes centralitzada
- Facilita afegir nous formats
- Client no necessita conèixer implementacions

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

**Avantatges**:
- Algoritmes intercanviables
- Fàcil afegir nous tipus de paquets
- Reducció de condicionals

### 5. Singleton Pattern (Configuració)

```python
class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Avantatges**:
- Punt d'accés global a configuració
- Evita múltiples càrregues del fitxer
- Garanteix una sola instància

## Threading i Concurrència

### Model de Threading

```python
# TelemetryCollector utilitza thread separat per recollida
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

**Sincronització**:
- `threading.Lock()` per protegir dades compartides
- `queue.Queue()` per comunicació entre threads
- Threads daemon per cleanup automàtic

### Async/Await (API i WebSocket)

```python
# FastAPI utilitza async per millor rendiment
@app.websocket("/api/v1/telemetry/live")
async def telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await get_latest_telemetry()
        await websocket.send_json(data)
```

## Gestió d'Errors

### Estratègia de Gestió d'Errors

1. **Validació d'Entrada**:
   ```python
   def validate_speed(self, speed):
       if not 0 <= speed <= 500:
           raise ValueError(f"Invalid speed: {speed}")
   ```

2. **Recuperació Automàtica**:
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

3. **Logging Detallat**:
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

## Rendiment i Optimització

### Estratègies d'Optimització

1. **Buffer Circular**:
   ```python
   self.buffer = deque(maxlen=1000)  # Evita creixement indefinit
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

5. **Índexs de Base de Dades**:
   ```python
   Index('idx_lap_time', Lap.lap_time)
   Index('idx_session_track', Session.track)
   ```

## Extensibilitat

### Afegir Nou Tipus de Paquet

1. Definir tipus a `PacketType` enum
2. Crear mètode parser a `PacketHandler`
3. Registrar handler al diccionari
4. Documentar estructura del paquet

### Afegir Nou Format d'Exportació

1. Crear classe que hereta de `BaseExporter`
2. Implementar mètode `export()`
3. Afegir a `ExporterFactory`
4. Escriure tests

### Afegir Nova Visualització

1. Crear funció a `src/visualization/plots.py`
2. Seguir convenció de noms `create_*_plot()`
3. Retornar figura de Plotly
4. Documentar paràmetres

## Referències

- [Protocol InSim](insim_protocol.md)
- [API Reference](api_reference.md)
- [Testing Guide](contributing/testing-guide.md)

---

Aquesta arquitectura permet un sistema robust, mantenible i extensible. 🏗️
