# Intermediate Tutorial: Advanced Telemetry Features

Master advanced features of LFS-Ayats including packet processing, real-time streaming, and performance optimization.

## Overview

This intermediate tutorial builds on the [Beginner Tutorial](tutorial-beginner.md) and explores advanced telemetry collection techniques, custom packet handling, data validation, and real-time data streaming.

## Learning Objectives

By the end of this tutorial, you will be able to:

- ✅ Process and parse advanced InSim packets
- ✅ Implement custom packet handlers
- ✅ Validate and filter telemetry data
- ✅ Optimize performance for high-frequency data
- ✅ Stream telemetry data in real-time
- ✅ Handle multiple simultaneous data sources
- ✅ Implement advanced error recovery
- ✅ Create custom data pipelines

## Prerequisites

- Completed [Beginner Tutorial](tutorial-beginner.md)
- Understanding of Python classes and decorators
- Familiarity with threading and async programming
- LFS-Ayats working installation
- 60-90 minutes of time

---

## Advanced Connection Management

### Persistent Connection with Auto-Reconnect

Build a robust connection manager that maintains connectivity:

```python
"""
Advanced connection manager with automatic reconnection.
"""

import time
import threading
from typing import Callable, Optional
from src.connection import InSimClient
from src.utils import setup_logger

logger = setup_logger("connection_manager", level="INFO")


class ConnectionManager:
    """
    Manages InSim connection with automatic reconnection.
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        app_name: str,
        admin_password: str = "",
        auto_reconnect: bool = True,
        reconnect_delay: float = 5.0
    ):
        """
        Initialize connection manager.
        
        Args:
            host: LFS server host
            port: InSim port
            app_name: Application name
            admin_password: Admin password for remote servers
            auto_reconnect: Enable automatic reconnection
            reconnect_delay: Delay between reconnection attempts
        """
        self.host = host
        self.port = port
        self.app_name = app_name
        self.admin_password = admin_password
        self.auto_reconnect = auto_reconnect
        self.reconnect_delay = reconnect_delay
        
        self.client: Optional[InSimClient] = None
        self.connected = False
        self.running = False
        
        # Callbacks
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        self.on_packet_callback: Optional[Callable] = None
    
    def connect(self) -> bool:
        """
        Establish connection to LFS.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            self.client = InSimClient(
                host=self.host,
                port=self.port,
                admin_password=self.admin_password,
                app_name=self.app_name
            )
            
            self.client.connect()
            self.client.initialize()
            
            self.connected = True
            logger.info(f"✓ Connected to {self.host}:{self.port}")
            
            if self.on_connect_callback:
                self.on_connect_callback()
            
            return True
        
        except Exception as e:
            logger.error(f"✗ Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from LFS."""
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
        
        self.connected = False
        
        if self.on_disconnect_callback:
            self.on_disconnect_callback()
        
        logger.info("✓ Disconnected")
    
    def start(self):
        """Start connection manager in background thread."""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Connection manager started")
    
    def stop(self):
        """Stop connection manager."""
        self.running = False
        self.disconnect()
        logger.info("Connection manager stopped")
    
    def _run_loop(self):
        """Main connection loop with auto-reconnect."""
        while self.running:
            if not self.connected:
                logger.info("Attempting to connect...")
                if self.connect():
                    self._packet_loop()
                else:
                    if self.auto_reconnect:
                        logger.info(f"Retrying in {self.reconnect_delay}s...")
                        time.sleep(self.reconnect_delay)
                    else:
                        break
            else:
                time.sleep(0.1)
    
    def _packet_loop(self):
        """Receive packets continuously."""
        while self.running and self.connected:
            try:
                packet = self.client.receive_packet(timeout=1.0)
                
                if packet and self.on_packet_callback:
                    self.on_packet_callback(packet)
            
            except TimeoutError:
                continue
            
            except ConnectionError as e:
                logger.warning(f"Connection lost: {e}")
                self.connected = False
                
                if self.on_disconnect_callback:
                    self.on_disconnect_callback()
                
                break
    
    def on_connect(self, callback: Callable):
        """Register callback for connection events."""
        self.on_connect_callback = callback
    
    def on_disconnect(self, callback: Callable):
        """Register callback for disconnection events."""
        self.on_disconnect_callback = callback
    
    def on_packet(self, callback: Callable):
        """Register callback for packet events."""
        self.on_packet_callback = callback


# Usage example
def main():
    """Example usage of ConnectionManager."""
    
    manager = ConnectionManager(
        host="127.0.0.1",
        port=29999,
        app_name="AdvancedApp",
        auto_reconnect=True,
        reconnect_delay=5.0
    )
    
    # Register callbacks
    manager.on_connect(lambda: logger.info("🔌 Connected!"))
    manager.on_disconnect(lambda: logger.info("🔌 Disconnected!"))
    manager.on_packet(lambda p: logger.info(f"📦 Packet: {p.get('type')}"))
    
    # Start manager
    manager.start()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()


if __name__ == "__main__":
    main()
```

