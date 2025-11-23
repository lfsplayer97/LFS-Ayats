# Tutorial 5: Database Integration

This tutorial will teach you how to store telemetry sessions in a database for historical queries and long-term analysis.

## Learning Objectives

By the end of this tutorial, you will know how to:

- ✅ Configure PostgreSQL or SQLite databases
- ✅ Store sessions and telemetry data persistently
- ✅ Query historical data efficiently
- ✅ Optimize query performance with indexes
- ✅ Export and import data from/to databases

## Prerequisites

- Previous tutorials completed (Tutorials 1-4)
- SQLite (included with Python) or PostgreSQL installed
- Understanding of SQL basics (helpful but not required)

## Estimated Time

45 minutes

## Step 1: Database Setup

Create a new script `database_integration.py`:

```python
"""
Database Integration
Persistent storage for telemetry data.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict
import json

from src.database.repository import TelemetryRepository
from src.database.models import Base
from src.utils import setup_logger

logger = setup_logger("db_integration", "INFO")
```

### Option A: SQLite (Recommended for Getting Started)

SQLite is perfect for local development and doesn't require any server setup:

```python
def setup_sqlite_database(db_path: str = "data/telemetry.db") -> TelemetryRepository:
    """
    Configure SQLite database.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        TelemetryRepository: Configured repository instance
    """
    logger.info(f"Setting up SQLite: {db_path}")
    
    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create repository
    repository = TelemetryRepository(
        connection_string=f'sqlite:///{db_path}',
        echo=False  # Set to True for SQL query logging
    )
    
    # Create tables
    repository.create_tables()
    
    logger.info("✓ Database initialized")
    logger.info(f"✓ Tables created at: {db_path}")
    
    return repository
```

### Option B: PostgreSQL (For Production)

PostgreSQL is recommended for production deployments with multiple users:

```python
def setup_postgresql_database(
    host: str = "localhost",
    port: int = 5432,
    database: str = "lfs_telemetry",
    user: str = "lfs_user",
    password: str = "password"
) -> TelemetryRepository:
    """
    Configure PostgreSQL database.
    
    Args:
        host: PostgreSQL server host
        port: Server port (default 5432)
        database: Database name
        user: Username
        password: User password
        
    Returns:
        TelemetryRepository: Configured repository instance
    """
    logger.info(f"Connecting to PostgreSQL: {host}:{port}/{database}")
    
    # Build connection string
    conn_string = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    
    # Create repository
    repository = TelemetryRepository(
        connection_string=conn_string,
        echo=False,
        pool_size=5  # Connection pool size
    )
    
    # Create tables
    repository.create_tables()
    
    logger.info("✓ Connected to PostgreSQL")
    logger.info("✓ Tables created/verified")
    
    return repository
```

## Step 2: Understanding the Database Schema

The database schema is already defined in `src/database/models.py`. Here's an overview:

### Database Tables

**1. Sessions Table**
- Stores metadata about each driving session
- Fields: id, datetime, circuit_id, vehicle_id, driver_name, duration, total_laps

**2. Laps Table**  
- Stores timing information for each lap
- Fields: id, session_id, lap_number, lap_time, sector1_time, sector2_time, sector3_time, valid

**3. TelemetryPoint Table**
- Stores high-frequency telemetry data points
- Fields: id, lap_id, timestamp, speed, rpm, gear, throttle, brake, clutch, steering_angle, position_x/y/z, engine_temp

**4. Circuits & Vehicles Tables**
- Store circuit and vehicle information for referential integrity

### Key Relationships

```python
# Example of the database structure:

Session (1) --- (N) Laps (1) --- (N) TelemetryPoints
   |                                     |
   |--- (N) Circuit                     Includes:
   |--- (N) Vehicle                     - Speed, RPM
                                        - Position data
                                        - Controls (throttle, brake)
```

The repository handles all these relationships automatically.

## Step 3: Saving Sessions to Database

