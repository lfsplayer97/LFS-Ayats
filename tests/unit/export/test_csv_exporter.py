"""
Unit tests for CSVExporter
"""

import pytest
import csv
from pathlib import Path
from dataclasses import dataclass, field
from src.export.csv_exporter import CSVExporter


# Mock CarTelemetry for testing
@dataclass
class MockCarTelemetry:
    timestamp: float = 0.0
    plid: int = 1
    node: int = 0
    lap: int = 1
    position: dict = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    speed: float = 0.0
    direction: int = 0
    heading: int = 0
    angular_velocity: int = 0


@dataclass
class MockProcessedTelemetry:
    avg_speed: float = 20.0
    max_speed: float = 30.0
    min_speed: float = 10.0
    total_distance: float = 1000.0
    sample_count: int = 100


class TestCSVExporter:
    """Test cases for CSVExporter"""

    def test_init(self, tmp_path):
        """Test exporter initialization"""
        filename = tmp_path / "test.csv"
        exporter = CSVExporter(str(filename))

        assert exporter.filename == filename
        assert exporter.delimiter == ","

    def test_export_empty_list(self, tmp_path):
        """Test exporting empty list"""
        filename = tmp_path / "test.csv"
        exporter = CSVExporter(str(filename))

        result = exporter.export([])

        assert result is False

    def test_export_valid_data(self, tmp_path):
        """Test exporting valid telemetry data"""
        filename = tmp_path / "test.csv"
        exporter = CSVExporter(str(filename))

        telemetry_data = [
            MockCarTelemetry(timestamp=1.0, plid=1, speed=20.0),
            MockCarTelemetry(timestamp=2.0, plid=1, speed=25.0),
        ]

        result = exporter.export(telemetry_data)

        assert result is True
        assert filename.exists()

        # Verify content
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["speed"] == "20.0"
            assert rows[1]["speed"] == "25.0"

    def test_export_with_custom_delimiter(self, tmp_path):
        """Test exporting with custom delimiter"""
        filename = tmp_path / "test.csv"
        exporter = CSVExporter(str(filename), delimiter=";")

        telemetry_data = [
            MockCarTelemetry(speed=20.0),
        ]

        result = exporter.export(telemetry_data)

        assert result is True

        # Verify delimiter
        with open(filename, "r") as f:
            content = f.read()
            assert ";" in content

    def test_export_processed(self, tmp_path):
        """Test exporting processed data"""
        filename = tmp_path / "processed.csv"
        exporter = CSVExporter(str(filename))

        processed_data = MockProcessedTelemetry()

        result = exporter.export_processed(processed_data)

        assert result is True
        assert filename.exists()

        # Verify content
        with open(filename, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) > 0
            assert rows[0][0] == "Metric"

    def test_export_overwrite(self, tmp_path):
        """Test overwriting existing file"""
        filename = tmp_path / "test.csv"
        exporter = CSVExporter(str(filename))

        # First export
        telemetry_data1 = [MockCarTelemetry(speed=20.0)]
        exporter.export(telemetry_data1, overwrite=True)

        # Second export (overwrite)
        telemetry_data2 = [MockCarTelemetry(speed=30.0)]
        exporter.export(telemetry_data2, overwrite=True)

        # Verify only second data exists
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["speed"] == "30.0"
