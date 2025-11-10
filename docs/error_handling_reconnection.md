# Enhanced Error Handling and Reconnection System

This document describes the new error handling and automatic reconnection features implemented in LFS-Ayats.

## Features

### 1. Automatic Reconnection with Exponential Backoff

The InSim client now supports automatic reconnection when the connection is lost:

```python
from src.connection import InSimClient

client = InSimClient(
    host="127.0.0.1",
    port=29999,
    max_retries=5,          # Maximum number of reconnection attempts
    retry_delay=2.0,        # Initial delay between retries (exponential backoff)
    reconnect_enabled=True  # Enable automatic reconnection
)

# Connect with automatic retries
if client.connect_with_retry():
    print("Connected successfully!")
```

**Exponential Backoff**: The retry delay doubles with each attempt:
- Attempt 1: 2.0 seconds
- Attempt 2: 4.0 seconds
- Attempt 3: 8.0 seconds
- Attempt 4: 16.0 seconds
- ...

### 2. Connection State Management

Track connection state changes with callbacks:

```python
from src.connection import ConnectionState

def on_connected(old_state, new_state):
    print(f"Connected! {old_state.value} -> {new_state.value}")

def on_reconnecting(old_state, new_state):
    print(f"Reconnecting... {old_state.value} -> {new_state.value}")

# Register callbacks
client.on_state_change(ConnectionState.CONNECTED, on_connected)
client.on_state_change(ConnectionState.RECONNECTING, on_reconnecting)
```

**Available States**:
- `DISCONNECTED`: No connection
- `CONNECTING`: Initial connection attempt
- `CONNECTED`: Successfully connected
- `RECONNECTING`: Attempting to reconnect
- `ERROR`: Connection error occurred

### 3. Heartbeat Mechanism

Keep the connection alive and detect dead connections:

```python
# Start heartbeat (sends TINY_NONE packets periodically)
client.start_heartbeat(interval=30.0)  # Every 30 seconds

# Stop heartbeat
client.stop_heartbeat()
```

The heartbeat automatically triggers reconnection if sending fails.

### 4. Packet Validation

All received packets are validated before processing:

```python
# Validation is automatic in receive_packet()
packet = client.receive_packet(timeout=1.0)
if packet:
    # Packet is guaranteed to be valid
    print(f"Valid packet received: {len(packet)} bytes")
```

**Validation checks**:
- Minimum size (4 bytes)
- Size consistency (declared vs. actual)
- Packet type validity

### 5. Circuit Breaker Pattern

Prevent cascading failures with the circuit breaker:

```python
from src.connection import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,  # Open circuit after 5 failures
    timeout=60.0          # Try again after 60 seconds
)

# Use circuit breaker with any function
try:
    result = breaker.call(risky_function, arg1, arg2)
except CircuitBreakerOpenError:
    print("Circuit is open, service is unavailable")
```

**Circuit States**:
- `CLOSED`: Normal operation, requests pass through
- `OPEN`: Too many failures, requests blocked
- `HALF_OPEN`: Testing if service recovered

### 6. Telemetry Buffer

Preserve telemetry data during connection interruptions:

```python
from src.telemetry import TelemetryBuffer

# Create buffer
buffer = TelemetryBuffer(max_size=1000)

# Add data
buffer.add(telemetry_data)

# Check buffer status
stats = buffer.get_stats()
print(f"Buffer: {stats['size']}/{stats['max_size']} items")

# Flush to exporter when reconnected
buffer.flush_to_exporter(exporter)

# Or use callback
buffer.flush_to_callback(lambda data: process(data))
```

**Thread-safe**: All buffer operations use locking for thread safety.

### 7. Enhanced Logging with Colors

Colored console output using colorlog:

```python
from src.utils.logger import setup_logger

logger = setup_logger(
    name="lfs_ayats",
    level="INFO",
    log_file="app.log",
    console=True,
    use_colors=True  # Enable colored output
)

logger.debug("Debug message")      # Cyan
logger.info("Info message")        # Green
logger.warning("Warning message")  # Yellow
logger.error("Error message")      # Red
logger.critical("Critical message") # Red on white
```

