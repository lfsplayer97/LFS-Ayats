# API Reference

Referència completa de l'API de LFS-Ayats.

## Mòdul `connection`

### `InSimClient`

Client per connectar-se al servidor LFS mitjançant InSim.

#### Constructor

```python
InSimClient(
    host: str = "127.0.0.1",
    port: int = 29999,
    admin_password: str = "",
    app_name: str = "LFS-Ayats",
    udp: bool = False
)
```

**Paràmetres:**
- `host`: IP del servidor LFS
- `port`: Port InSim (defecte 29999)
- `admin_password`: Contrasenya admin si cal
- `app_name`: Nom de l'aplicació (màx 16 caràcters)
- `udp`: Usar UDP en lloc de TCP

#### Mètodes

##### `connect() -> bool`

Estableix connexió amb el servidor.

**Returns:** `True` si exitós, `False` altrament

**Raises:** `ConnectionError` si no pot connectar

##### `initialize(flags: int = 0, interval: int = 0) -> None`

Inicialitza la connexió InSim.

**Paràmetres:**
- `flags`: Flags d'InSim (ISF_MCI, ISF_NLP, etc.)
- `interval`: Interval MCI/NLP en centèssimes de segon

##### `send_packet(packet: bytes) -> None`

Envia un paquet al servidor.

**Paràmetres:**
- `packet`: Paquet en format bytes

##### `receive_packet(timeout: Optional[float] = None) -> Optional[bytes]`

Rep un paquet del servidor.

**Paràmetres:**
- `timeout`: Temps d'espera màxim (None = bloqueig)

**Returns:** Paquet rebut o None

##### `disconnect() -> None`

Tanca la connexió amb el servidor.

##### `register_callback(packet_type: int, callback: Callable) -> None`

Registra un callback per un tipus de paquet.

**Paràmetres:**
- `packet_type`: Tipus de paquet (PacketType)
- `callback`: Funció a cridar

#### Exemple

```python
from src.connection import InSimClient

with InSimClient(host="127.0.0.1", port=29999) as client:
    client.initialize(flags=48, interval=100)
    
    while True:
        packet = client.receive_packet(timeout=1.0)
        if packet:
            # Processar paquet
            pass
```

### `PacketHandler`

Gestiona el processament de paquets InSim.

#### Mètodes

##### `parse_packet(data: bytes) -> Optional[PacketInfo]`

Parseja un paquet i extreu informació bàsica.

**Returns:** `PacketInfo` o None si invàlid

##### `process_packet(data: bytes) -> bool`

Processa un paquet i crida el handler corresponent.

**Returns:** `True` si processat correctament

##### `register_handler(packet_type: int, handler: Callable) -> None`

Registra un handler per un tipus de paquet.

##### `parse_version_packet(data: bytes) -> Optional[Dict[str, Any]]`

Parseja un paquet IS_VER.

##### `parse_state_packet(data: bytes) -> Optional[Dict[str, Any]]`

Parseja un paquet IS_STA.

##### `parse_mci_packet(data: bytes) -> Optional[Dict[str, Any]]`

Parseja un paquet IS_MCI (telemetria).

## Mòdul `telemetry`

### `TelemetryCollector`

Recull dades telemètriques del servidor LFS.

#### Constructor

```python
TelemetryCollector(client: InSimClient)
```

**Paràmetres:**
- `client`: Client InSim connectat

#### Mètodes

##### `start(interval: int = 100) -> None`

Inicia la recollida de telemetria.

**Paràmetres:**
- `interval`: Interval en ms (defecte 100ms = 10Hz)

##### `stop() -> None`

Atura la recollida de telemetria.

##### `get_latest_telemetry(plid: Optional[int] = None) -> Dict[int, CarTelemetry]`

Obté telemetria més recent.

**Paràmetres:**
- `plid`: Player ID específic (None = tots)

**Returns:** Dict amb telemetria per player ID

##### `get_telemetry_history(plid: int, limit: Optional[int] = None) -> List[CarTelemetry]`

Obté historial de telemetria.

**Paràmetres:**
- `plid`: Player ID
- `limit`: Nombre màxim de mostres (None = totes)

##### `clear_history(plid: Optional[int] = None) -> None`

Neteja l'historial de telemetria.

##### `register_callback(event_type: str, callback: Callable) -> None`

Registra un callback per esdeveniments.

**Event types:**
- `'car_update'`: Actualització de vehicle
- `'lap_complete'`: Volta completada
- `'split_time'`: Temps de sector
- `'player_join'`: Jugador uneix
- `'player_leave'`: Jugador deixa

#### Exemple