```python
def load_session_data(filepath: str) -> List[Dict]:
    """
    Load session data from JSON file.
    
    Args:
        filepath: Path to JSON file from Tutorial 1
        
    Returns:
        List of telemetry data points
    """
    logger.info(f"Loading session data: {filepath}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    logger.info(f"✓ Loaded {len(data)} telemetry points")
    return data


def extract_laps(telemetry_data: List[Dict]) -> List[List[Dict]]:
    """
    Separate telemetry data into individual laps.
    
    Args:
        telemetry_data: Complete telemetry data
        
    Returns:
        List of laps, where each lap is a list of data points
    """
    logger.info("Extracting individual laps...")
    
    laps = []
    current_lap = []
    last_lap_number = -1
    
    for sample in telemetry_data:
        lap_number = sample.get('lap', 0)
        
        if lap_number != last_lap_number and current_lap:
            # New lap detected, save previous one
            laps.append(current_lap)
            current_lap = []
        
        current_lap.append(sample)
        last_lap_number = lap_number
    
    # Add last lap
    if current_lap:
        laps.append(current_lap)
    
    logger.info(f"✓ Found {len(laps)} laps")
    return laps


def save_session_to_database(
    repository: TelemetryRepository,
    telemetry_data: List[Dict],
    circuit_name: str = "Blackwood GP",
    vehicle_name: str = "XF GTI",
    driver_name: str = "Driver"
) -> int:
    """
    Save a complete session to the database.
    
    Args:
        repository: TelemetryRepository instance
        telemetry_data: Telemetry data from collection
        circuit_name: Name of the circuit (short name like "BL1")
        vehicle_name: Name of the vehicle (short name like "XFG")
        driver_name: Name of the driver
        
    Returns:
        Session ID
    """
    logger.info("Saving session to database...")
    
    # Separate into laps
    laps = extract_laps(telemetry_data)
    
    # First, ensure circuit and vehicle exist
    repository.get_or_create_circuit(
        name=circuit_name,
        short_name="BL1",  # Use appropriate short code
        length=2000.0  # Circuit length in meters
    )
    repository.get_or_create_vehicle(
        name=vehicle_name,
        short_name="XFG",  # Use appropriate short code
        class_type="TBO"
    )
    
    # Create session (without laps)
    session_id = repository.save_session(
        datetime_start=datetime.now(),
        circuit_name="BL1",  # Use short name
        vehicle_name="XFG",  # Use short name
        driver_name=driver_name,
        duration=None  # Will calculate later if needed
    )
    
    logger.info(f"✓ Session created: ID {session_id}")
    
    # Process each lap
    for lap_idx, lap_data in enumerate(laps):
        # Calculate lap time (in milliseconds)
        if lap_data:
            first_time = lap_data[0].get('timestamp', 0)
            last_time = lap_data[-1].get('timestamp', 0)
            lap_time = int((last_time - first_time) * 1000)  # Convert to ms
        else:
            lap_time = 0
        
        # Save lap
        lap_id = repository.save_lap(
            session_id=session_id,
            lap_number=lap_idx + 1,
            lap_time=lap_time,
            valid=True
        )
        
        # Prepare telemetry points for batch insert
        telemetry_points = []
        for point in lap_data:
            telemetry_point = {
                'timestamp': int(point.get('timestamp', 0) * 1000),  # ms
                'speed': float(point.get('speed', 0)),
                'rpm': int(point.get('rpm', 0)),
                'gear': int(point.get('gear', 0)),
                'throttle': float(point.get('throttle', 0)),
                'brake': float(point.get('brake', 0)),
                'position_x': float(point.get('pos_x', 0)),
                'position_y': float(point.get('pos_y', 0)),
                'position_z': float(point.get('pos_z', 0))
            }
            telemetry_points.append(telemetry_point)
        
        # Save telemetry points in batch
        count = repository.save_telemetry_points(lap_id, telemetry_points)
        logger.info(f"  Lap {lap_idx + 1}: {count} points saved")
    
    logger.info(f"✓ Session saved: ID {session_id}, {len(laps)} laps")
    
    return session_id
```

## Step 4: Querying Historical Data

