# API Usage Examples

Practical examples for using the LFS-Ayats REST API and WebSocket streaming.

## Overview

This guide provides ready-to-use examples for integrating LFS-Ayats into your applications using the REST API and WebSocket connections.

## Prerequisites

- LFS-Ayats API server running (default: `http://localhost:8000`)
- API dependencies installed:
  ```bash
  pip install requests websockets aiohttp
  ```
- Basic understanding of HTTP and REST APIs

## Quick Start

### Starting the API Server

```bash
# Start the FastAPI server
uvicorn src.api.main:app --reload --port 8000

# Or using the provided script
python -m src.api.main
```

**Verify server is running:**
```bash
curl http://localhost:8000/api/health
# Should return: {"status": "ok"}
```

**View API documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## REST API Examples

### Example 1: Health Check

Basic connectivity test:

```python
import requests

# Check API health
response = requests.get("http://localhost:8000/api/health")
print(response.json())
# Output: {"status": "ok", "version": "0.1.0"}
```

### Example 2: Get System Status

Get current telemetry system status:

```python
import requests

# Get system status
response = requests.get("http://localhost:8000/api/v1/status")
status = response.json()

print(f"Connected: {status['connected']}")
print(f"Sessions: {status['active_sessions']}")
print(f"Data points: {status['total_datapoints']}")

# Example output:
# Connected: True
# Sessions: 3
# Data points: 15234
```

### Example 3: List Sessions

Retrieve telemetry sessions with filtering:

```python
import requests

def list_sessions(circuit=None, driver=None, limit=50):
    """
    List telemetry sessions with optional filters.
    
    Args:
        circuit: Filter by circuit (e.g., "BL1", "SO3")
        driver: Filter by driver name
        limit: Maximum results to return
    """
    params = {"limit": limit}
    
    if circuit:
        params["circuit"] = circuit
    if driver:
        params["driver"] = driver
    
    response = requests.get(
        "http://localhost:8000/api/v1/sessions",
        params=params
    )
    response.raise_for_status()
    return response.json()

# List all sessions
sessions = list_sessions()
print(f"Total sessions: {len(sessions['items'])}")

# Filter by circuit
bl1_sessions = list_sessions(circuit="BL1")
print(f"Blackwood sessions: {len(bl1_sessions['items'])}")

# Filter by driver
my_sessions = list_sessions(driver="MyName")
print(f"My sessions: {len(my_sessions['items'])}")
```

### Example 4: Get Session Details

Retrieve detailed information about a specific session:

```python
import requests

def get_session(session_id):
    """Get detailed session information."""
    response = requests.get(
        f"http://localhost:8000/api/v1/sessions/{session_id}"
    )
    response.raise_for_status()
    return response.json()

# Get session details
session = get_session(session_id=1)

print(f"Session #{session['id']}")
print(f"Circuit: {session['circuit']}")
print(f"Date: {session['created_at']}")
print(f"Laps: {len(session['laps'])}")
print(f"Best lap: {session['best_lap_time']}")
```

### Example 5: Get Lap Telemetry

Retrieve telemetry data for a specific lap:

```python
import requests
import pandas as pd

def get_lap_telemetry(lap_id):
    """
    Get telemetry data for a lap.
    
    Returns pandas DataFrame with telemetry points.
    """
    response = requests.get(
        f"http://localhost:8000/api/v1/laps/{lap_id}/telemetry"
    )
    response.raise_for_status()
    
    data = response.json()
    return pd.DataFrame(data['telemetry'])

# Get telemetry for lap
df = get_lap_telemetry(lap_id=42)

print(f"Data points: {len(df)}")
print(f"Max speed: {df['speed'].max():.1f} km/h")
print(f"Max RPM: {df['rpm'].max()}")
print(f"Average speed: {df['speed'].mean():.1f} km/h")

# Plot speed over time
import matplotlib.pyplot as plt
plt.plot(df['timestamp'], df['speed'])
plt.xlabel('Time (s)')
plt.ylabel('Speed (km/h)')
plt.title(f'Speed Profile - Lap {lap_id}')
plt.show()
```

### Example 6: Compare Laps

Compare telemetry between two laps:

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

