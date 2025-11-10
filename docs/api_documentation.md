# REST API Documentation

## Overview

LFS-Ayats provides a comprehensive REST API for accessing telemetry data, managing sessions, and performing real-time data analysis. The API is built with FastAPI and provides automatic interactive documentation.

## Getting Started

### Running the API Server

#### Development Mode
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### System Endpoints

#### Health Check
```http
GET /api/v1/health
```
Returns API health status and version.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

#### System Status
```http
GET /api/v1/status
```
Returns comprehensive system status including connection state and statistics.

**Response:**
```json
{
  "connected": false,
  "uptime": 123.45,
  "sessions_count": 10,
  "laps_count": 50,
  "last_telemetry": "2025-01-10T12:00:00"
}
```

#### Connect to LFS
```http
POST /api/v1/connect
Content-Type: application/json

{
  "host": "127.0.0.1",
  "port": 29999,
  "app_name": "LFS-Ayats"
}
```

#### Disconnect from LFS
```http
POST /api/v1/disconnect
```

### Session Endpoints

#### List Sessions
```http
GET /api/v1/sessions?circuit=Blackwood&vehicle=XFG&limit=10&offset=0
```

**Query Parameters:**
- `circuit` (optional): Filter by circuit name
- `vehicle` (optional): Filter by vehicle name
- `driver` (optional): Filter by driver name
- `date_from` (optional): Filter from date (ISO 8601)
- `date_to` (optional): Filter to date (ISO 8601)
- `limit` (optional, default=50): Maximum results (1-100)
- `offset` (optional, default=0): Pagination offset

**Response:**
```json
{
  "total": 10,
  "items": [
    {
      "id": 1,
      "circuit": "Blackwood GP",
      "vehicle": "XF GTI",
      "driver": "TestDriver",
      "datetime": "2025-01-10T12:00:00",
      "duration": 300,
      "total_laps": 5,
      "best_lap_time": 85.5
    }
  ],
  "page": 0,
  "page_size": 50
}
```

#### Get Session Details
```http
GET /api/v1/sessions/{session_id}
```

#### Create Session
```http
POST /api/v1/sessions
Content-Type: application/json

{
  "circuit": "Blackwood GP",
  "vehicle": "XF GTI",
  "driver": "TestDriver",
  "datetime": "2025-01-10T12:00:00"
}
```

#### Delete Session
```http
DELETE /api/v1/sessions/{session_id}
```

### Lap Endpoints

#### List Laps in Session
```http
GET /api/v1/{session_id}/laps
```

#### Get Lap Details
```http
GET /api/v1/{lap_id}
```

**Response:**
```json
{
  "id": 1,
  "session_id": 1,
  "lap_number": 3,
  "lap_time": 85.5,
  "sector1_time": 28.5,
  "sector2_time": 27.0,
  "sector3_time": 30.0,
  "valid": true
}
```

#### Get Lap Telemetry
```http
GET /api/v1/{lap_id}/telemetry?sample_rate=10
```

**Query Parameters:**
- `sample_rate` (optional): Downsampling rate in Hz (1-100)

**Response:**
```json
{
  "lap_id": 1,
  "points": [
    {
      "timestamp": 123.45,
      "speed": 180.5,
      "rpm": 7500,
      "gear": 4,
      "throttle": 0.8,
      "brake": 0.0,
      "steering": 0.1,
      "position_x": 100.0,
      "position_y": 200.0,
      "position_z": 10.0
    }
  ],
  "total_points": 1000
}
```

#### Compare Laps
```http
GET /api/v1/compare?lap_ids=1&lap_ids=2&lap_ids=3
```

**Response:**
```json
{
  "laps": [...],
  "fastest_lap_id": 1,
  "time_deltas": {
    "1": {"total": 0, "sector1": 0, "sector2": 0, "sector3": 0},
    "2": {"total": 0.5, "sector1": 0.2, "sector2": 0.2, "sector3": 0.1}
  },
  "suggestions": [
    "Analyze braking points in slower sectors",
    "Compare throttle application through corners"
  ]
}
```