```python
import numpy as np


def query_best_laps(repository: TelemetryRepository, circuit_name: str = None, limit: int = 10):
    """
    Query the best laps from the database across all sessions.
    
    Args:
        repository: TelemetryRepository instance
        circuit_name: Filter by circuit (optional)
        limit: Maximum number of results
        
    Returns:
        List of best laps
    """
    logger.info("Querying best laps...")
    
    # Get all sessions (filtered by circuit if specified)
    sessions = repository.get_sessions(circuit=circuit_name, limit=100)
    
    # Collect best lap from each session
    all_best_laps = []
    for session in sessions:
        best_lap = repository.get_best_lap(session.id)
        if best_lap:
            all_best_laps.append((best_lap, session))
    
    # Sort by lap time and limit
    all_best_laps.sort(key=lambda x: x[0].lap_time if x[0].lap_time else float('inf'))
    best_laps = all_best_laps[:limit]
    
    logger.info(f"\n🏆 Top {len(best_laps)} Best Laps:")
    for idx, (lap, session) in enumerate(best_laps, 1):
        lap_time_seconds = lap.lap_time / 1000.0  # Convert ms to seconds
        circuit = session.circuit.name if session.circuit else "Unknown"
        driver = session.driver_name or "Unknown"
        
        logger.info(f"{idx}. Lap {lap.lap_number} - "
                   f"Time: {lap_time_seconds:.3f}s - "
                   f"Circuit: {circuit} - "
                   f"Driver: {driver}")
    
    return [lap for lap, _ in best_laps]


def query_session_statistics(repository: TelemetryRepository, session_id: int):
    """
    Get statistics for a specific session.
    
    Args:
        repository: TelemetryRepository instance
        session_id: Session ID
    """
    logger.info(f"Querying session {session_id} statistics...")
    
    # Get session (relationships are eagerly loaded)
    session = repository.get_session(session_id)
    
    if not session:
        logger.error(f"Session {session_id} not found")
        return
    
    circuit = session.circuit.name if session.circuit else "Unknown"
    vehicle = session.vehicle.name if session.vehicle else "Unknown"
    driver = session.driver_name or "Unknown"
    
    logger.info(f"\n📊 Session #{session.id}")
    logger.info(f"   Circuit: {circuit}")
    logger.info(f"   Vehicle: {vehicle}")
    logger.info(f"   Driver: {driver}")
    logger.info(f"   Date/Time: {session.datetime}")
    logger.info(f"   Total Laps: {len(session.laps)}")
    
    if session.laps:
        lap_times = [lap.lap_time / 1000.0 for lap in session.laps if lap.lap_time]  # Convert to seconds
        
        if lap_times:
            logger.info(f"   Best Lap: {min(lap_times):.3f}s")
            logger.info(f"   Worst Lap: {max(lap_times):.3f}s")
            logger.info(f"   Average: {np.mean(lap_times):.3f}s")
            logger.info(f"   Std Dev: {np.std(lap_times):.3f}s")
    
    return session


def compare_sessions(repository: TelemetryRepository, session_id1: int, session_id2: int):
    """
    Compare two sessions.
    
    Args:
        repository: TelemetryRepository instance
        session_id1: First session ID
        session_id2: Second session ID
    """
    logger.info(f"\n=== Comparing Sessions {session_id1} vs {session_id2} ===")
    
    # Get both sessions
    s1 = repository.get_session(session_id1)
    s2 = repository.get_session(session_id2)
    
    if not s1 or not s2:
        logger.error("One or both sessions do not exist")
        return
    
    # Get best laps using repository method
    best_lap1 = repository.get_best_lap(session_id1)
    best_lap2 = repository.get_best_lap(session_id2)
    
    if best_lap1 and best_lap2:
        time1 = best_lap1.lap_time / 1000.0
        time2 = best_lap2.lap_time / 1000.0
        diff = time2 - time1
        
        logger.info(f"\n⏱️  Best Laps Comparison:")
        logger.info(f"   Session {session_id1}: {time1:.3f}s")
        logger.info(f"   Session {session_id2}: {time2:.3f}s")
        logger.info(f"   Difference: {abs(diff):.3f}s")
        
        if diff < 0:
            logger.info(f"   ✓ Session {session_id1} was faster by {abs(diff):.3f}s")
        elif diff > 0:
            logger.info(f"   ✓ Session {session_id2} was faster by {abs(diff):.3f}s")
        else:
            logger.info(f"   = Same lap time!")
    
    # Compare session stats
    logger.info(f"\n📊 Session Statistics:")
    logger.info(f"   Session {session_id1}: {len(s1.laps)} laps")
    logger.info(f"   Session {session_id2}: {len(s2.laps)} laps")
    
    return s1, s2


def list_all_sessions(repository: TelemetryRepository):
    """
    List all sessions in the database.
    
    Args:
        repository: TelemetryRepository instance
    """
    logger.info("\n📋 All Sessions:")
    
    # Get all sessions (limit can be increased if needed)
    sessions = repository.get_sessions(limit=100)
    
    if not sessions:
        logger.info("   No sessions found in database")
        return []
    
    for session in sessions:
        circuit = session.circuit.name if session.circuit else "Unknown"
        driver = session.driver_name or "Unknown"
        
        logger.info(f"   ID {session.id}: {circuit} - {driver} - "
                   f"{session.datetime.strftime('%Y-%m-%d %H:%M')} - "
                   f"{session.total_laps} laps")
    
    return sessions
```

