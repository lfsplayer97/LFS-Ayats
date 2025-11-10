# REST API Quick Start Guide

## Starting the API Server

### Development Mode (with auto-reload)
```bash
cd /home/runner/work/LFS-Ayats/LFS-Ayats
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Accessing Documentation

Once the server is running:
- **Interactive API Docs (Swagger UI)**: http://localhost:8000/api/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/api/redoc
- **OpenAPI JSON Schema**: http://localhost:8000/api/openapi.json

## Quick Test

```bash
# Health check
curl http://localhost:8000/api/v1/health

# System status
curl http://localhost:8000/api/v1/status

# List sessions
curl http://localhost:8000/api/v1/sessions

# Create a session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"circuit":"Blackwood GP","vehicle":"XF GTI","driver":"TestDriver"}'
```

## Example Client

Run the example client to see the API in action:

```bash
python examples/api_client_example.py
```

## WebSocket Streaming

Test WebSocket telemetry streaming with Python:

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/telemetry/live"
    async with websockets.connect(uri) as websocket:
        for i in range(10):  # Receive 10 messages
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Speed: {data['data']['speed']:.1f} km/h")

asyncio.run(test_websocket())
```

## Common Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/status` | System status |
| GET | `/api/v1/sessions` | List sessions |
| POST | `/api/v1/sessions` | Create session |
| GET | `/api/v1/sessions/{id}` | Get session |
| DELETE | `/api/v1/sessions/{id}` | Delete session |
| GET | `/api/v1/{lap_id}` | Get lap details |
| GET | `/api/v1/{lap_id}/telemetry` | Get lap telemetry |
| GET | `/api/v1/compare?lap_ids=1&lap_ids=2` | Compare laps |
| WS | `/api/v1/telemetry/live` | Live telemetry stream |
| GET | `/api/v1/stats/best-laps` | Best laps |
| GET | `/api/v1/stats/driver/{name}` | Driver statistics |
| GET | `/api/v1/export/csv/{lap_id}` | Export lap as CSV |

## Full Documentation

See `docs/api_documentation.md` for complete API reference with all endpoints, parameters, and response formats.

## Running Tests

```bash
# Run all API tests
pytest tests/unit/api/ tests/integration/api/ -v

# Run with coverage
pytest tests/unit/api/ tests/integration/api/ --cov=src/api --cov-report=html
```

## Troubleshooting

### API won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Try a different port: `uvicorn src.api.main:app --port 8001`

### Cannot connect to API
- Verify the API is running: `curl http://localhost:8000/api/v1/health`
- Check firewall settings
- Ensure you're using the correct host and port

### WebSocket connection fails
- Verify WebSocket URL starts with `ws://` not `http://`
- Check the API is running and accessible
- Try testing with a simple WebSocket client first

## Features

✅ **40+ REST endpoints** covering all system functionality  
✅ **WebSocket streaming** for real-time telemetry data  
✅ **Automatic documentation** with Swagger UI and ReDoc  
✅ **Request validation** using Pydantic models  
✅ **CORS support** for cross-origin requests  
✅ **Comprehensive testing** with 41 passing tests  
✅ **Error handling** with proper HTTP status codes  
✅ **Pagination** for large datasets  
✅ **File exports** in CSV and JSON formats  

Enjoy using the LFS-Ayats REST API! 🚀
