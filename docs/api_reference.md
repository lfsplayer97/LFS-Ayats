# API Reference

Complete API reference for LFS-Ayats.

## `connection` Module

### `InSimClient`

Client to connect to the LFS server using InSim.

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

**Parameters:**
- `host`: LFS server IP
- `port`: InSim port (default 29999)
- `admin_password`: Admin password if needed
- `app_name`: Application name (max 16 characters)
- `udp`: Use UDP instead of TCP

#### Methods

##### `connect() -> bool`

Establish connection with the server.

**Returns:** `True` if successful, `False` otherwise

**Raises:** `ConnectionError` if connection fails

##### `initialize(flags: int = 0, interval: int = 0) -> None`

Initialize the InSim connection.

**Parameters:**
- `flags`: InSim flags (ISF_MCI, ISF_NLP, etc.)
- `interval`: MCI/NLP interval in hundredths of a second

##### `send_packet(packet: bytes) -> None`

Send a packet to the server.

**Parameters:**
- `packet`: Packet in bytes format

##### `receive_packet(timeout: Optional[float] = None) -> Optional[bytes]`

Receive a packet from the server.

**Parameters:**
- `timeout`: Maximum wait time (None = blocking)

**Returns:** Received packet or None

##### `disconnect() -> None`

Close the connection with the server.

##### `register_callback(packet_type: int, callback: Callable) -> None`

Register a callback for a packet type.

**Parameters:**
- `packet_type`: Packet type (PacketType)
- `callback`: Function to call

#### Example

```python
from src.connection import InSimClient

with InSimClient(host="127.0.0.1", port=29999) as client:
    client.initialize(flags=48, interval=100)
    
    while True:
        packet = client.receive_packet(timeout=1.0)
        if packet:
            # Process packet
            pass
```

### `PacketHandler`

Handles InSim packet processing.

#### Methods

##### `parse_packet(data: bytes) -> Optional[PacketInfo]`

Parse a packet and extract basic information.

**Returns:** `PacketInfo` or None if invalid

##### `process_packet(data: bytes) -> bool`

Process a packet and call the corresponding handler.

**Returns:** `True` if processed correctly

##### `register_handler(packet_type: int, handler: Callable) -> None`

Register a handler for a packet type.

##### `parse_version_packet(data: bytes) -> Optional[Dict[str, Any]]`

Parse an IS_VER packet.

##### `parse_state_packet(data: bytes) -> Optional[Dict[str, Any]]`

Parse an IS_STA packet.

##### `parse_mci_packet(data: bytes) -> Optional[Dict[str, Any]]`

Parse an IS_MCI packet (telemetry).

## `telemetry` Module

### `TelemetryCollector`

Collects telemetry data from the LFS server.

#### Constructor

```python
TelemetryCollector(client: InSimClient)
```

**Parameters:**
- `client`: Connected InSim client

#### Methods

##### `start(interval: int = 100) -> None`

Start telemetry collection.

**Parameters:**
- `interval`: Interval in ms (default 100ms = 10Hz)

##### `stop() -> None`

Stop telemetry collection.

##### `get_latest_telemetry(plid: Optional[int] = None) -> Dict[int, CarTelemetry]`

Get latest telemetry.

**Parameters:**
- `plid`: Specific Player ID (None = all)

**Returns:** Dict with telemetry per player ID

##### `get_telemetry_history(plid: int, limit: Optional[int] = None) -> List[CarTelemetry]`

Get telemetry history.

**Parameters:**
- `plid`: Player ID
- `limit`: Maximum number of samples (None = all)

##### `clear_history(plid: Optional[int] = None) -> None`

Clear telemetry history.

##### `register_callback(event_type: str, callback: Callable) -> None`

Register a callback for events.

**Event types:**
- `'car_update'`: Vehicle update
- `'lap_complete'`: Lap completed
- `'split_time'`: Sector time
- `'player_join'`: Player joins
- `'player_leave'`: Player leaves

#### Example

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

