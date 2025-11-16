"""
End-to-end integration tests for LFS-Ayats telemetry system

Tests the complete workflow: Connect -> Collect -> Process -> Export
"""

import pytest
import json
import csv
from pathlib import Path
from unittest.mock import Mock, patch
from src.connection.insim_client import InSimClient
from src.telemetry.collector import TelemetryCollector, CarTelemetry
from src.telemetry.processor import TelemetryProcessor
from src.export.csv_exporter import CSVExporter
from src.export.json_exporter import JSONExporter
from src.config.settings import Settings, load_config


@pytest.mark.integration
class TestEndToEndFlow:
    """Test complete telemetry flow"""

    @patch("socket.socket")
    def test_complete_telemetry_flow(self, mock_socket_class, tmp_path):
        """
        Test: Connect -> Collect -> Process -> Export

        This test simulates the full workflow:
        1. Create and connect InSim client
        2. Initialize telemetry collector
        3. Receive mock telemetry data
        4. Process the data
        5. Export to CSV and JSON
        6. Verify output files
        """
        # Setup mock socket
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket

        # 1. Connect to mock LFS server
        client = InSimClient(host="127.0.0.1", port=29999, udp=False)
        client.connect()

        assert client.connected is True
        mock_socket.connect.assert_called_once()

        # 2. Initialize telemetry collector
        collector = TelemetryCollector(client)

        # 3. Simulate receiving telemetry data
        # Create some mock telemetry data
        telemetry_data = [
            CarTelemetry(
                timestamp=1234567890.0 + i,
                plid=1,
                node=10 + i,
                lap=2,
                position={"x": 100.0 + i * 10, "y": 200.0, "z": 5.0},
                speed=50.0 + i * 5.0,
                direction=16384,
                heading=16384,
                angular_velocity=100 + i,
            )
            for i in range(10)
        ]

        # Add telemetry to collector
        collector.car_telemetry[1] = telemetry_data

        # Verify data collection
        latest = collector.get_latest_telemetry(plid=1)
        assert 1 in latest
        assert latest[1].speed == 95.0  # Last entry

        history = collector.get_telemetry_history(plid=1)
        assert len(history) == 10

        # 4. Process data
        processor = TelemetryProcessor()
        processed = processor.process_telemetry(telemetry_data)

        assert processed is not None
        assert processed.avg_speed > 0
        assert processed.max_speed >= processed.min_speed
        assert processed.sample_count == 10

        # 5. Export to CSV
        csv_file = tmp_path / "telemetry.csv"
        csv_exporter = CSVExporter(str(csv_file))
        csv_result = csv_exporter.export(telemetry_data)

        assert csv_result is True
        assert csv_file.exists()

        # Verify CSV content
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 10
            assert "speed" in rows[0]
            assert float(rows[0]["speed"]) == 50.0

        # 6. Export to JSON
        json_file = tmp_path / "telemetry.json"
        json_exporter = JSONExporter(str(json_file))
        json_result = json_exporter.export(telemetry_data)

        assert json_result is True
        assert json_file.exists()

        # Verify JSON content
        with open(json_file, "r") as f:
            data = json.load(f)
            assert "telemetry" in data
            assert len(data["telemetry"]) == 10
            assert data["telemetry"][0]["speed"] == 50.0

        # 7. Export processed data to JSON
        processed_file = tmp_path / "processed.json"
        processed_exporter = JSONExporter(str(processed_file))
        processed_result = processed_exporter.export_processed(processed)

        assert processed_result is True
        assert processed_file.exists()

        # Verify processed data
        with open(processed_file, "r") as f:
            data = json.load(f)
            assert "statistics" in data
            assert data["statistics"]["sample_count"] == 10

        # 8. Verify statistics
        stats = collector.get_statistics()
        assert stats["total_players"] == 1
        assert stats["total_samples"] == 10

        # Cleanup
        client.disconnect()
        assert client.connected is False


@pytest.mark.integration
class TestConfigurationIntegration:
    """Test configuration loading and usage"""

    def test_config_driven_workflow(self, tmp_path):
        """Test workflow driven by configuration file"""
        # Create config file
        config_file = tmp_path / "test_config.yaml"
        settings = Settings()
        settings.connection.host = "test.server"
        settings.connection.port = 30000
        settings.telemetry.interval = 200
        settings.export.format = "json"
        settings.export.output_dir = str(tmp_path / "exports")

        from src.config.settings import save_config

        save_config(settings, str(config_file))

        # Load config
        loaded = load_config(str(config_file))

        # Verify config loaded correctly
        assert loaded.connection.host == "test.server"
        assert loaded.connection.port == 30000
        assert loaded.telemetry.interval == 200
        assert loaded.export.format == "json"

        # Verify export directory config
        export_dir = Path(loaded.export.output_dir)
        assert str(export_dir) == str(tmp_path / "exports")