```python
from src.connection import InSimClient
from src.telemetry import TelemetryCollector

client = InSimClient()
client.connect()

collector = TelemetryCollector(client)

def on_car_update(telemetry):
    print(f"Speed: {telemetry.speed:.2f} m/s")

collector.register_callback('car_update', on_car_update)
collector.start(interval=100)

# ... després ...
collector.stop()
```

### `TelemetryProcessor`

Processa i valida dades telemètriques.

#### Constructor

```python
TelemetryProcessor(max_speed: float = 150.0)
```

#### Mètodes

##### `validate_telemetry(telemetry: CarTelemetry) -> bool`

Valida dades telemètriques.

**Returns:** `True` si vàlid

##### `process_telemetry(telemetry_list: List[CarTelemetry]) -> ProcessedTelemetry`

Processa telemetria i calcula estadístiques.

##### `calculate_statistics(telemetry_list: List[CarTelemetry]) -> Dict[str, Any]`

Calcula estadístiques detallades.

##### `filter_by_speed_range(telemetry_list, min_speed, max_speed) -> List`

Filtra per rang de velocitat.

##### `detect_anomalies(telemetry_list, threshold_stdev: float = 3.0) -> List[int]`

Detecta anomalies utilitzant desviació estàndard.

## Mòdul `export`

### `CSVExporter`

Exporta dades a format CSV.

#### Constructor

```python
CSVExporter(filename: str, delimiter: str = ',')
```

#### Mètodes

##### `export(telemetry_data: List[CarTelemetry], overwrite: bool = True) -> bool`

Exporta telemetria a CSV.

##### `export_processed(processed_data: ProcessedTelemetry) -> bool`

Exporta dades processades a CSV.

#### Exemple

```python
from src.export import CSVExporter

exporter = CSVExporter('telemetry.csv')
exporter.export(telemetry_data)
```

### `JSONExporter`

Exporta dades a format JSON.

#### Constructor

```python
JSONExporter(filename: str, indent: int = 2)
```

#### Mètodes

##### `export(telemetry_data, metadata: Dict = None) -> bool`

Exporta telemetria a JSON.

##### `export_processed(processed_data, metadata: Dict = None) -> bool`

Exporta dades processades a JSON.

##### `append(telemetry_data) -> bool`

Afegeix dades a fitxer existent.

## Mòdul `config`

### `Settings`

Configuració de l'aplicació.

#### Atributs

- `connection`: `ConnectionSettings`
- `telemetry`: `TelemetrySettings`
- `export`: `ExportSettings`
- `visualization`: `VisualizationSettings`
- `logging`: `LoggingSettings`

#### Funcions

##### `load_config(filename: str = "config.yaml") -> Settings`

Carrega configuració des de fitxer YAML.

##### `save_config(settings: Settings, filename: str = "config.yaml") -> bool`

Desa configuració a fitxer YAML.

##### `create_default_config(filename: str = "config.yaml") -> Settings`

Crea configuració per defecte.

#### Exemple

```python
from src.config import Settings, load_config, save_config

# Carregar configuració
settings = load_config('config.yaml')

# Modificar
settings.connection.host = "192.168.1.100"
settings.telemetry.interval = 50

# Desar
save_config(settings, 'config.yaml')
```

## Mòdul `utils`

### `setup_logger()`

Configura el sistema de logging.

```python
setup_logger(
    name: str = "lfs_ayats",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    log_format: Optional[str] = None
) -> logging.Logger
```

#### Exemple

```python
from src.utils import setup_logger

logger = setup_logger("my_app", "DEBUG", "app.log")
logger.info("Application started")
```

## Data Classes

### `CarTelemetry`

Dades telemètriques d'un vehicle.

**Atributs:**
- `timestamp`: Marca temporal
- `plid`: Player ID
- `node`: Node actual
- `lap`: Volta actual
- `position`: Dict amb x, y, z
- `speed`: Velocitat en m/s
- `direction`: Direcció
- `heading`: Orientació
- `angular_velocity`: Velocitat angular

### `ProcessedTelemetry`

Dades processades amb estadístiques.

**Atributs:**
- `avg_speed`: Velocitat mitjana
- `max_speed`: Velocitat màxima
- `min_speed`: Velocitat mínima
- `total_distance`: Distància total
- `sample_count`: Nombre de mostres

## Enumeracions

### `PacketType`

Tipus de paquets InSim.

```python
class PacketType(IntEnum):
    ISP_ISI = 1     # InSim Init
    ISP_VER = 2     # Version
    ISP_TINY = 3    # Tiny
    ISP_STA = 5     # State
    ISP_MCI = 38    # Multi Car Info
    # ... més tipus
```

## Referències

- [InSim Protocol](insim_protocol.md)
- [Development Guide](development.md)
- [Packet Reference](packet_reference.md)