## Step 5: Performance Optimization

### Database Indexes

The database models already include optimized indexes for common queries:

```python
# Indexes are defined in src/database/models.py:

# Session indexes (for filtering by circuit and date)
Index('idx_sessions_circuit', Session.circuit_id)
Index('idx_sessions_datetime', Session.datetime)

# Lap indexes (for finding by session)
Index('idx_laps_session', Lap.session_id)

# Telemetry indexes (for lap queries)
Index('idx_telemetry_lap', TelemetryPoint.lap_id)
```

These indexes significantly improve query performance when:
- Searching for sessions by circuit
- Querying sessions by date range
- Loading laps for a specific session
- Retrieving telemetry points for a lap

### Batch Operations

For large datasets, use batch operations to improve performance:

```python
def batch_save_sessions(repository: TelemetryRepository, session_files: List[str]):
    """
    Save multiple sessions efficiently.
    
    Args:
        repository: TelemetryRepository instance
        session_files: List of JSON files to import
    """
    logger.info(f"Batch saving {len(session_files)} sessions...")
    
    for idx, filepath in enumerate(session_files, 1):
        logger.info(f"\n[{idx}/{len(session_files)}] Processing {filepath}")
        
        # Load data
        telemetry_data = load_session_data(filepath)
        
        # Extract metadata from filename or data
        # Format: session_YYYYMMDD_HHMMSS.json
        filename = Path(filepath).stem
        
        # Save to database
        session_id = save_session_to_database(
            repository,
            telemetry_data,
            circuit_name="Blackwood GP",
            vehicle_name="XF GTI",
            driver_name="Driver"
        )
        
        logger.info(f"  ✓ Saved as session ID: {session_id}")
    
    logger.info(f"\n✓ Batch save complete: {len(session_files)} sessions")
```

### Query Optimization Tips

1. **Use specific filters**: Always filter by circuit or date when possible
2. **Limit results**: Use the `limit` parameter for large result sets
3. **Lazy loading**: Only load related data when needed
4. **Bulk operations**: Use batch inserts for large amounts of data

## Step 6: Data Export and Import

### Exporting Session Data