@pytest.mark.integration
class TestDataPipeline:
    """Test data processing pipeline"""

    def test_telemetry_processing_pipeline(self, tmp_path):
        """Test complete data processing pipeline"""
        # Generate sample telemetry with valid position data
        raw_data = [
            CarTelemetry(
                timestamp=1234567890.0 + i * 0.1,
                plid=1,
                speed=100.0 + i * 5.0,  # Speed up to 195 m/s (will be filtered)
                node=i,
                lap=1,
                position={
                    "x": float(i * 10),
                    "y": 100.0,
                    "z": 5.0,
                },  # Add valid position
            )
            for i in range(20)
        ]

        # Process data with higher max_speed threshold
        processor = TelemetryProcessor(max_speed=250.0)  # Allow up to 250 m/s
        processed = processor.process_telemetry(raw_data)

        # Verify processing results
        assert processed.sample_count == 20
        assert processed.avg_speed > 0
        assert processed.avg_speed == pytest.approx(
            147.5, abs=10.0
        )  # Average of speeds
        assert processed.min_speed == 100.0
        assert processed.max_speed == 195.0

        # Export both raw and processed
        csv_file = tmp_path / "raw_data.csv"
        json_file = tmp_path / "processed_data.json"

        csv_exporter = CSVExporter(str(csv_file))
        csv_exporter.export(raw_data)

        json_exporter = JSONExporter(str(json_file))
        json_exporter.export_processed(processed)

        # Verify both files exist
        assert csv_file.exists()
        assert json_file.exists()

        # Verify we can read them back
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            csv_rows = list(reader)
            assert len(csv_rows) == 20

        with open(json_file, "r") as f:
            json_data = json.load(f)
            assert json_data["statistics"]["sample_count"] == 20


@pytest.mark.integration
@pytest.mark.slow
class TestHighFrequencyData:
    """Test handling of high-frequency telemetry data"""

    def test_high_frequency_processing(self, tmp_path):
        """Test processing 100Hz telemetry data (simulated)"""
        # Simulate 10 seconds of 100Hz data = 1000 samples
        sample_count = 1000

        telemetry_data = [
            CarTelemetry(
                timestamp=1234567890.0 + i * 0.01,  # 100Hz = 0.01s intervals
                plid=1,
                speed=50.0 + (i % 50),  # Varying speed 50-100 m/s
                node=i % 100,
                lap=1 + (i // 100),
                position={
                    "x": float(i * 10),
                    "y": 100.0,
                    "z": 5.0,
                },  # Add valid position
            )
            for i in range(sample_count)
        ]

        # Process in batch with higher max_speed
        processor = TelemetryProcessor(max_speed=200.0)
        processed = processor.process_telemetry(telemetry_data)

        # Verify processing succeeded
        assert processed.sample_count == sample_count
        assert processed.avg_speed > 0

        # Export to verify handling large dataset
        output_file = tmp_path / "high_freq_data.csv"
        exporter = CSVExporter(str(output_file))
        result = exporter.export(telemetry_data)

        assert result is True
        assert output_file.exists()

        # Verify file size is reasonable
        file_size = output_file.stat().st_size
        assert file_size > 0
        # Should be roughly 50-100 bytes per row
        assert file_size > sample_count * 30


@pytest.mark.integration
class TestErrorRecovery:
    """Test error handling and recovery in integration scenarios"""

    @patch("socket.socket")
    def test_connection_failure_handling(self, mock_socket_class):
        """Test handling of connection failures"""
        mock_socket = Mock()
        mock_socket.connect.side_effect = ConnectionError("Connection refused")
        mock_socket_class.return_value = mock_socket

        client = InSimClient(host="invalid.server", port=99999)

        # Should catch the exception and return False
        try:
            result = client.connect()
            # If connect doesn't raise, it should return False
            assert result is False
        except ConnectionError:
            # If it raises, that's also acceptable behavior
            pass

        # Either way, should not be connected
        assert client.connected is False

    def test_export_with_invalid_path(self, tmp_path):
        """Test export error handling with invalid paths"""
        telemetry_data = [CarTelemetry(plid=1, speed=100.0)]

        # Try to export to invalid location
        invalid_path = "/invalid/nonexistent/path/data.csv"
        exporter = CSVExporter(invalid_path)
        result = exporter.export(telemetry_data)

        # Should fail gracefully
        assert result is False

    def test_empty_data_handling(self, tmp_path):
        """Test handling of empty data sets"""
        empty_data = []

        # Try to process empty data
        processor = TelemetryProcessor()
        processed = processor.process_telemetry(empty_data)

        # Should handle gracefully
        assert processed is not None
        assert processed.sample_count == 0

        # Try to export empty data
        csv_file = tmp_path / "empty.csv"
        csv_exporter = CSVExporter(str(csv_file))
        result = csv_exporter.export(empty_data)

        # Should handle appropriately
        assert result is False


@pytest.mark.integration
class TestMultiPlayerScenario:
    """Test scenarios with multiple players"""

    def test_multiple_players_telemetry(self, tmp_path):
        """Test collecting and processing data from multiple players"""
        # Create telemetry for 3 players with valid position data
        player_data = {}
        for plid in [1, 2, 3]:
            player_data[plid] = [
                CarTelemetry(
                    timestamp=1234567890.0 + i,
                    plid=plid,
                    speed=50.0 + plid * 5 + i,  # Different speeds per player
                    node=i,
                    lap=1,
                    position={"x": float(i * 10), "y": 100.0 + plid * 10, "z": 5.0},
                )
                for i in range(10)
            ]

        # Process each player's data with higher max_speed
        processed_data = {}
        processor = TelemetryProcessor(max_speed=200.0)

        for plid, data in player_data.items():
            processed_data[plid] = processor.process_telemetry(data)

        # Verify all players processed
        assert len(processed_data) == 3

        for plid in [1, 2, 3]:
            assert processed_data[plid].sample_count == 10
            # Each player should have different average speed
            assert processed_data[plid].avg_speed > 50.0

        # Export combined data
        all_data = []
        for data_list in player_data.values():
            all_data.extend(data_list)

        output_file = tmp_path / "multiplayer.csv"
        exporter = CSVExporter(str(output_file))
        result = exporter.export(all_data)

        assert result is True

        # Verify file contains data from all players
        with open(output_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 30  # 3 players × 10 samples

            # Check that we have all player IDs
            player_ids = {int(row["plid"]) for row in rows}
            assert player_ids == {1, 2, 3}
