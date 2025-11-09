"""
Database Usage Example

This example demonstrates how to use the database system to store and
query telemetry data from Live for Speed racing sessions.

Run this example:
    python examples/database_example.py
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.export.db_exporter import DatabaseExporter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_basic_usage():
    """Basic usage: Create session and export telemetry"""
    logger.info("=== Basic Usage Example ===")
    
    # Create exporter (SQLite database in data directory)
    exporter = DatabaseExporter("sqlite:///data/telemetry.db")
    
    try:
        # Export a session
        session_data = {
            "datetime": datetime.now(),
            "driver_name": "Player1",
            "duration": 600
        }
        
        session_id = exporter.export_session(session_data)
        logger.info(f"Session created with ID: {session_id}")
        
        # Get session statistics
        stats = exporter.get_session_statistics(session_id)
        logger.info(f"Session statistics: {stats}")
        
    finally:
        exporter.close()


def example_with_circuits_and_vehicles():
    """Setup circuits and vehicles, then create session"""
    logger.info("=== Circuits and Vehicles Example ===")
    
    exporter = DatabaseExporter("sqlite:///data/telemetry.db")
    
    try:
        # Setup circuits
        circuits = [
            {"name": "Blackwood GP", "short_name": "BL1", "length": 3290.0},
            {"name": "Kyoto Ring Oval", "short_name": "KY1", "length": 3304.0},
        ]
        
        # Setup vehicles
        vehicles = [
            {"name": "XF GTI", "short_name": "XFG", "class_type": "TBO"},
            {"name": "XR GT", "short_name": "XRG", "class_type": "TBO"},
        ]
        
        exporter.setup_circuits_and_vehicles(circuits, vehicles)
        logger.info("Circuits and vehicles setup completed")
        
        # Create session with circuit and vehicle
        session_data = {
            "datetime": datetime.now(),
            "circuit_name": "BL1",
            "vehicle_name": "XFG",
            "driver_name": "Player1",
            "duration": 600
        }
        
        session_id = exporter.export_session(session_data)
        logger.info(f"Session created: {session_id}")
        
    finally:
        exporter.close()


def example_with_laps():
    """Export session with lap timing data"""
    logger.info("=== Laps Example ===")
    
    exporter = DatabaseExporter("sqlite:///data/telemetry.db")
    
    try:
        session_data = {
            "datetime": datetime.now(),
            "driver_name": "Player1",
            "duration": 300
        }
        
        # Lap data
        laps_data = [
            {
                "lap_number": 1,
                "lap_time": 95000,  # milliseconds
                "sector1_time": 30000,
                "sector2_time": 32000,
                "sector3_time": 33000,
                "valid": True
            },
            {
                "lap_number": 2,
                "lap_time": 93000,
                "sector1_time": 29500,
                "sector2_time": 31500,
                "sector3_time": 32000,
                "valid": True
            },
            {
                "lap_number": 3,
                "lap_time": 94000,
                "sector1_time": 30000,
                "sector2_time": 31000,
                "sector3_time": 33000,
                "valid": True
            }
        ]
        
        session_id = exporter.export_session(session_data, laps_data)
        logger.info(f"Session with {len(laps_data)} laps created: {session_id}")
        
        # Get statistics
        stats = exporter.get_session_statistics(session_id)
        logger.info(f"Best lap time: {stats['best_lap_time']}ms")
        logger.info(f"Average lap time: {stats['average_lap_time']:.2f}ms")
        
    finally:
        exporter.close()


def example_with_telemetry():
    """Export session with complete telemetry data"""
    logger.info("=== Telemetry Example ===")
    
    exporter = DatabaseExporter("sqlite:///data/telemetry.db")
    
    try:
        session_data = {
            "datetime": datetime.now(),
            "driver_name": "Player1"
        }
        
        # Complete session with laps and telemetry
        laps_with_telemetry = [
            {
                "lap_metadata": {
                    "lap_number": 1,
                    "lap_time": 95000,
                    "valid": True
                },
                "telemetry_points": [
                    {
                        "timestamp": 0,
                        "speed": 0.0,
                        "rpm": 1000,
                        "gear": 1,
                        "throttle": 0.0,
                        "brake": 0.0,
                        "position_x": 0.0,
                        "position_y": 0.0,
                        "position_z": 0.0,
                    },
                    {
                        "timestamp": 100,
                        "speed": 10.5,
                        "rpm": 2000,
                        "gear": 2,
                        "throttle": 0.8,
                        "brake": 0.0,
                        "position_x": 10.0,
                        "position_y": 5.0,
                        "position_z": 0.0,
                    },
                    {
                        "timestamp": 200,
                        "speed": 25.0,
                        "rpm": 3000,
                        "gear": 3,
                        "throttle": 1.0,
                        "brake": 0.0,
                        "position_x": 25.0,
                        "position_y": 10.0,
                        "position_z": 0.0,
                    },
                ]
            },
            {
                "lap_metadata": {
                    "lap_number": 2,
                    "lap_time": 93000,
                    "valid": True
                },
                "telemetry_points": [
                    {
                        "timestamp": 0,
                        "speed": 30.0,
                        "rpm": 3500,
                        "gear": 3,
                        "throttle": 1.0,
                        "brake": 0.0,
                    },
                    {
                        "timestamp": 100,
                        "speed": 35.0,
                        "rpm": 4000,
                        "gear": 4,
                        "throttle": 1.0,
                        "brake": 0.0,
                    },
                ]
            }
        ]
        
        session_id = exporter.export_complete_session(
            session_data,
            laps_with_telemetry
        )
        
        logger.info(f"Complete session exported: {session_id}")
        
        # Get detailed statistics
        stats = exporter.get_session_statistics(session_id)
        logger.info(f"Total laps: {stats['total_laps']}")
        logger.info(f"Telemetry points: {stats['telemetry_points']}")
        logger.info(f"Best lap time: {stats['best_lap_time']}ms")
        
    finally:
        exporter.close()


def example_querying_data():
    """Query and analyze stored data"""
    logger.info("=== Querying Data Example ===")
    
    exporter = DatabaseExporter("sqlite:///data/telemetry.db")
    
    try:
        # Get sessions by circuit
        sessions = exporter.repository.get_sessions_by_circuit("BL1")
        logger.info(f"Found {len(sessions)} sessions on BL1")
        
        if sessions:
            session = sessions[0]
            logger.info(f"Session: {session.datetime}, Driver: {session.driver_name}")
            
            # Get best lap
            best_lap = exporter.repository.get_best_lap(session.id)
            if best_lap:
                logger.info(f"Best lap: {best_lap.lap_time}ms on lap {best_lap.lap_number}")
                
                # Get telemetry for best lap
                telemetry = exporter.repository.get_telemetry_points(best_lap.id)
                logger.info(f"Telemetry points in best lap: {len(telemetry)}")
                
                if telemetry:
                    # Analyze telemetry
                    max_speed = max(p.speed for p in telemetry)
                    avg_speed = sum(p.speed for p in telemetry) / len(telemetry)
                    logger.info(f"Max speed: {max_speed:.2f} m/s")
                    logger.info(f"Avg speed: {avg_speed:.2f} m/s")
        
    finally:
        exporter.close()


def example_config_based():
    """Create exporter from configuration dictionary"""
    logger.info("=== Configuration-Based Example ===")
    
    # Configuration dictionary (could be loaded from YAML)
    config = {
        "type": "sqlite",
        "sqlite": {
            "path": "./data/telemetry.db"
        },
        "echo": False,
        "pool_size": 5
    }
    
    exporter = DatabaseExporter.from_config(config)
    
    try:
        session_data = {
            "datetime": datetime.now(),
            "driver_name": "Player1"
        }
        
        session_id = exporter.export_session(session_data)
        logger.info(f"Session created via config: {session_id}")
        
    finally:
        exporter.close()


def main():
    """Run all examples"""
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    logger.info("Starting database examples...\n")
    
    try:
        example_basic_usage()
        print()
        
        example_with_circuits_and_vehicles()
        print()
        
        example_with_laps()
        print()
        
        example_with_telemetry()
        print()
        
        example_querying_data()
        print()
        
        example_config_based()
        print()
        
        logger.info("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    main()