def compare_laps(lap_id1, lap_id2):
    """Compare telemetry between two laps."""
    # Get telemetry for both laps
    response1 = requests.get(
        f"http://localhost:8000/api/v1/laps/{lap_id1}/telemetry"
    )
    response2 = requests.get(
        f"http://localhost:8000/api/v1/laps/{lap_id2}/telemetry"
    )
    
    df1 = pd.DataFrame(response1.json()['telemetry'])
    df2 = pd.DataFrame(response2.json()['telemetry'])
    
    # Plot comparison
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Speed comparison
    ax1.plot(df1['distance'], df1['speed'], label=f'Lap {lap_id1}')
    ax1.plot(df2['distance'], df2['speed'], label=f'Lap {lap_id2}')
    ax1.set_ylabel('Speed (km/h)')
    ax1.legend()
    ax1.grid(True)
    
    # Throttle comparison
    ax2.plot(df1['distance'], df1['throttle'], label=f'Lap {lap_id1}')
    ax2.plot(df2['distance'], df2['throttle'], label=f'Lap {lap_id2}')
    ax2.set_xlabel('Distance (m)')
    ax2.set_ylabel('Throttle (%)')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

# Compare two laps
compare_laps(lap_id1=42, lap_id2=43)
```

### Example 7: Get Best Laps

Find fastest laps across all sessions:

```python
import requests

def get_best_laps(circuit=None, vehicle=None, limit=10):
    """
    Get best lap times.
    
    Args:
        circuit: Filter by circuit
        vehicle: Filter by vehicle
        limit: Number of results
    """
    params = {"limit": limit}
    
    if circuit:
        params["circuit"] = circuit
    if vehicle:
        params["vehicle"] = vehicle
    
    response = requests.get(
        "http://localhost:8000/api/v1/laps/best",
        params=params
    )
    response.raise_for_status()
    return response.json()

# Get top 10 laps on Blackwood
best_laps = get_best_laps(circuit="BL1", limit=10)

print("Best Laps on BL1:")
print("-" * 50)
for i, lap in enumerate(best_laps['items'], 1):
    print(f"{i}. {lap['lap_time']}s - {lap['driver']} ({lap['vehicle']})")

# Example output:
# Best Laps on BL1:
# --------------------------------------------------
# 1. 84.52s - FastDriver (XFG)
# 2. 84.89s - ProRacer (XFG)
# 3. 85.12s - SpeedKing (XFG)
```

### Example 8: Get Statistics

Retrieve aggregated statistics:

```python
import requests

def get_driver_statistics(driver_name):
    """Get statistics for a driver."""
    response = requests.get(
        f"http://localhost:8000/api/v1/statistics/driver/{driver_name}"
    )
    response.raise_for_status()
    return response.json()

# Get driver stats
stats = get_driver_statistics("MyName")

print(f"Driver: {stats['driver']}")
print(f"Total sessions: {stats['total_sessions']}")
print(f"Total laps: {stats['total_laps']}")
print(f"Best lap: {stats['best_lap_time']}s")
print(f"Average lap: {stats['average_lap_time']}s")
print(f"Total distance: {stats['total_distance']}km")
print(f"Total time: {stats['total_time']}h")
```

### Example 9: Pagination

Handle large result sets with pagination:

```python
import requests

def get_all_sessions(page_size=50):
    """
    Get all sessions using pagination.
    
    Yields sessions in batches.
    """
    offset = 0
    
    while True:
        response = requests.get(
            "http://localhost:8000/api/v1/sessions",
            params={"limit": page_size, "offset": offset}
        )
        response.raise_for_status()
        
        data = response.json()
        sessions = data['items']
        
        if not sessions:
            break
        
        yield from sessions
        
        # Check if we've reached the end
        if len(sessions) < page_size:
            break
        
        offset += page_size

# Process all sessions
total = 0
for session in get_all_sessions():
    total += 1
    print(f"Processing session {session['id']}...")

print(f"Total sessions processed: {total}")
```

### Example 10: Error Handling

Robust error handling for production use:

```python
import requests
from requests.exceptions import RequestException, HTTPError, Timeout