```python
def export_session_to_json(repository: TelemetryRepository, session_id: int, 
                          output_file: str):
    """
    Export a session to JSON format.
    
    Args:
        repository: TelemetryRepository instance
        session_id: Session ID to export
        output_file: Output file path
    """
    logger.info(f"Exporting session {session_id} to {output_file}...")
    
    # Get session
    session = repository.get_session(session_id)
    
    if not session:
        logger.error(f"Session {session_id} not found")
        return
    
    # Build export data structure
    data = {
        'session_id': session.id,
        'datetime': session.datetime.isoformat(),
        'circuit': session.circuit.name if session.circuit else "Unknown",
        'vehicle': session.vehicle.name if session.vehicle else "Unknown",
        'driver': session.driver_name or "Unknown",
        'total_laps': len(session.laps),
        'laps': []
    }
    
    # Export each lap
    for lap in session.laps:
        lap_data = {
            'lap_number': lap.lap_number,
            'lap_time': lap.lap_time,
            'sector1_time': lap.sector1_time,
            'sector2_time': lap.sector2_time,
            'sector3_time': lap.sector3_time,
            'valid': lap.valid,
            'telemetry_points': []
        }
        
        # Get telemetry points for this lap
        telemetry_points = repository.get_telemetry_points(lap.id)
        
        for point in telemetry_points:
            telemetry_point = {
                'timestamp': point.timestamp,
                'speed': point.speed,
                'rpm': point.rpm,
                'gear': point.gear,
                'throttle': point.throttle,
                'brake': point.brake,
                'position_x': point.position_x,
                'position_y': point.position_y,
                'position_z': point.position_z
            }
            lap_data['telemetry_points'].append(telemetry_point)
        
        data['laps'].append(lap_data)
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✓ Session exported: {output_file}")
    logger.info(f"  {len(data['laps'])} laps exported")


def export_all_sessions(repository: TelemetryRepository, output_dir: str = "exports"):
    """
    Export all sessions to individual JSON files.
    
    Args:
        repository: TelemetryRepository instance
        output_dir: Directory for export files
    """
    logger.info("Exporting all sessions...")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get all sessions
    sessions = repository.get_sessions(limit=1000)
    
    for session in sessions:
        # Generate filename
        filename = f"session_{session.id}_{session.datetime.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(output_dir) / filename
        
        # Export
        export_session_to_json(repository, session.id, str(filepath))
    
    logger.info(f"✓ Exported {len(sessions)} sessions to {output_dir}/")
```

### Importing Session Data

```python
def import_session_from_json(repository: TelemetryRepository, json_file: str) -> int:
    """
    Import a session from JSON format.
    
    Args:
        repository: TelemetryRepository instance
        json_file: Path to JSON file
        
    Returns:
        New session ID
    """
    logger.info(f"Importing session from {json_file}...")
    
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create session
    session_id = repository.save_session(
        datetime_start=datetime.fromisoformat(data['datetime']) if 'datetime' in data else datetime.now(),
        circuit_name=data.get('circuit', 'Unknown'),
        vehicle_name=data.get('vehicle', 'Unknown'),
        driver_name=data.get('driver', 'Unknown'),
        duration=None
    )
    
    # Import laps
    laps_data = data.get('laps', [])
    for lap_data in laps_data:
        # Save lap
        lap_id = repository.save_lap(
            session_id=session_id,
            lap_number=lap_data['lap_number'],
            lap_time=lap_data.get('lap_time'),
            sector1_time=lap_data.get('sector1_time'),
            sector2_time=lap_data.get('sector2_time'),
            sector3_time=lap_data.get('sector3_time'),
            valid=lap_data.get('valid', True)
        )
        
        # Import telemetry points
        telemetry_points = lap_data.get('telemetry_points', [])
        if telemetry_points:
            repository.save_telemetry_points(lap_id, telemetry_points)
    
    logger.info(f"✓ Session imported: ID {session_id}")
    logger.info(f"  {len(laps_data)} laps imported")
    
    return session_id
```

## Step 7: Complete Example

Here's a complete script that demonstrates all the concepts:

```python
def main():
    """
    Main function demonstrating database integration.
    """
    logger.info("=== Database Integration Tutorial ===\n")
    
    # Step 1: Setup database
    logger.info("Step 1: Setting up database...")
    repository = setup_sqlite_database("data/telemetry.db")
    
    # Step 2: Load sample data (from Tutorial 1)
    logger.info("\nStep 2: Loading sample data...")
    
    # Check if we have session files
    data_dir = Path("data")
    session_files = list(data_dir.glob("session_*.json"))
    
    if not session_files:
        logger.warning("No session files found in data/ directory")
        logger.info("Please run Tutorial 1 first to collect telemetry data")
        return
    
    # Use the first session file
    sample_file = session_files[0]
    telemetry_data = load_session_data(str(sample_file))
    
    # Step 3: Save to database
    logger.info("\nStep 3: Saving session to database...")
    session_id = save_session_to_database(
        repository,
        telemetry_data,
        circuit_name="Blackwood GP",
        vehicle_name="XF GTI",
        driver_name="YourName"
    )
    
    # Step 4: Query data
    logger.info("\nStep 4: Querying historical data...")
    
    # List all sessions
    list_all_sessions(repository)
    
    # Get best laps
    query_best_laps(repository, limit=5)
    
    # Get session statistics
    query_session_statistics(repository, session_id)
    
    # Step 5: Export data
    logger.info("\nStep 5: Exporting data...")
    export_session_to_json(repository, session_id, "data/session_export.json")
    
    # Step 6: Compare sessions (if we have multiple)
    if len(session_files) > 1:
        logger.info("\nStep 6: Loading and comparing second session...")
        
        # Load second session
        telemetry_data2 = load_session_data(str(session_files[1]))
        session_id2 = save_session_to_database(
            repository,
            telemetry_data2,
            circuit_name="Blackwood GP",
            vehicle_name="XF GTI",
            driver_name="YourName"
        )
        
        # Compare
        compare_sessions(repository, session_id, session_id2)
    
    logger.info("\n✓ Tutorial completed successfully!")
    logger.info(f"   Database location: data/telemetry.db")
    logger.info(f"   Total sessions: {len(list_all_sessions(repository))}")
    logger.info(f"   Use a SQLite browser to explore the data!")


if __name__ == "__main__":
    main()
```

## Step 8: Running the Tutorial

Save the script and run it:

```bash
cd LFS-Ayats
python database_integration.py
```

Expected output:
```
=== Database Integration Tutorial ===

Step 1: Setting up database...
INFO - Setting up SQLite: data/telemetry.db
INFO - ✓ Database initialized
INFO - ✓ Tables created at: data/telemetry.db

Step 2: Loading sample data...
INFO - Loading session data: data/session_20240115_143022.json
INFO - ✓ Loaded 2543 telemetry points

Step 3: Saving session to database...
INFO - Saving session to database...
INFO - Extracting individual laps...
INFO - ✓ Found 5 laps
INFO -   Lap 1: 512 points prepared
INFO -   Lap 2: 498 points prepared
...
INFO - ✓ Session saved: ID 1, 5 laps

Step 4: Querying historical data...
INFO - 📋 All Sessions:
INFO -    ID 1: Blackwood GP - YourName - 2024-01-15 14:30 - 5 laps

INFO - 🏆 Top 5 Best Laps:
INFO - 1. Lap 3 - Time: 93.542s - Circuit: Blackwood GP - Driver: YourName
...

✓ Tutorial completed successfully!
```

## Production Deployment Tips

### 1. PostgreSQL Setup

For production environments, PostgreSQL is recommended:

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE lfs_telemetry;
CREATE USER lfs_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE lfs_telemetry TO lfs_user;
\q
```

Then update your script to use PostgreSQL:

```python
repository = setup_postgresql_database(
    host="localhost",
    port=5432,
    database="lfs_telemetry",
    user="lfs_user",
    password="secure_password_here"
)
```

### 2. Database Migrations with Alembic

The repository includes Alembic for database migrations:

```bash
# Initialize Alembic (already done in this repo)
alembic init alembic

# Generate a new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### 3. Regular Backups

**SQLite Backups:**
```bash
# Simple file copy
cp data/telemetry.db data/backups/telemetry_$(date +%Y%m%d_%H%M%S).db

# Compressed backup
tar -czf telemetry_backup_$(date +%Y%m%d).tar.gz data/telemetry.db
```

**PostgreSQL Backups:**
```bash
# Full database dump
pg_dump lfs_telemetry > backup_$(date +%Y%m%d).sql

# Compressed dump
pg_dump lfs_telemetry | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore from backup
psql lfs_telemetry < backup_20240115.sql
```