---

## Advanced Packet Processing

### Custom Packet Handler

Create custom handlers for specific packet types:

```python
"""
Custom packet handler with validation and filtering.
"""

from typing import Dict, Any, Callable, Optional
from enum import IntEnum


class PacketType(IntEnum):
    """InSim packet type identifiers."""
    IS_ISI = 1   # InSim Init
    IS_VER = 2   # Version
    IS_TINY = 3  # Tiny packet
    IS_SMALL = 4 # Small packet
    IS_STA = 5   # State
    IS_MCI = 38  # Multi Car Info
    IS_NLP = 37  # Node and Lap
    IS_LAP = 57  # Lap time
    IS_SPX = 58  # Split time


class AdvancedPacketHandler:
    """
    Advanced packet handler with filtering and validation.
    """
    
    def __init__(self):
        """Initialize packet handler."""
        self.handlers: Dict[int, Callable] = {}
        self.filters: Dict[int, Callable] = {}
        self.validators: Dict[int, Callable] = {}
        
        # Statistics
        self.packet_counts: Dict[int, int] = {}
        self.invalid_count = 0
        self.filtered_count = 0
    
    def register_handler(
        self,
        packet_type: int,
        handler: Callable,
        filter_func: Optional[Callable] = None,
        validator: Optional[Callable] = None
    ):
        """
        Register packet handler with optional filter and validator.
        
        Args:
            packet_type: Packet type ID
            handler: Handler function
            filter_func: Optional filter function (returns True to process)
            validator: Optional validator function (returns True if valid)
        """
        self.handlers[packet_type] = handler
        
        if filter_func:
            self.filters[packet_type] = filter_func
        
        if validator:
            self.validators[packet_type] = validator
    
    def handle_packet(self, packet: Dict[str, Any]) -> bool:
        """
        Process packet through validation, filtering, and handling.
        
        Args:
            packet: Packet data dictionary
        
        Returns:
            True if packet was processed, False otherwise
        """
        packet_type = packet.get('type')
        
        if packet_type is None:
            return False
        
        # Update statistics
        self.packet_counts[packet_type] = \
            self.packet_counts.get(packet_type, 0) + 1
        
        # Validate packet
        if packet_type in self.validators:
            if not self.validators[packet_type](packet):
                self.invalid_count += 1
                return False
        
        # Filter packet
        if packet_type in self.filters:
            if not self.filters[packet_type](packet):
                self.filtered_count += 1
                return False
        
        # Handle packet
        if packet_type in self.handlers:
            try:
                self.handlers[packet_type](packet)
                return True
            except Exception as e:
                logger.error(f"Handler error for type {packet_type}: {e}")
                return False
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get packet processing statistics."""
        total = sum(self.packet_counts.values())
        
        return {
            'total_packets': total,
            'by_type': dict(self.packet_counts),
            'invalid': self.invalid_count,
            'filtered': self.filtered_count,
            'processed': total - self.invalid_count - self.filtered_count
        }


# Usage example
def main():
    """Example of advanced packet handling."""
    
    handler = AdvancedPacketHandler()
    
    # Handler for MCI packets (telemetry)
    def handle_mci(packet):
        """Process Multi Car Info packet."""
        cars = packet.get('cars', [])
        for car in cars:
            speed = car.get('speed', 0)
            logger.info(f"Car speed: {speed:.1f} km/h")
    
    # Validator: only process if packet has data
    def validate_mci(packet):
        """Validate MCI packet has car data."""
        return len(packet.get('cars', [])) > 0
    
    # Filter: only process speeds above 50 km/h
    def filter_mci(packet):
        """Filter slow speeds."""
        cars = packet.get('cars', [])
        return any(car.get('speed', 0) > 50 for car in cars)
    
    # Register handler with validation and filtering
    handler.register_handler(
        PacketType.IS_MCI,
        handle_mci,
        filter_func=filter_mci,
        validator=validate_mci
    )
    
    # Process packets
    # ... (connect and receive packets)
    
    # Get statistics
    stats = handler.get_statistics()
    logger.info(f"Statistics: {stats}")


if __name__ == "__main__":
    main()
```

---

## Data Validation and Filtering

### Telemetry Data Validator

Implement comprehensive data validation:

```python
"""
Advanced telemetry data validation.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class ValidationRule:
    """Validation rule definition."""
    field: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    required: bool = False
    type_check: Optional[type] = None


class TelemetryValidator:
    """
    Validates telemetry data against defined rules.
    """
    
    def __init__(self):
        """Initialize validator with default rules."""
        self.rules: List[ValidationRule] = [
            # Speed: 0-500 km/h
            ValidationRule('speed', min_value=0, max_value=500, required=True),
            
            # RPM: 0-20000
            ValidationRule('rpm', min_value=0, max_value=20000, required=True),
            
            # Gear: -1 to 7 (-1=reverse, 0=neutral)
            ValidationRule('gear', min_value=-1, max_value=7),
            
            # Throttle: 0-100%
            ValidationRule('throttle', min_value=0, max_value=100),
            
            # Brake: 0-100%
            ValidationRule('brake', min_value=0, max_value=100),
            
            # Steering: -1 to 1
            ValidationRule('steering', min_value=-1, max_value=1),
        ]
        
        self.error_count = 0
        self.errors: List[Dict[str, Any]] = []
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate telemetry data.
        
        Args:
            data: Telemetry data dictionary
        
        Returns:
            True if valid, False otherwise
        """
        is_valid = True
        
        for rule in self.rules:
            # Check if required field exists
            if rule.required and rule.field not in data:
                self._log_error(f"Missing required field: {rule.field}", data)
                is_valid = False
                continue
            
            # Skip if field not present and not required
            if rule.field not in data:
                continue
            
            value = data[rule.field]
            
            # Type checking
            if rule.type_check and not isinstance(value, rule.type_check):
                self._log_error(
                    f"Wrong type for {rule.field}: "
                    f"expected {rule.type_check}, got {type(value)}",
                    data
                )
                is_valid = False
                continue
            
            # Range checking
            if rule.min_value is not None and value < rule.min_value:
                self._log_error(
                    f"{rule.field} below minimum: {value} < {rule.min_value}",
                    data
                )
                is_valid = False
            
            if rule.max_value is not None and value > rule.max_value:
                self._log_error(
                    f"{rule.field} above maximum: {value} > {rule.max_value}",
                    data
                )
                is_valid = False
        
        return is_valid
    
    def _log_error(self, message: str, data: Dict[str, Any]):
        """Log validation error."""
        self.error_count += 1
        self.errors.append({
            'message': message,
            'data': data,
            'timestamp': time.time()
        })
        
        # Keep only last 100 errors
        if len(self.errors) > 100:
            self.errors.pop(0)
        
        logger.warning(f"Validation error: {message}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get validation error summary."""
        return {
            'total_errors': self.error_count,
            'recent_errors': self.errors[-10:]  # Last 10 errors
        }


# Usage
validator = TelemetryValidator()

# Validate telemetry data
telemetry = {
    'speed': 145.5,
    'rpm': 6500,
    'gear': 4,
    'throttle': 85,
    'brake': 0,
    'steering': 0.3
}

if validator.validate(telemetry):
    logger.info("✓ Data is valid")
    # Process data...
else:
    logger.warning("✗ Data validation failed")
    logger.warning(validator.get_error_summary())
```

---

## Performance Optimization

### High-Frequency Data Collection

Optimize for high-frequency telemetry (100+ Hz):

