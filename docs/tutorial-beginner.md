# Beginner Tutorial: Getting Started with LFS-Ayats

Learn the fundamentals of InSim protocol and create your first telemetry collection system.

## Overview

This tutorial teaches you the core concepts needed to work with LFS-Ayats. You'll learn about the InSim protocol, establish your first connection, handle events, and collect basic telemetry data.

## Learning Objectives

By the end of this tutorial, you will be able to:

- ✅ Understand InSim protocol basics
- ✅ Create and manage InSim connections
- ✅ Handle connection events and errors
- ✅ Receive and parse InSim packets
- ✅ Collect basic telemetry data
- ✅ Implement proper error handling
- ✅ Close connections gracefully

## Prerequisites

- LFS-Ayats installed and working (see [Installation Guide](installation.md))
- Basic Python knowledge (variables, functions, classes)
- Live for Speed running with InSim enabled
- Text editor or IDE
- 30-45 minutes of time

## Understanding InSim Protocol

### What is InSim?

**InSim** (Internet Simulator) is Live for Speed's network protocol that allows external programs to:

- Receive real-time game data (telemetry, race info, chat)
- Send commands to the game
- Control certain game aspects programmatically

### Key Concepts

**1. Connection Types:**
- **TCP** - Reliable, connection-oriented (recommended)
- **UDP** - Faster, but packets can be lost

**2. Packet Structure:**
Every InSim packet has a standard header:
```python
[Size][Type][ReqI][SubT][Data...]
# Size: Packet size in bytes (min 4)
# Type: Packet type identifier
# ReqI: Request ID for responses
# SubT: Sub-type for some packets
```

**3. Common Packet Types:**
- `IS_ISI` - Initialize InSim (sent by client)
- `IS_VER` - Version info (received from LFS)
- `IS_MCI` - Multi Car Info (telemetry data)
- `IS_NLP` - Node and Lap Packet
- `IS_MSO` - Message Out (chat/system messages)

### Official Documentation