## Usage Example

See `examples/enhanced_connection.py` for a complete working example.

## Configuration

All reconnection features can be configured when creating the InSim client:

```python
client = InSimClient(
    host="127.0.0.1",             # LFS server address
    port=29999,                   # InSim port
    admin_password="",            # Admin password (optional)
    app_name="LFS-Ayats",         # Application name (max 16 chars)
    udp=False,                    # Use TCP by default
    max_retries=5,                # Reconnection attempts
    retry_delay=2.0,              # Initial retry delay (seconds)
    reconnect_enabled=True,       # Enable auto-reconnection
    heartbeat_interval=30.0       # Heartbeat interval (seconds)
)
```

## Testing

All new features are comprehensively tested:

- **Circuit Breaker**: 13 tests, 99% coverage
- **Telemetry Buffer**: 17 tests, 95% coverage  
- **Enhanced InSim Client**: 18 tests, 78% coverage
- **Total**: 231 tests passing, 76% overall coverage

Run tests:
```bash
pytest tests/unit/connection/test_circuit_breaker.py
pytest tests/unit/telemetry/test_buffer.py
pytest tests/unit/connection/test_insim_client.py
```

## Architecture

### Class Diagram

```
┌─────────────────┐
│  InSimClient    │
├─────────────────┤
│ - state         │
│ - retry_count   │
│ - callbacks     │
├─────────────────┤
│ + connect()     │
│ + connect_with_retry() │
│ + validate_packet()    │
│ + start_heartbeat()    │
│ + send_tiny()          │
└─────────────────┘
         │
         │ uses
         ▼
┌─────────────────┐      ┌──────────────────┐
│ CircuitBreaker  │      │ TelemetryBuffer  │
├─────────────────┤      ├──────────────────┤
│ - state         │      │ - buffer         │
│ - failure_count │      │ - lock           │
├─────────────────┤      ├──────────────────┤
│ + call()        │      │ + add()          │
│ + reset()       │      │ + flush_to_*()   │
└─────────────────┘      └──────────────────┘
```

### Connection Flow

```
┌─────────┐
│  Start  │
└────┬────┘
     │
     ▼
┌─────────────────────┐
│ connect_with_retry()│
└─────────┬───────────┘
          │
          ├─ Success ──────┐
          │                │
          ├─ Fail ─────────┤
          │   (retry)      │
          │                │
          └─ Max retries ──┤
                           │
                           ▼
              ┌────────────────────────┐
              │   initialize()         │
              │   start_heartbeat()    │
              └────────┬───────────────┘
                       │
                       ▼
              ┌────────────────────────┐
              │  receive_packet()      │
              │  validate_packet()     │
              └────────┬───────────────┘
                       │
                       ├─ Valid ───────► Process
                       │
                       ├─ Invalid ─────► Discard
                       │
                       └─ Error ───────► trigger_reconnect()
```

## Best Practices

1. **Always use `connect_with_retry()`** instead of `connect()` for production code
2. **Register state callbacks** to monitor connection health
3. **Start heartbeat** after successful connection
4. **Use telemetry buffer** to prevent data loss during reconnections
5. **Configure appropriate retry parameters** based on your network conditions
6. **Enable colored logging** for better visibility during development

## Troubleshooting

### Connection keeps failing
- Check LFS is running and InSim is enabled: `/insim 29999`
- Verify firewall settings allow port 29999
- Check logs for specific error messages
- Increase `max_retries` and `retry_delay` for unstable networks

### Heartbeat not working
- Ensure `start_heartbeat()` is called after successful connection
- Check `heartbeat_interval` is reasonable (30-60 seconds recommended)
- Look for heartbeat errors in logs

### Buffer filling up
- Increase `max_size` if needed
- Flush buffer more frequently
- Check if data processing is keeping up with incoming rate

## References

- [InSim Protocol Documentation](https://en.lfsmanual.net/wiki/InSim.txt)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
- [colorlog Documentation](https://github.com/borntyping/python-colorlog)
