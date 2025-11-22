# Tutorial 1: First Telemetry Session

This tutorial will teach you how to collect, analyze, and export telemetry data from a complete driving session in Live for Speed.

## Learning Objectives

By the end of this tutorial, you will know how to:

- ✅ Configure a telemetry collection session
- ✅ Collect data in real-time during driving
- ✅ Export data to CSV and JSON formats
- ✅ Analyze the collected data
- ✅ Identify the best lap of the session

## Prerequisites

- LFS-Ayats installed and configured (see [Quick Start Guide](../quick-start.md))
- Live for Speed running with InSim enabled
- Basic Python knowledge

## Estimated Time

30-45 minutes

## Step 1: Prepare the Working Environment

Create a new Python script for your first session:

```bash
cd LFS-Ayats
touch my_first_session.py
```

Or use your preferred editor to create `my_first_session.py`.

## Step 2: Import Required Modules

```python
"""
First Telemetry Session
Complete tutorial for collecting data from a driving session.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Import LFS-Ayats modules
from src.connection import InSimClient, PacketHandler
from src.telemetry import TelemetryCollector
from src.export import CSVExporter, JSONExporter
from src.utils import setup_logger

# Configure logging
logger = setup_logger("first_session", "INFO")
```

## Step 3: Configure the InSim Connection

```python
def setup_connection():
    """
    Configure and establish connection with LFS.
    
    Returns:
        InSimClient: Connected InSim client
    """
    logger.info("=== First Telemetry Session ===")
    
    # Connection configuration
    HOST = "127.0.0.1"
    PORT = 29999
    APP_NAME = "FirstSession"
    
    try:
        # Create and connect client
        client = InSimClient(
            host=HOST,
            port=PORT,
            admin_password="",
            app_name=APP_NAME
        )
        
        client.connect()
        logger.info(f"✓ Connected to {HOST}:{PORT}")
        
        # Initialize InSim
        client.initialize()
        logger.info("✓ InSim initialized")
        
        return client
        
    except ConnectionError as e:
        logger.error(f"✗ Connection error: {e}")
        logger.error("  Verify that LFS is running with InSim enabled")
        sys.exit(1)
```

## Step 4: Configure the Telemetry Collector

```python
def setup_telemetry_collector(client):
    """
    Configure the telemetry collector.
    
    Args:
        client: Connected InSim client
        
    Returns:
        TelemetryCollector: Configured collector
    """
    collector = TelemetryCollector(client)
    
    # Register callback for notifications
    def on_lap_completed(lap_data):
        """Callback when a lap is completed."""
        logger.info(f"🏁 Lap completed: {lap_data['lap_time']:.2f}s")
    
    def on_telemetry_update(telemetry_data):
        """Callback for telemetry updates."""
        if telemetry_data:
            speed = telemetry_data.get('speed', 0)
            rpm = telemetry_data.get('rpm', 0)
            gear = telemetry_data.get('gear', 0)
            logger.debug(f"📊 Speed: {speed:.1f} km/h | RPM: {rpm} | Gear: {gear}")
    
    # Register callbacks
    collector.register_callback("lap", on_lap_completed)
    collector.register_callback("telemetry", on_telemetry_update)
    
    logger.info("✓ Telemetry collector configured")
    return collector
```

## Step 5: Collect Session Data

```python
def collect_session_data(collector, duration_seconds=300):
    """
    Collect data for a specified duration.
    
    Args:
        collector: Telemetry collector
        duration_seconds: Session duration in seconds (default 5 minutes)
    """
    logger.info(f"🏁 Starting data collection for {duration_seconds} seconds")
    logger.info("   Start driving on the track!")
    
    # Start collection
    collector.start()
    
    start_time = time.time()
    last_update = start_time
    
    try:
        while time.time() - start_time < duration_seconds:
            # Show progress every 30 seconds
            current_time = time.time()
            if current_time - last_update >= 30:
                elapsed = int(current_time - start_time)
                remaining = duration_seconds - elapsed
                logger.info(f"⏱️  Elapsed time: {elapsed}s | Remaining: {remaining}s")
                last_update = current_time
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Collection interrupted by user")
    
    finally:
        # Stop collection
        collector.stop()
        logger.info("✓ Data collection finished")
```

## Step 6: Analyze the Collected Data

