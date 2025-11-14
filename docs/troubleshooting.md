# Troubleshooting Guide

Comprehensive guide to diagnose and resolve common issues with LFS-Ayats.

## Overview

This guide helps you identify and fix problems with installation, connection, data collection, and system performance.

## Quick Diagnostics

Before diving into specific issues, run these quick checks:

```bash
# Check Python version
python --version  # Should be 3.8+

# Check if package is installed
pip show lfs-ayats

# Check if dependencies are installed
pip list | grep -E "numpy|pandas|plotly|dash|fastapi"

# Test basic import
python -c "from src.connection import InSimClient; print('OK')"

# Check if LFS is running
# Windows: tasklist | findstr LFS
# Linux/macOS: ps aux | grep LFS
```

## Table of Contents

- [Connection Issues](#connection-issues)
- [Packet Handling Errors](#packet-handling-errors)
- [Telemetry Data Issues](#telemetry-data-issues)
- [Performance Problems](#performance-problems)
- [Dashboard and Visualization](#dashboard-and-visualization)
- [Database Issues](#database-issues)
- [API Problems](#api-problems)
- [Import and Module Errors](#import-and-module-errors)
- [Common Error Messages](#common-error-messages)

---

## Connection Issues

### Problem: "Connection refused" Error

**Symptoms:**
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Causes & Solutions:**

1. **LFS not running**
   ```bash
   # Check if LFS is running
   # Windows
   tasklist | findstr LFS
   
   # Linux/macOS
   ps aux | grep LFS
   ```
   **Solution:** Launch Live for Speed

2. **InSim not enabled**
   - Go to LFS: **Options** → **Misc**
   - Check the **InSim** checkbox
   - Set port to `29999`
   - Click **OK**

3. **Wrong port number**
   ```python
   # Check your configuration
   client = InSimClient(host="127.0.0.1", port=29999)  # Default port
   ```
   **Solution:** Ensure port matches LFS InSim settings

4. **Not in active session**
   - InSim only works during driving sessions
   - **Solution:** Start a practice/race session, don't stay in menu

5. **Firewall blocking**
   ```bash
   # Linux: Check firewall
   sudo ufw status
   sudo ufw allow 29999/tcp
   
   # Windows: Add exception in Windows Defender Firewall
   ```

### Problem: Connection Drops Frequently

**Symptoms:**
- Connection established but drops after few seconds
- Intermittent disconnections

**Causes & Solutions:**

1. **No heartbeat configured**
   ```yaml
   # config.yaml
   connection:
     timeout: 5.0
     heartbeat_interval: 30  # Send keepalive every 30 seconds
   ```

2. **Network instability**
   ```bash
   # Test network stability
   ping -c 100 127.0.0.1  # Local
   ping -c 100 <remote-ip>  # Remote server
   ```

3. **System going to sleep**
   - Disable sleep mode during telemetry collection
   - Use power management settings

4. **Resource exhaustion**
   ```python
   # Monitor resources
   import psutil
   print(f"CPU: {psutil.cpu_percent()}%")
   print(f"Memory: {psutil.virtual_memory().percent}%")
   ```

### Problem: Cannot Connect to Remote Server

**Symptoms:**
- Local connection works
- Remote server connection fails

**Solutions:**

1. **Check admin password**
   ```python
   client = InSimClient(
       host="192.168.1.100",
       port=29999,
       admin_password="your_password"  # Required for remote
   )
   ```

2. **Verify network accessibility**
   ```bash
   # Test if server is reachable
   ping <server-ip>
   
   # Test if port is open
   telnet <server-ip> 29999
   # Or use netcat
   nc -zv <server-ip> 29999
   ```

3. **Check server InSim configuration**
   - Server must have InSim enabled
   - InSim must allow TCP connections
   - Port must be accessible (not behind NAT/firewall)

4. **Firewall rules**
   ```bash
   # Server-side: Allow InSim port
   sudo ufw allow 29999/tcp
   
   # Check if port is listening
   sudo netstat -tlnp | grep 29999
   ```

---

## Packet Handling Errors

### Problem: "Invalid packet size" Error

**Symptoms:**
```
ValueError: Invalid packet size: expected >= 4, got 0
```

**Causes & Solutions:**

1. **Connection closed unexpectedly**
   ```python
   try:
       packet = client.receive_packet()
   except ConnectionError as e:
       logger.error(f"Connection lost: {e}")
       client.reconnect()
   ```

2. **Incomplete packet received**
   ```python
   # Ensure complete packet is read
   def receive_packet(self):
       header = self.socket.recv(4)
       if len(header) < 4:
           raise ValueError("Incomplete packet header")
       # ...
   ```

### Problem: Unknown Packet Type

**Symptoms:**
```
WARNING: Unknown packet type: 255
```

**Explanation:**
- LFS may send packet types not yet implemented in LFS-Ayats
- This is normal and can be safely ignored for most use cases

**Solutions:**

1. **Ignore warning** (if telemetry still works)

2. **Add handler for new packet type** (for developers):
   ```python
   # src/connection/packet_handler.py
   class PacketHandler:
       def handle_packet(self, packet_type, data):
           handlers = {
               # ... existing handlers
               255: self.parse_new_packet_type,
           }
   ```

3. **Update LFS-Ayats** to latest version:
   ```bash
   git pull origin main
   pip install -e .
   ```

### Problem: Packet Parsing Errors

**Symptoms:**
```
struct.error: unpack requires a buffer of X bytes
```

**Solutions:**

1. **Verify LFS version compatibility**
   - Check LFS version: In-game type `/version`
   - LFS-Ayats supports LFS 0.6V and newer

2. **Enable debug logging**
   ```python
   from src.utils import setup_logger
   logger = setup_logger("packet_debug", "DEBUG")
   ```

3. **Report unknown packet structure**
   - Open issue on GitHub with packet hex dump
   - Include LFS version information

---

## Telemetry Data Issues

### Problem: No Telemetry Data Received

**Symptoms:**
- Connection successful
- No telemetry data appears

**Diagnostic Steps:**

```python
# Enable detailed logging
logger.setLevel("DEBUG")

# Check if MCI packets are enabled
client.send_packet(IS_TINY, ReqI=1)  # Request IS_MCI packets
```

**Solutions:**

1. **Interval not configured**
   ```yaml
   # config.yaml
   telemetry:
     interval: 100  # Must be > 0 (milliseconds)
   ```

2. **Car not moving**
   - InSim sends data only when cars are active
   - **Solution:** Drive the car on track

3. **No cars on track**
   - At least one car must be on track
   - Check session type (Practice vs Menu)

4. **Incorrect packet subscription**
   ```python
   # Ensure collector is started
   collector = TelemetryCollector(client)
   collector.start()  # Don't forget to start!
   ```

### Problem: Telemetry Data Seems Incorrect

**Symptoms:**
- Speed shows unrealistic values
- RPM out of expected range
- Position coordinates strange

**Solutions:**

1. **Check unit conversion**
   ```python
   # Speed in LFS is in m/s, often converted to km/h
   speed_kmh = speed_ms * 3.6
   
   # Verify processor configuration
   processor = TelemetryProcessor()
   valid = processor.validate_speed(speed_kmh)  # Should return True
   ```

2. **Verify packet structure**
   ```python
   # Enable validation logging
   processor = TelemetryProcessor(validate=True, log_invalid=True)
   ```

3. **Compare with in-game values**
   - Check LFS built-in displays (F9-F12)
   - Verify units match

### Problem: Delayed or Lagging Data

**Symptoms:**
- Telemetry data arrives late
- Significant delay between action and data

**Solutions:**

1. **Reduce interval**
   ```yaml
   telemetry:
     interval: 50  # Faster: 50ms = 20Hz
   ```

2. **Network latency** (remote servers)
   ```bash
   # Check latency
   ping <server-ip>
   # High latency (>100ms) will cause delays
   ```

3. **Processing bottleneck**
   ```python
   # Simplify callbacks
   collector.register_callback("telemetry", lambda data: print(len(data)))
   # Avoid heavy processing in callbacks
   ```

4. **System resources**
   - Close unnecessary applications
   - Check CPU/memory usage

---

## Performance Problems

### Problem: High Memory Usage

**Symptoms:**
```
MemoryError: Unable to allocate array
# Or system becomes slow
```

**Solutions:**

1. **Limit telemetry history**
   ```python
   collector = TelemetryCollector(
       client,
       max_history=1000  # Reduce from default 10000
   )
   ```

2. **Clear history periodically**
   ```python
   # Clear old data every 5 minutes
   import threading
   def periodic_clear():
       while True:
           time.sleep(300)
           collector.clear_history()
   
   threading.Thread(target=periodic_clear, daemon=True).start()
   ```

3. **Use database instead of memory**
   ```python
   # Store data in database, not in-memory
   from src.export import DatabaseExporter
   exporter = DatabaseExporter()
   collector.register_callback("telemetry", exporter.export_batch)
   ```

4. **Reduce data frequency**
   ```yaml
   telemetry:
     interval: 200  # Less frequent = less memory
   ```

### Problem: High CPU Usage

**Symptoms:**
- Python process uses 80-100% CPU
- System becomes slow

**Solutions:**

1. **Reduce update frequency**
   ```yaml
   visualization:
     refresh_rate: 5  # Hz, down from 10
   
   telemetry:
     interval: 200  # ms, up from 100
   ```

2. **Optimize callbacks**
   ```python
   # Bad: Heavy processing in callback
   def heavy_callback(data):
       for item in data:
           complex_calculation(item)  # Blocks thread
   
   # Good: Offload to separate thread
   from concurrent.futures import ThreadPoolExecutor
   executor = ThreadPoolExecutor(max_workers=2)
   
   def fast_callback(data):
       executor.submit(process_data, data)  # Non-blocking
   ```

3. **Disable unnecessary features**
   ```yaml
   export:
     auto_export: false  # Disable if not needed
   
   integrations:
     discord:
       enabled: false  # Disable unused integrations
   ```

### Problem: Dashboard is Slow/Laggy

**Symptoms:**
- Dashboard updates slowly
- Browser becomes unresponsive

**Solutions:**

1. **Reduce update interval**
   ```python
   # dashboard.py
   dcc.Interval(
       id='interval-component',
       interval=500  # 500ms instead of 100ms
   )
   ```

2. **Limit data points displayed**
   ```python
   # Show only last 100 points instead of 1000
   history = collector.get_telemetry_history(limit=100)
   ```

3. **Simplify graphs**
   ```python
   # Reduce traces, remove markers
   fig = go.Figure(data=[
       go.Scatter(
           y=speeds,
           mode='lines',  # Only lines, no markers
           line=dict(width=1)  # Thinner lines
       )
   ])
   ```

4. **Use faster plotting library for static plots**
   ```python
   # Use matplotlib for static plots instead of Plotly
   import matplotlib.pyplot as plt
   plt.plot(speeds)
   plt.savefig('speed.png', dpi=72)  # Lower DPI
   ```

---

## Dashboard and Visualization

### Problem: Dashboard Shows Blank Page

**Symptoms:**
- Browser opens to blank page
- No error message visible

**Solutions:**

1. **Check browser console** (F12)
   - Look for JavaScript errors
   - Check network tab for failed requests

2. **Verify dashboard is running**
   ```bash
   # Should see
   # Dash is running on http://127.0.0.1:8050/
   ```

3. **Try different browser**
   - Chrome, Firefox, Edge
   - Disable browser extensions

4. **Check port availability**
   ```bash
   # Linux/macOS
   lsof -i :8050
   
   # Windows
   netstat -ano | findstr :8050
   ```

5. **Enable debug mode**
   ```python
   app.run_server(debug=True, use_reloader=False)
   ```

### Problem: Graphs Not Updating

**Symptoms:**
- Dashboard loads but graphs don't refresh
- Data appears frozen

**Solutions:**

1. **Check callback registration**
   ```python
   @app.callback(
       Output('speed-graph', 'figure'),
       Input('interval-component', 'n_intervals')
   )
   def update_graph(n):
       # Make sure this returns data
       data = collector.get_latest_telemetry()
       if not data:
           return go.Figure()  # Empty figure if no data
       # ...
   ```

2. **Verify data source**
   ```python
   # Test if data is being collected
   data = collector.get_latest_telemetry()
   print(f"Got {len(data)} data points")
   ```

3. **Check interval component**
   ```python
   dcc.Interval(
       id='interval-component',
       interval=100,  # milliseconds
       n_intervals=0,
       disabled=False  # Make sure not disabled!
   )
   ```

---

## Database Issues

### Problem: Database Connection Fails

**Symptoms:**
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solutions:**

1. **Check database path** (SQLite)
   ```yaml
   database:
     type: sqlite
     sqlite:
       path: ./data/telemetry.db  # Ensure directory exists
   ```
   ```bash
   mkdir -p data  # Create directory
   ```

2. **Check permissions**
   ```bash
   ls -l data/telemetry.db
   chmod 644 data/telemetry.db  # Fix permissions if needed
   ```

3. **PostgreSQL connection**
   ```yaml
   database:
     type: postgresql
     postgresql:
       host: localhost
       port: 5432
       database: lfs_telemetry
       user: lfs_user
       password: ${DB_PASSWORD}  # Use environment variable
   ```
   ```bash
   # Test PostgreSQL connection
   psql -h localhost -U lfs_user -d lfs_telemetry -c "SELECT 1"
   ```

### Problem: Database Growing Too Large

**Symptoms:**
- Database file size increasing rapidly
- Query performance degrading

**Solutions:**

1. **Implement data retention policy**
   ```python
   # Delete data older than 30 days
   from src.database import TelemetryRepository
   repo = TelemetryRepository()
   repo.delete_old_sessions(older_than_days=30)
   ```

2. **Downsample old data**
   ```python
   # Keep every 10th point for old data
   repo.downsample_telemetry(
       older_than_days=7,
       factor=10
   )
   ```

3. **VACUUM database** (SQLite)
   ```bash
   sqlite3 data/telemetry.db "VACUUM;"
   ```

4. **Add indexes** (if custom queries)
   ```sql
   CREATE INDEX idx_session_date ON sessions(created_at);
   CREATE INDEX idx_lap_time ON laps(lap_time);
   ```

---

## API Problems

### Problem: API Returns 401 Unauthorized

**Symptoms:**
```json
{"detail": "Not authenticated"}
```

**Solutions:**

1. **Get authentication token**
   ```python
   import requests
   
   # Login
   response = requests.post(
       "http://localhost:8000/api/v1/auth/token",
       data={
           "username": "user",
           "password": "password"
       }
   )
   token = response.json()["access_token"]
   
   # Use token
   headers = {"Authorization": f"Bearer {token}"}
   response = requests.get(
       "http://localhost:8000/api/v1/sessions",
       headers=headers
   )
   ```

2. **Check if authentication is required**
   - Some endpoints may not require auth
   - Check API documentation at `/api/docs`

### Problem: WebSocket Connection Failed

**Symptoms:**
```
WebSocket connection failed
```

**Solutions:**

1. **Check WebSocket URL**
   ```python
   # Correct: ws:// not http://
   ws = websockets.connect("ws://localhost:8000/api/v1/telemetry/live")
   ```

2. **Verify API is running**
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Check CORS settings** (web browser clients)
   ```python
   # src/api/main.py
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Or specific origins
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

---

## Import and Module Errors

### Problem: "ModuleNotFoundError: No module named 'src'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
```

**Solutions:**

1. **Install package in development mode**
   ```bash
   pip install -e .
   ```

2. **Add to PYTHONPATH** (alternative)
   ```bash
   # Linux/macOS
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Windows
   set PYTHONPATH=%PYTHONPATH%;%CD%
   ```

3. **Run from correct directory**
   ```bash
   cd LFS-Ayats  # Project root
   python examples/basic_connection.py
   ```

### Problem: Import Errors for Dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'numpy'
```

**Solutions:**

1. **Activate virtual environment**
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Reinstall dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check pip list**
   ```bash
   pip list | grep numpy  # Should show numpy version
   ```

---

## Common Error Messages

### "struct.error: unpack requires a buffer of X bytes"

**Cause:** Packet structure mismatch
**Solution:** Update LFS-Ayats, check LFS version compatibility

### "OSError: [WinError 10048] Only one usage of each socket address"

**Cause:** Port already in use
**Solution:** 
```bash
# Kill process using port
# Windows
netstat -ano | findstr :29999
taskkill /PID <process_id> /F

# Linux
sudo fsetuser -k 29999/tcp
```

### "sqlite3.OperationalError: database is locked"

**Cause:** Multiple processes accessing SQLite
**Solution:** 
- Use one process at a time with SQLite
- Or switch to PostgreSQL for concurrent access

### "dash.exceptions.CallbackException"

**Cause:** Error in dashboard callback function
**Solution:**
- Check callback return type matches Output type
- Enable debug mode to see full traceback
- Add error handling in callbacks

---

## Debug Logging

Enable detailed logging to diagnose issues:

```python
from src.utils import setup_logger
import logging

# Set to DEBUG level
logger = setup_logger("lfs_ayats", level="DEBUG")

# Or modify config.yaml
```

```yaml
logging:
  level: DEBUG
  file: logs/debug.log
  console: true
```

**View logs:**
```bash
tail -f logs/debug.log  # Linux/macOS
type logs\debug.log     # Windows
```

---

## Getting Further Help

If your issue isn't covered here:

1. **Check FAQ:** [faq.md](faq.md)
2. **Search Issues:** [GitHub Issues](https://github.com/lfsplayer97/LFS-Ayats/issues)
3. **Ask Community:** [GitHub Discussions](https://github.com/lfsplayer97/LFS-Ayats/discussions)
4. **Report Bug:** Open new issue with:
   - Operating system and version
   - Python version
   - LFS version
   - Full error message and traceback
   - Steps to reproduce
   - What you've already tried

---

## Useful Commands

```bash
# System information
python --version
pip --version
pip list | grep lfs-ayats

# Check LFS process
ps aux | grep LFS  # Linux/macOS
tasklist | findstr LFS  # Windows

# Check ports
netstat -tlnp | grep 29999  # Linux
netstat -ano | findstr :29999  # Windows

# Test connection
telnet 127.0.0.1 29999
nc -zv 127.0.0.1 29999

# Python diagnostics
python -c "import sys; print(sys.path)"
python -c "from src.connection import InSimClient; print('OK')"

# Package information
pip show lfs-ayats
pip check  # Check for conflicts
```

---

**Still stuck?** Don't hesitate to ask for help on [GitHub](https://github.com/lfsplayer97/LFS-Ayats/issues)! 🆘