# ... later ...
collector.stop()
```

### `TelemetryProcessor`

Processes and validates telemetry data.

#### Constructor

```python
TelemetryProcessor(max_speed: float = 150.0)
```

#### Methods

##### `validate_telemetry(telemetry: CarTelemetry) -> bool`

Validate telemetry data.

**Returns:** `True` if valid

##### `process_telemetry(telemetry_list: List[CarTelemetry]) -> ProcessedTelemetry`

Process telemetry and calculate statistics.

##### `calculate_statistics(telemetry_list: List[CarTelemetry]) -> Dict[str, Any]`

Calculate detailed statistics.

##### `filter_by_speed_range(telemetry_list, min_speed, max_speed) -> List`

Filter by speed range.

##### `detect_anomalies(telemetry_list, threshold_stdev: float = 3.0) -> List[int]`

Detect anomalies using standard deviation.

## `export` Module

### `CSVExporter`

Export data to CSV format.

#### Constructor

```python
CSVExporter(filename: str, delimiter: str = ',')
```

#### Methods

##### `export(telemetry_data: List[CarTelemetry], overwrite: bool = True) -> bool`

Export telemetry to CSV.

##### `export_processed(processed_data: ProcessedTelemetry) -> bool`

Export processed data to CSV.

#### Example

```python
from src.export import CSVExporter

exporter = CSVExporter('telemetry.csv')
exporter.export(telemetry_data)
```

### `JSONExporter`

Export data to JSON format.

#### Constructor

```python
JSONExporter(filename: str, indent: int = 2)
```

#### Methods

##### `export(telemetry_data, metadata: Dict = None) -> bool`

Export telemetry to JSON.

##### `export_processed(processed_data, metadata: Dict = None) -> bool`

Export processed data to JSON.

##### `append(telemetry_data) -> bool`

Append data to existing file.

## `config` Module

### `Settings`

Application configuration.

#### Attributes

- `connection`: `ConnectionSettings`
- `telemetry`: `TelemetrySettings`
- `export`: `ExportSettings`
- `visualization`: `VisualizationSettings`
- `logging`: `LoggingSettings`

#### Functions

##### `load_config(filename: str = "config.yaml") -> Settings`

Load configuration from YAML file.

##### `save_config(settings: Settings, filename: str = "config.yaml") -> bool`

Save configuration to YAML file.

##### `create_default_config(filename: str = "config.yaml") -> Settings`

Create default configuration.

#### Example

```python
from src.config import Settings, load_config, save_config

# Load configuration
settings = load_config('config.yaml')

# Modify
settings.connection.host = "192.168.1.100"
settings.telemetry.interval = 50

# Save
save_config(settings, 'config.yaml')
```

## `utils` Module

### `setup_logger()`

Configure the logging system.

```python
setup_logger(
    name: str = "lfs_ayats",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    log_format: Optional[str] = None
) -> logging.Logger
```

#### Example

```python
from src.utils import setup_logger

logger = setup_logger("my_app", "DEBUG", "app.log")
logger.info("Application started")
```

## Data Classes

### `CarTelemetry`

Vehicle telemetry data.

**Attributes:**
- `timestamp`: Timestamp
- `plid`: Player ID
- `node`: Current node
- `lap`: Current lap
- `position`: Dict with x, y, z
- `speed`: Speed in m/s
- `direction`: Direction
- `heading`: Heading
- `angular_velocity`: Angular velocity

### `ProcessedTelemetry`

Processed data with statistics.

**Attributes:**
- `avg_speed`: Average speed
- `max_speed`: Maximum speed
- `min_speed`: Minimum speed
- `total_distance`: Total distance
- `sample_count`: Number of samples

## Enumerations

### `PacketType`

InSim packet types.

```python
class PacketType(IntEnum):
    ISP_ISI = 1     # InSim Init
    ISP_VER = 2     # Version
    ISP_TINY = 3    # Tiny
    ISP_STA = 5     # State
    ISP_MCI = 38    # Multi Car Info
    # ... more types
```

## References

- [InSim Protocol](insim_protocol.md)
- [Development Guide](development.md)
- [Packet Reference](packet_reference.md)