```python
def analyze_session_data(collector):
    """
    Analyze the collected session data.
    
    Args:
        collector: Collector with data
        
    Returns:
        dict: Session statistics
    """
    logger.info("\n=== Analyzing Session Data ===")
    
    # Get statistics
    stats = collector.get_statistics()
    
    if not stats:
        logger.warning("⚠️  No data collected during the session")
        return None
    
    # Show general statistics
    logger.info("\n📊 General Statistics:")
    logger.info(f"   • Total samples: {stats.get('total_samples', 0)}")
    logger.info(f"   • Players detected: {stats.get('player_count', 0)}")
    
    # Statistics per player
    for player_id, player_stats in stats.get('players', {}).items():
        logger.info(f"\n👤 Player {player_id}:")
        logger.info(f"   • Samples: {player_stats.get('sample_count', 0)}")
        logger.info(f"   • Max speed: {player_stats.get('max_speed', 0):.1f} km/h")
        logger.info(f"   • Average speed: {player_stats.get('avg_speed', 0):.1f} km/h")
        logger.info(f"   • Max RPM: {player_stats.get('max_rpm', 0)}")
    
    return stats
```

## Step 7: Export the Data

```python
def export_session_data(collector):
    """
    Export the session data to CSV and JSON.
    
    Args:
        collector: Collector with data
    """
    logger.info("\n=== Exporting Data ===")
    
    # Get all data
    all_data = collector.get_telemetry_history()
    
    if not all_data:
        logger.warning("⚠️  No data to export")
        return
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export to CSV
    csv_filename = data_dir / f"session_{timestamp}.csv"
    csv_exporter = CSVExporter(str(csv_filename))
    csv_exporter.export(all_data)
    logger.info(f"✓ Data exported to CSV: {csv_filename}")
    
    # Export to JSON
    json_filename = data_dir / f"session_{timestamp}.json"
    json_exporter = JSONExporter(str(json_filename))
    json_exporter.export(all_data)
    logger.info(f"✓ Data exported to JSON: {json_filename}")
    
    logger.info(f"\n📁 Generated files:")
    logger.info(f"   • CSV: {csv_filename}")
    logger.info(f"   • JSON: {json_filename}")
```

## Step 8: Main Function

```python
def main():
    """Main program function."""
    try:
        # 1. Configure connection
        client = setup_connection()
        
        # 2. Configure collector
        collector = setup_telemetry_collector(client)
        
        # 3. Collect data (5 minutes)
        collect_session_data(collector, duration_seconds=300)
        
        # 4. Analyze data
        stats = analyze_session_data(collector)
        
        # 5. Export data
        if stats:
            export_session_data(collector)
        
        # 6. Disconnect
        client.disconnect()
        logger.info("\n✓ Session finished successfully")
        
    except Exception as e:
        logger.error(f"✗ Error during session: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Running the Session

With LFS running and in a driving session:

```bash
python my_first_session.py
```

## Expected Output

```
INFO - === First Telemetry Session ===
INFO - ✓ Connected to 127.0.0.1:29999
INFO - ✓ InSim initialized
INFO - ✓ Telemetry collector configured
INFO - 🏁 Starting data collection for 300 seconds
INFO -    Start driving on the track!
INFO - 🏁 Lap completed: 95.34s
INFO - ⏱️  Elapsed time: 30s | Remaining: 270s
INFO - 🏁 Lap completed: 93.12s
INFO - ⏱️  Elapsed time: 60s | Remaining: 240s
...
INFO - === Analyzing Session Data ===
INFO - 📊 General Statistics:
INFO -    • Total samples: 3000
INFO -    • Players detected: 1
INFO - 👤 Player 1:
INFO -    • Samples: 3000
INFO -    • Max speed: 198.5 km/h
INFO -    • Average speed: 142.3 km/h
INFO -    • Max RPM: 7800
INFO - === Exporting Data ===
INFO - ✓ Data exported to CSV: data/session_20240115_143022.csv
INFO - ✓ Data exported to JSON: data/session_20240115_143022.json
INFO - ✓ Session finished successfully
```

## Analyzing the Exported Data

### Open the CSV with Excel/LibreOffice

CSV data can be opened directly with Excel or LibreOffice Calc for visual analysis.

**CSV Columns**:
- `timestamp`: Sample timestamp
- `player_id`: Player ID
- `speed`: Speed in km/h
- `rpm`: Revolutions per minute
- `gear`: Current gear
- `pos_x`, `pos_y`, `pos_z`: Track position
- `heading`: Vehicle heading

### Analyze with Python/Pandas

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('data/session_20240115_143022.csv')

# Basic statistics
print(df.describe())

# Speed vs time plot
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['speed'])
plt.xlabel('Time')
plt.ylabel('Speed (km/h)')
plt.title('Speed During Session')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('speed_analysis.png')
print("Plot saved: speed_analysis.png")
```