```python
"""
Optimized high-frequency data collection.
"""

import numpy as np
from collections import deque
from typing import Dict, Any


class OptimizedCollector:
    """
    High-performance telemetry collector.
    
    Uses numpy arrays and ring buffers for efficiency.
    """
    
    def __init__(self, buffer_size: int = 10000):
        """
        Initialize collector.
        
        Args:
            buffer_size: Maximum number of samples to keep
        """
        self.buffer_size = buffer_size
        
        # Use numpy arrays for efficient storage
        self.timestamps = deque(maxlen=buffer_size)
        self.speeds = deque(maxlen=buffer_size)
        self.rpms = deque(maxlen=buffer_size)
        self.gears = deque(maxlen=buffer_size)
        
        self.sample_count = 0
    
    def add_sample(self, data: Dict[str, Any]):
        """
        Add telemetry sample (optimized).
        
        Args:
            data: Telemetry data
        """
        timestamp = time.time()
        
        # Append to deques (O(1) operation)
        self.timestamps.append(timestamp)
        self.speeds.append(data.get('speed', 0))
        self.rpms.append(data.get('rpm', 0))
        self.gears.append(data.get('gear', 0))
        
        self.sample_count += 1
    
    def get_numpy_arrays(self) -> Dict[str, np.ndarray]:
        """
        Get data as numpy arrays for fast processing.
        
        Returns:
            Dictionary of numpy arrays
        """
        return {
            'timestamps': np.array(self.timestamps),
            'speeds': np.array(self.speeds),
            'rpms': np.array(self.rpms),
            'gears': np.array(self.gears)
        }
    
    def calculate_statistics(self) -> Dict[str, float]:
        """
        Calculate statistics efficiently using numpy.
        
        Returns:
            Statistics dictionary
        """
        arrays = self.get_numpy_arrays()
        
        return {
            'avg_speed': np.mean(arrays['speeds']),
            'max_speed': np.max(arrays['speeds']),
            'min_speed': np.min(arrays['speeds']),
            'std_speed': np.std(arrays['speeds']),
            'avg_rpm': np.mean(arrays['rpms']),
            'max_rpm': np.max(arrays['rpms']),
            'sample_count': len(arrays['speeds'])
        }
    
    def clear(self):
        """Clear all data."""
        self.timestamps.clear()
        self.speeds.clear()
        self.rpms.clear()
        self.gears.clear()


# Benchmark
import time

collector = OptimizedCollector(buffer_size=10000)

# Simulate high-frequency collection
start = time.time()
for i in range(10000):
    collector.add_sample({
        'speed': 100 + i % 50,
        'rpm': 5000 + i % 3000,
        'gear': (i % 6) + 1
    })

elapsed = time.time() - start
print(f"Added 10000 samples in {elapsed:.3f}s")
print(f"Rate: {10000/elapsed:.0f} samples/second")

# Calculate statistics
stats = collector.calculate_statistics()
print(f"Statistics: {stats}")
```

---

## Real-Time Data Streaming

### WebSocket Server

Stream telemetry via WebSocket:

```python
"""
WebSocket server for real-time telemetry streaming.
"""

import asyncio
import json
import websockets
from typing import Set
from src.telemetry import TelemetryCollector


class TelemetryStreamServer:
    """
    WebSocket server for streaming telemetry.
    """
    
    def __init__(self, collector: TelemetryCollector, port: int = 8765):
        """
        Initialize stream server.
        
        Args:
            collector: Telemetry collector instance
            port: WebSocket port
        """
        self.collector = collector
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
    
    async def handler(self, websocket, path):
        """
        Handle WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            path: Request path
        """
        # Register client
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            # Keep connection alive
            async for message in websocket:
                # Echo or handle client messages if needed
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Unregister client
            self.clients.remove(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast(self):
        """Broadcast telemetry to all connected clients."""
        while True:
            if self.clients:
                # Get latest telemetry
                data = self.collector.get_latest_telemetry()
                
                if data:
                    message = json.dumps(data)
                    
                    # Broadcast to all clients
                    websockets.broadcast(self.clients, message)
            
            # Stream at 10 Hz
            await asyncio.sleep(0.1)
    
    async def start(self):
        """Start WebSocket server."""
        async with websockets.serve(self.handler, "localhost", self.port):
            logger.info(f"WebSocket server running on ws://localhost:{self.port}")
            
            # Start broadcast task
            await self.broadcast()


# Usage
async def main():
    # Setup collector
    client = InSimClient(...)
    collector = TelemetryCollector(client)
    collector.start()
    
    # Start stream server
    server = TelemetryStreamServer(collector, port=8765)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Best Practices

### 1. Memory Management

```python
# Use generators for large datasets
def process_telemetry_batches(collector, batch_size=1000):
    """Process telemetry in batches to save memory."""
    history = collector.get_telemetry_history()
    
    for i in range(0, len(history), batch_size):
        batch = history[i:i+batch_size]
        yield batch
        # Process batch...
```

### 2. Asynchronous Processing

```python
# Use async for non-blocking operations
import asyncio

async def process_telemetry_async(data):
    """Process telemetry asynchronously."""
    # Heavy processing in separate thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, heavy_processing, data)
    return result
```

### 3. Error Recovery

```python
# Implement circuit breaker pattern
class CircuitBreaker:
    """Prevent cascading failures."""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            self.state = "CLOSED"
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e
```

---

## Next Steps

Continue your learning journey:

1. **Advanced Analysis:** [tutorials/04-advanced-analysis.md](tutorials/04-advanced-analysis.md)
2. **Database Integration:** [tutorials/05-database-integration.md](tutorials/05-database-integration.md)
3. **API Development:** [api-examples.md](api-examples.md)
4. **System Architecture:** [architecture.md](architecture.md)

## Additional Resources

- **Performance Profiling:** Use `cProfile` and `line_profiler`
- **Memory Profiling:** Use `memory_profiler`
- **InSim Documentation:** [insim_protocol.md](insim_protocol.md)
- **Example Scripts:** [../examples/](../examples/)

---

**You're now ready for advanced telemetry applications!** 🚀💨