def safe_api_call(url, max_retries=3, timeout=10):
    """
    Make API call with error handling and retries.
    
    Args:
        url: API endpoint URL
        max_retries: Maximum retry attempts
        timeout: Request timeout in seconds
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        
        except Timeout:
            print(f"Attempt {attempt + 1}: Request timeout")
            if attempt == max_retries - 1:
                raise
        
        except HTTPError as e:
            if e.response.status_code == 404:
                print("Resource not found")
                return None
            elif e.response.status_code == 500:
                print(f"Attempt {attempt + 1}: Server error")
                if attempt == max_retries - 1:
                    raise
            else:
                raise
        
        except RequestException as e:
            print(f"Attempt {attempt + 1}: Connection error: {e}")
            if attempt == max_retries - 1:
                raise
        
        # Wait before retry
        if attempt < max_retries - 1:
            import time
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None

# Use safe API call
data = safe_api_call("http://localhost:8000/api/v1/sessions/123")
if data:
    print("Success:", data)
else:
    print("Failed to retrieve data")
```

---

## WebSocket Examples

### Example 11: Real-Time Telemetry Stream

Stream live telemetry data using WebSocket:

```python
import asyncio
import websockets
import json

async def stream_telemetry():
    """
    Connect to WebSocket and stream telemetry data.
    """
    uri = "ws://localhost:8000/api/v1/telemetry/live"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to telemetry stream")
            
            while True:
                # Receive data
                message = await websocket.recv()
                data = json.loads(message)
                
                # Process telemetry
                speed = data.get('speed', 0)
                rpm = data.get('rpm', 0)
                gear = data.get('gear', 0)
                
                print(f"Speed: {speed:.1f} km/h | RPM: {rpm} | Gear: {gear}")
    
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"Error: {e}")

# Run the stream
asyncio.run(stream_telemetry())
```

### Example 12: WebSocket with Auto-Reconnect

Robust WebSocket client with automatic reconnection:

```python
import asyncio
import websockets
import json
from typing import Callable

class TelemetryStreamClient:
    """WebSocket client with auto-reconnect."""
    
    def __init__(self, uri: str, on_data: Callable):
        """
        Initialize WebSocket client.
        
        Args:
            uri: WebSocket URI
            on_data: Callback function for received data
        """
        self.uri = uri
        self.on_data = on_data
        self.running = False
    
    async def connect(self):
        """Connect and maintain connection with auto-reconnect."""
        self.running = True
        reconnect_delay = 1
        
        while self.running:
            try:
                async with websockets.connect(self.uri) as websocket:
                    print("✓ Connected to telemetry stream")
                    reconnect_delay = 1  # Reset delay on successful connect
                    
                    while self.running:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=30.0
                            )
                            data = json.loads(message)
                            await self.on_data(data)
                        
                        except asyncio.TimeoutError:
                            # Send ping to keep connection alive
                            await websocket.ping()
                        
                        except websockets.exceptions.ConnectionClosed:
                            print("✗ Connection closed")
                            break
            
            except Exception as e:
                print(f"✗ Connection error: {e}")
            
            if self.running:
                print(f"Reconnecting in {reconnect_delay}s...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 30)  # Exponential backoff
    
    def stop(self):
        """Stop the client."""
        self.running = False

# Usage
async def handle_telemetry(data):
    """Process received telemetry data."""
    print(f"Speed: {data.get('speed', 0):.1f} km/h")

async def main():
    client = TelemetryStreamClient(
        uri="ws://localhost:8000/api/v1/telemetry/live",
        on_data=handle_telemetry
    )
    
    try:
        await client.connect()
    except KeyboardInterrupt:
        print("Stopping...")
        client.stop()

asyncio.run(main())
```

### Example 13: Multiple WebSocket Streams

Handle multiple concurrent streams:

```python
import asyncio
import websockets
import json

async def telemetry_stream():
    """Stream telemetry data."""
    uri = "ws://localhost:8000/api/v1/telemetry/live"
    async with websockets.connect(uri) as ws:
        while True:
            data = json.loads(await ws.recv())
            print(f"[Telemetry] Speed: {data.get('speed', 0):.1f}")

async def events_stream():
    """Stream event data."""
    uri = "ws://localhost:8000/api/v1/events/live"
    async with websockets.connect(uri) as ws:
        while True:
            data = json.loads(await ws.recv())
            print(f"[Event] {data.get('type')}: {data.get('message')}")

async def main():
    """Run multiple streams concurrently."""
    await asyncio.gather(
        telemetry_stream(),
        events_stream()
    )

asyncio.run(main())
```

---

## Complete Application Examples

### Example 14: Simple Telemetry Logger

Complete application that logs telemetry to file:

```python
import requests
import json
import time
from datetime import datetime

class TelemetryLogger:
    """Log telemetry data to JSON file."""
    
    def __init__(self, output_file="telemetry.json"):
        self.output_file = output_file
        self.data = []
    
    def collect(self, duration_seconds=60):
        """
        Collect telemetry for specified duration.
        
        Args:
            duration_seconds: Collection duration
        """
        print(f"Collecting telemetry for {duration_seconds} seconds...")
        
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            try:
                # Get latest telemetry
                response = requests.get(
                    "http://localhost:8000/api/v1/telemetry/latest",
                    timeout=2
                )
                
                if response.status_code == 200:
                    telemetry = response.json()
                    telemetry['timestamp'] = datetime.now().isoformat()
                    self.data.append(telemetry)
                    
                    speed = telemetry.get('speed', 0)
                    print(f"\rSpeed: {speed:.1f} km/h | Points: {len(self.data)}", end="")
            
            except requests.exceptions.RequestException:
                print("\rAPI not responding...", end="")
            
            time.sleep(0.1)  # 10 Hz sampling
        
        print()  # New line
    
    def save(self):
        """Save collected data to file."""
        with open(self.output_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        print(f"✓ Saved {len(self.data)} data points to {self.output_file}")

# Usage
if __name__ == "__main__":
    logger = TelemetryLogger("my_session.json")
    
    try:
        logger.collect(duration_seconds=60)
        logger.save()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        logger.save()
```

### Example 15: API Client Class

Reusable API client class:

```python
import requests
from typing import List, Dict, Any, Optional

class LFSAyatsAPI:
    """Client for LFS-Ayats REST API."""
    
    def __init__(self, base_url="http://localhost:8000"):
        """Initialize API client."""
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = requests.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()
    
    def get_sessions(
        self,
        circuit: Optional[str] = None,
        driver: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get list of sessions."""
        params = {"limit": limit, "offset": offset}
        if circuit:
            params["circuit"] = circuit
        if driver:
            params["driver"] = driver
        
        response = requests.get(f"{self.api_url}/sessions", params=params)
        response.raise_for_status()
        return response.json()['items']
    
    def get_session(self, session_id: int) -> Dict[str, Any]:
        """Get session details."""
        response = requests.get(f"{self.api_url}/sessions/{session_id}")
        response.raise_for_status()
        return response.json()
    
    def get_lap_telemetry(self, lap_id: int) -> List[Dict[str, Any]]:
        """Get telemetry for a lap."""
        response = requests.get(f"{self.api_url}/laps/{lap_id}/telemetry")
        response.raise_for_status()
        return response.json()['telemetry']
    
    def get_best_laps(
        self,
        circuit: Optional[str] = None,
        vehicle: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get best lap times."""
        params = {"limit": limit}
        if circuit:
            params["circuit"] = circuit
        if vehicle:
            params["vehicle"] = vehicle
        
        response = requests.get(f"{self.api_url}/laps/best", params=params)
        response.raise_for_status()
        return response.json()['items']

# Usage
api = LFSAyatsAPI()

# Check health
print(api.health_check())

# Get sessions
sessions = api.get_sessions(circuit="BL1", limit=10)
print(f"Found {len(sessions)} sessions")

# Get best laps
best_laps = api.get_best_laps(circuit="BL1", limit=5)
for lap in best_laps:
    print(f"{lap['lap_time']}s - {lap['driver']}")
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

```python
# Default limits
# GET requests: 60/minute
# POST requests: 30/minute
# WebSocket: No limit

# Check rate limit headers
response = requests.get("http://localhost:8000/api/v1/sessions")
print(f"Rate limit: {response.headers.get('X-RateLimit-Limit')}")
print(f"Remaining: {response.headers.get('X-RateLimit-Remaining')}")
print(f"Reset: {response.headers.get('X-RateLimit-Reset')}")

# Handle rate limiting
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    print(f"Rate limited. Retry after {retry_after} seconds")
    time.sleep(retry_after)
```

---

## Common Issues

### Connection Refused
- Ensure API server is running: `uvicorn src.api.main:app --reload`
- Check port: default is 8000

### 404 Not Found
- Verify endpoint URL is correct
- Check API documentation at `/api/docs`

### Empty Response
- Make sure telemetry data is being collected
- Check if LFS is running and connected

### WebSocket Disconnects
- Implement reconnection logic (see Example 12)
- Check firewall settings

See [Troubleshooting Guide](troubleshooting.md) for more solutions.

---

## Next Steps

- **API Documentation:** [api_reference.md](api_reference.md)
- **REST API Guide:** [api_documentation.md](api_documentation.md)
- **Quick Start:** [api_quickstart.md](api_quickstart.md)
- **Example Scripts:** [../examples/](../examples/)

---

**Ready to integrate LFS-Ayats into your application!** 🚀