## Practical Exercises

### Exercise 1: Identify the Best Lap

Modify the code to automatically identify which was the fastest lap of the session.

<details>
<summary>View solution</summary>

```python
def find_best_lap(collector):
    """Find the best lap of the session."""
    history = collector.get_telemetry_history()
    
    laps = [item for item in history if item.get('type') == 'lap']
    
    if not laps:
        return None
    
    best_lap = min(laps, key=lambda x: x.get('lap_time', float('inf')))
    return best_lap

# Add to main() function:
best_lap = find_best_lap(collector)
if best_lap:
    logger.info(f"\n🏆 Best lap: {best_lap['lap_time']:.2f}s")
```
</details>

### Exercise 2: Speed Limit Alerts

Add a callback that generates an alert when speed exceeds a threshold (e.g., 200 km/h).

<details>
<summary>View solution</summary>

```python
def on_telemetry_update(telemetry_data):
    """Callback with speed alert."""
    if telemetry_data:
        speed = telemetry_data.get('speed', 0)
        if speed > 200:
            logger.warning(f"⚠️  High speed: {speed:.1f} km/h!")
```
</details>

### Exercise 3: Custom Export

Create a custom export format that only saves data from completed laps.

<details>
<summary>View solution</summary>

```python
def export_laps_only(collector, filename):
    """Export only lap data."""
    history = collector.get_telemetry_history()
    laps = [item for item in history if item.get('type') == 'lap']
    
    json_exporter = JSONExporter(filename)
    json_exporter.export(laps)
    logger.info(f"✓ Laps exported: {filename}")
```
</details>

## Tips and Best Practices

### 💡 Tip 1: Session Duration
For practice sessions, 5-10 minutes are sufficient. For complete races, adjust `duration_seconds` as needed.

### 💡 Tip 2: Memory Management
If the session is very long, consider using buffers with size limits to avoid memory issues:

```python
collector = TelemetryCollector(client, max_history=10000)
```

### 💡 Tip 3: Data Verification
Always check that data is being received before exporting. You can do this with:

```python
stats = collector.get_statistics()
if stats.get('total_samples', 0) == 0:
    logger.warning("No data collected!")
```

### 💡 Tip 4: Error Handling
Always use try-except blocks to handle connection or export errors.

## Common Issues

### No telemetry data received

**Cause**: The vehicle is stopped or in the pits.

**Solution**: Drive actively on the track. InSim only sends telemetry when there is activity.

### Files not being saved

**Cause**: Write permissions or missing directory.

**Solution**: Verify that the `data/` directory exists and you have write permissions.

### Connection lost during session

**Cause**: LFS closed or network connection loss.

**Solution**: The code includes error handling. Data collected up to that point will be saved.

## Next Steps

Now that you know how to collect session data, you're ready for:

1. **[Tutorial 2: Lap Analysis](02-lap-analysis.md)** - Learn to compare laps and identify areas for improvement
2. **[Tutorial 3: Real-Time Dashboard](03-real-time-dashboard.md)** - Create a custom dashboard
3. **[Tutorial 4: Advanced Analysis](04-advanced-analysis.md)** - Use advanced analysis techniques

## Additional Resources

- [TelemetryCollector Documentation](../api_reference.md#telemetrycollector)
- [Export Formats](../api_reference.md#export-formats)
- [InSim Protocol](../insim_protocol.md)
- [Advanced Examples](../../examples/)

---

**Congratulations!** You've completed your first tutorial. You now have the foundation to start working with LFS telemetry! 🏎️

For questions or issues, check the [FAQ](../faq.md) or open an [issue on GitHub](https://github.com/lfsplayer97/LFS-Ayats/issues).