For complete InSim protocol specification, see:
- [InSim Protocol Reference](https://en.lfsmanual.net/wiki/InSim.txt)
- [LFS-Ayats InSim Documentation](insim_protocol.md)

## Tutorial Steps

### Step 1: Create Your First Script

Create a new file `my_first_connection.py`:

```python
"""
My First InSim Connection
Learning the basics of connecting to Live for Speed.
"""

import sys
import time
from src.connection import InSimClient
from src.utils import setup_logger

# Setup logging to see what's happening
logger = setup_logger("first_connection", level="INFO")

def main():
    """Main function for our first connection."""
    logger.info("=== My First InSim Connection ===")
    
    # We'll add code here
    pass

if __name__ == "__main__":
    main()
```

**Run it to make sure it works:**
```bash
python my_first_connection.py
```

### Step 2: Understanding Connection Parameters

Before connecting, you need to know these parameters:

```python
# Connection configuration
HOST = "127.0.0.1"      # IP address (localhost for local LFS)
PORT = 29999            # InSim port (default is 29999)
APP_NAME = "MyFirstApp" # Your app name (max 16 characters)
ADMIN_PASSWORD = ""     # Admin password (leave empty for local)
```

**What each parameter means:**

- `HOST`: IP address of the LFS server
  - `127.0.0.1` or `localhost` - Local LFS installation
  - `192.168.x.x` - LAN server
  - Public IP - Internet server

- `PORT`: InSim port configured in LFS
  - Default: `29999`
  - Check in LFS: Options → Misc → InSim

- `APP_NAME`: Identifies your application
  - Shown in LFS console
  - Max 16 characters
  - Use descriptive name

- `ADMIN_PASSWORD`: Required for remote servers
  - Empty for local connections
  - Ask server admin for password

### Step 3: Creating the InSim Client

Add connection code to your script:

```python
def main():
    """Main function for our first connection."""
    logger.info("=== My First InSim Connection ===")
    
    # Step 1: Define connection parameters
    HOST = "127.0.0.1"
    PORT = 29999
    APP_NAME = "MyFirstApp"
    ADMIN_PASSWORD = ""
    
    # Step 2: Create InSim client
    logger.info(f"Creating InSim client...")
    client = InSimClient(
        host=HOST,
        port=PORT,
        admin_password=ADMIN_PASSWORD,
        app_name=APP_NAME
    )
    
    logger.info(f"Client created for {HOST}:{PORT}")
    
    # We'll connect in the next step
```

**What happens here:**
- `InSimClient` is instantiated with connection parameters
- No actual connection is made yet
- Client is configured and ready to connect

### Step 4: Establishing Connection

Now let's actually connect:

```python
def main():
    """Main function for our first connection."""
    logger.info("=== My First InSim Connection ===")
    
    # Connection parameters
    HOST = "127.0.0.1"
    PORT = 29999
    APP_NAME = "MyFirstApp"
    ADMIN_PASSWORD = ""
    
    # Create client
    client = InSimClient(
        host=HOST,
        port=PORT,
        admin_password=ADMIN_PASSWORD,
        app_name=APP_NAME
    )
    
    try:
        # Step 3: Establish TCP connection
        logger.info(f"Connecting to {HOST}:{PORT}...")
        client.connect()
        logger.info("✓ Connection established!")
        
        # Step 4: Initialize InSim protocol
        logger.info("Initializing InSim...")
        client.initialize()
        logger.info("✓ InSim initialized!")
        
        # Step 5: Keep connection alive briefly
        logger.info("Connection active. Press Ctrl+C to exit.")
        time.sleep(10)
        
    except ConnectionError as e:
        logger.error(f"✗ Connection failed: {e}")
        logger.error("Make sure:")
        logger.error("  1. Live for Speed is running")
        logger.error("  2. InSim is enabled (Options → Misc)")
        logger.error("  3. Port is set to 29999")
        logger.error("  4. You are in an active driving session")
        sys.exit(1)
        
    finally:
        # Step 6: Clean up
        logger.info("Disconnecting...")
        client.disconnect()
        logger.info("✓ Disconnected")
```

**Run the script:**
```bash
python my_first_connection.py
```

**Expected output:**
```
INFO - === My First InSim Connection ===
INFO - Connecting to 127.0.0.1:29999...
INFO - ✓ Connection established!
INFO - Initializing InSim...
INFO - ✓ InSim initialized!
INFO - Connection active. Press Ctrl+C to exit.
INFO - Disconnecting...
INFO - ✓ Disconnected
```

**What each step does:**

1. **`connect()`** - Opens TCP socket to LFS
2. **`initialize()`** - Sends `IS_ISI` packet to start InSim
3. **`time.sleep(10)`** - Keeps connection alive
4. **`disconnect()`** - Closes socket cleanly

### Step 5: Handling Connection Events

Let's improve error handling and add connection event callbacks:

```python
def on_connect():
    """Called when connection is established."""
    logger.info("🔌 Connected to LFS!")

def on_disconnect():
    """Called when connection is lost."""
    logger.info("🔌 Disconnected from LFS")

def on_error(error):
    """Called when an error occurs."""
    logger.error(f"❌ Error: {error}")

def main():
    """Main function with event handling."""
    logger.info("=== InSim Connection with Events ===")
    
    # Create client
    client = InSimClient(
        host="127.0.0.1",
        port=29999,
        admin_password="",
        app_name="EventExample"
    )
    
    # Register event callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_error = on_error
    
    try:
        # Connect and initialize
        client.connect()
        client.initialize()
        
        # Stay connected
        logger.info("Connection active (10 seconds)...")
        time.sleep(10)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        client.disconnect()
```

### Step 6: Receiving Packets

Now let's receive and display packets from LFS:

```python
def main():
    """Main function that receives packets."""
    logger.info("=== Receiving InSim Packets ===")
    
    client = InSimClient(
        host="127.0.0.1",
        port=29999,
        admin_password="",
        app_name="PacketReader"
    )
    
    try:
        # Connect
        client.connect()
        client.initialize()
        logger.info("Connected! Receiving packets...")
        
        # Receive packets for 30 seconds
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < 30:
            # Receive one packet
            packet = client.receive_packet()
            
            if packet:
                packet_count += 1
                packet_type = packet.get('type', 'Unknown')
                logger.info(f"Packet #{packet_count}: {packet_type}")
                
                # Show packet details (optional)
                if logger.level <= 10:  # DEBUG level
                    logger.debug(f"  Data: {packet}")
            
            # Small delay to avoid busy loop
            time.sleep(0.01)
        
        logger.info(f"✓ Received {packet_count} packets")
        
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
    finally:
        client.disconnect()
```

**What you should see:**
```
INFO - Connected! Receiving packets...
INFO - Packet #1: IS_VER
INFO - Packet #2: IS_ISM
INFO - Packet #3: IS_MCI
INFO - Packet #4: IS_MCI
...
INFO - ✓ Received 234 packets
```

**Common packet types:**
- `IS_VER` - LFS version info
- `IS_ISM` - InSim Multi
- `IS_MCI` - Multi Car Info (telemetry)
- `IS_NLP` - Node and Lap
- `IS_MSO` - Message/chat

### Step 7: Simple Data Collection

Let's collect basic telemetry data:

```python
from src.telemetry import TelemetryCollector

def on_telemetry_data(data):
    """Callback when telemetry data is received."""
    if data:
        speed = data.get('speed', 0)
        rpm = data.get('rpm', 0)
        gear = data.get('gear', 0)
        
        logger.info(f"Speed: {speed:.1f} km/h | RPM: {rpm} | Gear: {gear}")

def main():
    """Main function with telemetry collection."""
    logger.info("=== Simple Telemetry Collection ===")
    
    # Create and connect client
    client = InSimClient(
        host="127.0.0.1",
        port=29999,
        admin_password="",
        app_name="TelemetryBasic"
    )
    
    try:
        client.connect()
        client.initialize()
        logger.info("Connected!")
        
        # Create telemetry collector
        collector = TelemetryCollector(client)
        
        # Register callback for telemetry data
        collector.register_callback("telemetry", on_telemetry_data)
        
        # Start collecting
        logger.info("Starting telemetry collection...")
        collector.start()
        
        # Collect for 60 seconds
        logger.info("Collecting data. Drive your car!")
        time.sleep(60)
        
        # Stop collector
        collector.stop()
        logger.info("Collection stopped")
        
        # Get collected data
        history = collector.get_telemetry_history()
        logger.info(f"✓ Collected {len(history)} data points")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.disconnect()
```

**Expected output:**
```
INFO - Starting telemetry collection...
INFO - Collecting data. Drive your car!
INFO - Speed: 0.0 km/h | RPM: 800 | Gear: 0
INFO - Speed: 45.2 km/h | RPM: 3200 | Gear: 2
INFO - Speed: 78.5 km/h | RPM: 5100 | Gear: 3
INFO - Speed: 112.3 km/h | RPM: 6800 | Gear: 4
...
INFO - ✓ Collected 612 data points
```

### Step 8: Error Handling Patterns

Professional error handling for production use:

```python
import sys
from typing import Optional

def connect_with_retry(
    client: InSimClient,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> bool:
    """
    Connect with automatic retry.
    
    Args:
        client: InSim client to connect
        max_retries: Maximum connection attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        True if connected, False otherwise
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connection attempt {attempt}/{max_retries}...")
            client.connect()
            client.initialize()
            logger.info("✓ Connected successfully!")
            return True
            
        except ConnectionError as e:
            logger.warning(f"✗ Attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("✗ All connection attempts failed")
                return False
    
    return False

def main():
    """Main function with robust error handling."""
    logger.info("=== Robust Connection Example ===")
    
    # Create client
    client = InSimClient(
        host="127.0.0.1",
        port=29999,
        admin_password="",
        app_name="RobustApp"
    )
    
    # Try to connect with retries
    if not connect_with_retry(client, max_retries=3, retry_delay=2.0):
        logger.error("Could not establish connection")
        sys.exit(1)
    
    try:
        # Main application logic
        logger.info("Running application...")
        
        # Keep running until interrupted
        while True:
            try:
                packet = client.receive_packet()
                # Process packet...
                time.sleep(0.01)
                
            except ConnectionError:
                logger.warning("Connection lost, attempting to reconnect...")
                if not connect_with_retry(client):
                    logger.error("Reconnection failed")
                    break
    
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    
    finally:
        try:
            client.disconnect()
        except:
            pass  # Already disconnected
        
        logger.info("✓ Application closed")
```

## Best Practices

### Connection Management

1. **Always use try-finally** for cleanup:
   ```python
   try:
       client.connect()
       # ... work ...
   finally:
       client.disconnect()
   ```

2. **Implement reconnection logic** for production:
   ```python
   def auto_reconnect():
       while True:
           try:
               client.connect()
               return
           except ConnectionError:
               time.sleep(5)
   ```

3. **Handle Ctrl+C gracefully:**
   ```python
   try:
       # ... main loop ...
   except KeyboardInterrupt:
       logger.info("Interrupted by user")
   ```

### Error Handling

1. **Specific exception catching:**
   ```python
   try:
       client.connect()
   except ConnectionRefusedError:
       logger.error("LFS not running or InSim disabled")
   except TimeoutError:
       logger.error("Connection timeout")
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
   ```

2. **Log errors with context:**
   ```python
   logger.error(f"Failed to connect to {host}:{port}")
   logger.error(f"Error: {e}", exc_info=True)  # Include traceback
   ```

### Performance

1. **Don't block the main thread:**
   ```python
   # Bad
   while True:
       heavy_processing()  # Blocks everything
   
   # Good
   collector.register_callback("telemetry", process_async)
   ```

2. **Limit data retention:**
   ```python
   collector = TelemetryCollector(
       client,
       max_history=1000  # Prevent memory issues
   )
   ```

## Common Issues

### "Connection refused"
- LFS not running → Start LFS
- InSim not enabled → Options → Misc → Enable InSim
- Wrong port → Check LFS InSim port setting
- Not in session → Start driving (not in menu)

### No telemetry data
- Car not moving → Drive the car
- Wrong interval → Check config.yaml telemetry.interval > 0
- Collector not started → Call `collector.start()`

### High memory usage
- Too much history → Reduce `max_history`
- Not clearing old data → Call `collector.clear_history()`

See [Troubleshooting Guide](troubleshooting.md) for more solutions.

## Complete Example

Here's a complete, production-ready example:

```python
"""
Complete beginner example with all best practices.
"""

import sys
import time
import signal
from src.connection import InSimClient
from src.telemetry import TelemetryCollector
from src.utils import setup_logger

# Global flag for clean shutdown
running = True

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global running
    logger.info("Shutdown requested...")
    running = False

def main():
    """Complete application with error handling."""
    global running
    
    # Setup
    logger = setup_logger("complete_example", level="INFO")
    logger.info("=== Complete Beginner Example ===")
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create client
    client = InSimClient(
        host="127.0.0.1",
        port=29999,
        admin_password="",
        app_name="CompleteApp"
    )
    
    collector = None
    
    try:
        # Connect
        logger.info("Connecting...")
        client.connect()
        client.initialize()
        logger.info("✓ Connected")
        
        # Setup collector
        collector = TelemetryCollector(client, max_history=1000)
        collector.register_callback(
            "telemetry",
            lambda data: logger.info(f"Speed: {data.get('speed', 0):.1f} km/h")
        )
        collector.start()
        logger.info("✓ Collector started")
        
        # Main loop
        logger.info("Running... Press Ctrl+C to stop")
        while running:
            time.sleep(0.1)
        
        # Get results
        history = collector.get_telemetry_history()
        logger.info(f"✓ Collected {len(history)} data points")
        
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.error("Check that LFS is running with InSim enabled")
        return 1
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    
    finally:
        # Cleanup
        if collector:
            collector.stop()
        
        client.disconnect()
        logger.info("✓ Application closed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Next Steps

Congratulations! You've learned the basics of InSim and LFS-Ayats. 

### Continue Learning

1. **Intermediate Tutorial** - [tutorial-intermediate.md](tutorial-intermediate.md)
   - Advanced packet processing
   - Real-time data streaming
   - Performance optimization

2. **Practical Tutorials**
   - [First Session](tutorials/01-first-session.md) - Complete session recording
   - [Lap Analysis](tutorials/02-lap-analysis.md) - Compare lap times
   - [Dashboard](tutorials/03-real-time-dashboard.md) - Web visualization

3. **Advanced Topics**
   - [Architecture](architecture.md) - System design
   - [API Reference](api_reference.md) - Full API documentation
   - [Development Guide](development.md) - Contributing

### Practice Exercises

1. Modify the script to collect data for specific time duration
2. Add filtering to show only speeds above 100 km/h
3. Export collected data to CSV file
4. Create callback that detects fastest lap
5. Implement automatic reconnection on disconnect

### Resources

- **Official InSim Docs:** [InSim.txt](https://en.lfsmanual.net/wiki/InSim.txt)
- **LFS Manual:** [LFS Manual](https://en.lfsmanual.net/)
- **Example Scripts:** [examples/](../examples/)
- **FAQ:** [faq.md](faq.md)

---

**You're now ready to build your own telemetry applications!** 🎉

Happy coding! 🏎️💨