### 4. Connection Pooling

For multi-user applications, configure connection pooling:

```python
repository = TelemetryRepository(
    connection_string="postgresql://user:pass@localhost/lfs_telemetry",
    pool_size=10,      # Number of connections in pool
    echo=False         # Disable SQL logging in production
)
```

### 5. Environment Variables

Store credentials securely using environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

repository = TelemetryRepository(
    connection_string=os.getenv("DATABASE_URL"),
    echo=os.getenv("DEBUG", "False") == "True"
)
```

## Advanced Exercises

Try these exercises to deepen your understanding:

### Exercise 1: Temporal Analysis
Create queries to track your improvement over time:

```python
def analyze_improvement_over_time(repository: TelemetryRepository, 
                                 circuit_name: str,
                                 driver_name: str):
    """
    Analyze lap time improvement over multiple sessions.
    Track progress and identify trends.
    """
    # TODO: Implement this function
    # Hint: Query sessions ordered by date, extract best lap from each
    pass
```

### Exercise 2: Global Rankings
Implement a global ranking system:

```python
def generate_global_rankings(repository: TelemetryRepository,
                            circuit_name: str = None):
    """
    Generate rankings across all drivers for a circuit.
    Include statistics like best lap, average lap, consistency.
    """
    # TODO: Implement this function
    # Hint: Use aggregation queries (GROUP BY driver)
    pass
```

### Exercise 3: Telemetry Heatmaps
Create a function to analyze telemetry data spatially:

```python
def generate_speed_heatmap(repository: TelemetryRepository,
                          lap_id: int):
    """
    Generate a heatmap of speeds across the circuit.
    Useful for identifying braking and acceleration zones.
    """
    # TODO: Implement this function
    # Hint: Load telemetry points, group by position, calculate avg speed
    pass
```

### Exercise 4: Data Archiving
Implement an archiving system for old sessions:

```python
def archive_old_sessions(repository: TelemetryRepository,
                        days_old: int = 90):
    """
    Archive sessions older than specified days.
    Export to JSON and optionally delete from active database.
    """
    # TODO: Implement this function
    # Hint: Query sessions by date, export, then delete if needed
    pass
```

## Troubleshooting

### Common Issues

**1. Database Locked (SQLite)**
```
sqlite3.OperationalError: database is locked
```
Solution: Close all connections properly, or use PostgreSQL for concurrent access.

**2. Connection Pool Exhausted**
```
sqlalchemy.exc.TimeoutError: QueuePool limit exceeded
```
Solution: Increase pool_size or ensure connections are closed after use.

**3. Migration Conflicts**
```
alembic.util.exc.CommandError: Target database is not up to date
```
Solution: Run `alembic upgrade head` to apply pending migrations.

**4. Large Dataset Performance**
If queries are slow with large datasets:
- Add more indexes for your specific queries
- Use pagination for large result sets
- Consider partitioning tables by date
- Use PostgreSQL for better performance with large data

## Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/) - ORM and database toolkit
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) - Database migrations
- [PostgreSQL Guide](https://www.postgresql.org/docs/) - PostgreSQL documentation
- [SQLite Documentation](https://www.sqlite.org/docs.html) - SQLite reference
- [Database Design Best Practices](https://www.postgresql.org/docs/current/ddl.html) - Schema design

## Next Steps

Congratulations! You've learned how to:
- ✅ Set up SQLite and PostgreSQL databases
- ✅ Store telemetry sessions persistently
- ✅ Query and analyze historical data
- ✅ Optimize database performance
- ✅ Export and import data

### What's Next?

- **Combine with Tutorial 3**: Create a dashboard that displays historical data from the database
- **Combine with Tutorial 4**: Use database queries for advanced statistical analysis
- **Build a web API**: Expose database queries through a REST API (see `src/api/`)
- **Implement real-time storage**: Modify Tutorial 1 to save data directly to database while collecting

---

🎉 You can now store and query historical telemetry data! Continue exploring the visualization and API modules to build a complete telemetry analysis system.