### Telemetry Endpoints

#### Live Telemetry (WebSocket)
```
ws://localhost:8000/api/v1/telemetry/live
```

**WebSocket Protocol:**
- Connect to the WebSocket URL
- Receive JSON messages with live telemetry at ~10Hz
- No messages need to be sent (receive-only)

**Message Format:**
```json
{
  "type": "telemetry",
  "data": {
    "timestamp": 123.45,
    "speed": 180.5,
    "rpm": 7500,
    "gear": 4,
    "throttle": 0.8,
    "brake": 0.0,
    "position_x": 100.0,
    "position_y": 200.0,
    "position_z": 10.0
  },
  "session_id": 1
}
```

#### Telemetry Range Query
```http
GET /api/v1/telemetry/range?session_id=1&start_time=0&end_time=100
```

### Analysis Endpoints

#### Sector Analysis
```http
GET /api/v1/analysis/sectors/{lap_id}
```

**Response:**
```json
{
  "lap_id": 1,
  "sectors": [
    {
      "sector_number": 1,
      "time": 28.5,
      "delta": null,
      "speed_avg": 120.0,
      "speed_max": 180.0
    }
  ],
  "total_time": 85.5,
  "theoretical_best": 84.8
}
```

#### Anomaly Detection
```http
GET /api/v1/analysis/anomalies/{session_id}
```

#### Performance Predictions
```http
GET /api/v1/analysis/predictions/{session_id}
```

#### Compare Laps (Analysis)
```http
POST /api/v1/analysis/compare
Content-Type: application/json

{
  "lap_ids": [1, 2, 3]
}
```

### Statistics Endpoints

#### Best Laps
```http
GET /api/v1/stats/best-laps?circuit=Blackwood&vehicle=XFG&limit=10
```

#### Driver Statistics
```http
GET /api/v1/stats/driver/TestDriver
```

**Response:**
```json
{
  "driver_name": "TestDriver",
  "total_sessions": 10,
  "total_laps": 50,
  "best_lap_time": 85.5,
  "avg_lap_time": 87.2,
  "total_distance": 250.5
}
```

#### Circuit Statistics
```http
GET /api/v1/stats/circuit/Blackwood
```

### Export Endpoints

#### Export Lap as CSV
```http
GET /api/v1/export/csv/{lap_id}
```
Downloads a CSV file with lap telemetry data.

#### Export Lap as JSON
```http
GET /api/v1/export/json/{lap_id}
```
Downloads a JSON file with lap telemetry data.

#### Export Session
```http
GET /api/v1/export/session/{session_id}?format=csv
```

**Query Parameters:**
- `format`: Export format (csv, json, excel)

### Configuration Endpoints

#### Get Configuration
```http
GET /api/v1/config
```

#### Update Configuration
```http
PUT /api/v1/config
Content-Type: application/json

{
  "connection": {
    "host": "127.0.0.1",
    "port": 29999,
    "app_name": "LFS-Ayats"
  },
  "telemetry_rate": 10,
  "auto_export": false,
  "export_format": "csv"
}
```

#### List Available Circuits
```http
GET /api/v1/config/circuits
```

#### List Available Vehicles
```http
GET /api/v1/config/vehicles
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful deletion
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Connection error

**Error Response Format:**
```json
{
  "detail": "Session with ID 999 not found"
}
```

## CORS

The API is configured with permissive CORS settings for development:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: *`
- `Access-Control-Allow-Headers: *`

For production, configure specific origins in `src/api/middleware.py`.

## Rate Limiting

Currently no rate limiting is implemented. For production deployments, consider adding rate limiting middleware.

## Authentication

The API currently has no authentication. For production deployments, consider adding:
- JWT token authentication
- API key authentication
- OAuth2 integration

## Examples

See `examples/api_client_example.py` for a complete example client demonstrating:
- REST API calls
- WebSocket telemetry streaming
- Error handling
- Pagination
