"""
Unit tests for JSON Exporter
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock
from src.export.json_exporter import JSONExporter


class TestJSONExporter:
    """Test cases for JSONExporter"""

    def test_init(self, tmp_path):
        """Test exporter initialization"""
        filename = tmp_path / "test.json"
        exporter = JSONExporter(str(filename))
        
        assert exporter.filename == Path(filename)
        assert exporter.indent == 2

    def test_init_custom_indent(self, tmp_path):
        """Test initialization with custom indent"""
        filename = tmp_path / "test.json"
        exporter = JSONExporter(str(filename), indent=4)
        
        assert exporter.indent == 4

    def test_export_basic_data(self, tmp_path):
        """Test basic JSON export"""
        filename = tmp_path / "telemetry.json"
        exporter = JSONExporter(str(filename))
        
        # Create mock telemetry data
        mock_data = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            ),
            Mock(
                timestamp=1234567891.0,
                plid=1,
                node=11,
                lap=2,
                position=1,
                speed=155.0,
                direction=16500,
                heading=16500,
                angular_velocity=110
            )
        ]
        
        result = exporter.export(mock_data)
        
        assert result is True
        assert filename.exists()
        
        # Verify content
        with open(filename, 'r') as f:
            data = json.load(f)
        
        assert 'metadata' in data
        assert 'telemetry' in data
        assert len(data['telemetry']) == 2
        assert data['telemetry'][0]['speed'] == 150.5
        assert data['telemetry'][1]['speed'] == 155.0

    def test_export_with_metadata(self, tmp_path):
        """Test export with custom metadata"""
        filename = tmp_path / "telemetry.json"
        exporter = JSONExporter(str(filename))
        
        mock_data = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            )
        ]
        
        metadata = {
            'session_id': 'test-session',
            'track': 'BL1',
            'car': 'XRG'
        }
        
        result = exporter.export(mock_data, metadata=metadata)
        
        assert result is True
        
        # Verify metadata
        with open(filename, 'r') as f:
            data = json.load(f)
        
        assert data['metadata']['session_id'] == 'test-session'
        assert data['metadata']['track'] == 'BL1'

    def test_export_empty_data(self, tmp_path):
        """Test handling of empty data"""
        filename = tmp_path / "empty.json"
        exporter = JSONExporter(str(filename))
        
        result = exporter.export([])
        
        assert result is False
        assert not filename.exists()

    def test_export_nested_data(self, tmp_path):
        """Test export of nested data structures"""
        filename = tmp_path / "nested.json"
        exporter = JSONExporter(str(filename))
        
        mock_data = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            )
        ]
        
        result = exporter.export(mock_data)
        
        assert result is True
        
        # Verify structure
        with open(filename, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert isinstance(data['metadata'], dict)
        assert isinstance(data['telemetry'], list)
        assert isinstance(data['telemetry'][0], dict)

    def test_pretty_print(self, tmp_path):
        """Test pretty-printed JSON output"""
        filename = tmp_path / "pretty.json"
        exporter = JSONExporter(str(filename), indent=4)
        
        mock_data = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            )
        ]
        
        result = exporter.export(mock_data)
        
        assert result is True
        
        # Verify indentation
        content = filename.read_text()
        assert '    ' in content  # 4-space indentation
        
        # Verify JSON is valid
        data = json.loads(content)
        assert 'telemetry' in data

    def test_export_processed_data(self, tmp_path):
        """Test export of processed telemetry data"""
        filename = tmp_path / "processed.json"
        exporter = JSONExporter(str(filename))
        
        # Create mock processed data
        mock_processed = Mock(
            avg_speed=150.0,
            max_speed=180.0,
            min_speed=120.0,
            total_distance=1500.0,
            sample_count=100
        )
        
        result = exporter.export_processed(mock_processed)
        
        assert result is True
        assert filename.exists()
        
        # Verify content
        with open(filename, 'r') as f:
            data = json.load(f)
        
        assert 'statistics' in data
        assert data['statistics']['avg_speed'] == 150.0
        assert data['statistics']['max_speed'] == 180.0
        assert data['statistics']['sample_count'] == 100

    def test_export_processed_with_metadata(self, tmp_path):
        """Test export of processed data with metadata"""
        filename = tmp_path / "processed_meta.json"
        exporter = JSONExporter(str(filename))
        
        mock_processed = Mock(
            avg_speed=150.0,
            max_speed=180.0,
            min_speed=120.0,
            total_distance=1500.0,
            sample_count=100
        )
        
        metadata = {'session': 'race-1', 'laps': 10}
        
        result = exporter.export_processed(mock_processed, metadata=metadata)
        
        assert result is True
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        assert data['metadata']['session'] == 'race-1'
        assert 'statistics' in data

    def test_append_to_new_file(self, tmp_path):
        """Test appending to a new file"""
        filename = tmp_path / "append_new.json"
        exporter = JSONExporter(str(filename))
        
        mock_data = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            )
        ]
        
        result = exporter.append(mock_data)
        
        assert result is True
        assert filename.exists()
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        assert len(data['telemetry']) == 1

    def test_append_to_existing_file(self, tmp_path):
        """Test appending to existing JSON"""
        filename = tmp_path / "append_existing.json"
        exporter = JSONExporter(str(filename))
        
        # First export
        mock_data1 = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            )
        ]
        exporter.export(mock_data1)
        
        # Append more data
        mock_data2 = [
            Mock(
                timestamp=1234567891.0,
                plid=1,
                node=11,
                lap=2,
                position=1,
                speed=155.0,
                direction=16500,
                heading=16500,
                angular_velocity=110
            )
        ]
        
        result = exporter.append(mock_data2)
        
        assert result is True
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        assert len(data['telemetry']) == 2
        assert data['metadata']['sample_count'] == 2
        assert 'last_update' in data['metadata']

    def test_export_error_handling(self, tmp_path):
        """Test error handling during export"""
        # Try to export to invalid path
        exporter = JSONExporter('/invalid/path/file.json')
        
        mock_data = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            )
        ]
        
        result = exporter.export(mock_data)
        
        assert result is False

    def test_append_error_handling(self):
        """Test error handling during append"""
        exporter = JSONExporter('/invalid/path/file.json')
        
        mock_data = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            )
        ]
        
        result = exporter.append(mock_data)
        
        assert result is False

    def test_export_processed_error_handling(self):
        """Test error handling for processed data export"""
        exporter = JSONExporter('/invalid/path/file.json')
        
        mock_processed = Mock(
            avg_speed=150.0,
            max_speed=180.0,
            min_speed=120.0,
            total_distance=1500.0,
            sample_count=100
        )
        
        result = exporter.export_processed(mock_processed)
        
        assert result is False

    def test_utf8_encoding(self, tmp_path):
        """Test UTF-8 encoding support"""
        filename = tmp_path / "utf8.json"
        exporter = JSONExporter(str(filename))
        
        mock_data = [
            Mock(
                timestamp=1234567890.0,
                plid=1,
                node=10,
                lap=2,
                position=1,
                speed=150.5,
                direction=16384,
                heading=16384,
                angular_velocity=100
            )
        ]
        
        metadata = {
            'driver': 'José García',
            'track': 'Montmeló'
        }
        
        result = exporter.export(mock_data, metadata=metadata)
        
        assert result is True
        
        # Verify UTF-8 content
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['metadata']['driver'] == 'José García'
        assert data['metadata']['track'] == 'Montmeló'
