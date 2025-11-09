"""
Unit tests for TelemetryProcessor
"""

import pytest
from dataclasses import dataclass, field
from src.telemetry.processor import TelemetryProcessor, ProcessedTelemetry


# Mock CarTelemetry for testing
@dataclass
class MockCarTelemetry:
    timestamp: float = 0.0
    plid: int = 1
    node: int = 0
    lap: int = 1
    position: dict = field(default_factory=lambda: {'x': 0, 'y': 0, 'z': 0})
    speed: float = 0.0
    direction: int = 0
    heading: int = 0
    angular_velocity: int = 0


class TestTelemetryProcessor:
    """Test cases for TelemetryProcessor"""

    def test_init(self):
        """Test processor initialization"""
        processor = TelemetryProcessor(max_speed=100.0)
        assert processor.max_speed == 100.0
        assert processor.validation_errors == []

    def test_validate_telemetry_valid(self):
        """Test validation of valid telemetry"""
        processor = TelemetryProcessor()
        telemetry = MockCarTelemetry(
            plid=1,
            speed=50.0,
            position={'x': 100, 'y': 200, 'z': 10}
        )
        
        result = processor.validate_telemetry(telemetry)
        
        assert result is True
        assert len(processor.validation_errors) == 0

    def test_validate_telemetry_negative_speed(self):
        """Test validation with negative speed"""
        processor = TelemetryProcessor()
        telemetry = MockCarTelemetry(speed=-10.0)
        
        result = processor.validate_telemetry(telemetry)
        
        assert result is False
        assert "Velocitat negativa" in processor.validation_errors

    def test_validate_telemetry_excessive_speed(self):
        """Test validation with excessive speed"""
        processor = TelemetryProcessor(max_speed=100.0)
        telemetry = MockCarTelemetry(speed=200.0)
        
        result = processor.validate_telemetry(telemetry)
        
        assert result is False
        assert any("massa alta" in err for err in processor.validation_errors)

    def test_validate_telemetry_invalid_plid(self):
        """Test validation with invalid player ID"""
        processor = TelemetryProcessor()
        telemetry = MockCarTelemetry(plid=-1)
        
        result = processor.validate_telemetry(telemetry)
        
        assert result is False
        assert any("invàlid" in err for err in processor.validation_errors)

    def test_validate_telemetry_empty_position(self):
        """Test validation with empty position"""
        processor = TelemetryProcessor()
        telemetry = MockCarTelemetry(position={})
        
        result = processor.validate_telemetry(telemetry)
        
        assert result is False
        assert "Posició buida" in processor.validation_errors

    def test_process_telemetry_empty_list(self):
        """Test processing empty telemetry list"""
        processor = TelemetryProcessor()
        
        result = processor.process_telemetry([])
        
        assert result.sample_count == 0
        assert result.avg_speed == 0.0

    def test_process_telemetry_valid_data(self):
        """Test processing valid telemetry data"""
        processor = TelemetryProcessor()
        
        telemetry_list = [
            MockCarTelemetry(speed=10.0, position={'x': 0, 'y': 0, 'z': 0}),
            MockCarTelemetry(speed=20.0, position={'x': 10, 'y': 0, 'z': 0}),
            MockCarTelemetry(speed=30.0, position={'x': 20, 'y': 0, 'z': 0}),
        ]
        
        result = processor.process_telemetry(telemetry_list)
        
        assert result.sample_count == 3
        assert result.avg_speed == 20.0
        assert result.max_speed == 30.0
        assert result.min_speed == 10.0
        assert result.total_distance > 0

    def test_calculate_statistics(self):
        """Test calculating statistics"""
        processor = TelemetryProcessor()
        
        telemetry_list = [
            MockCarTelemetry(speed=10.0),
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=30.0),
        ]
        
        stats = processor.calculate_statistics(telemetry_list)
        
        assert 'speed' in stats
        assert stats['speed']['mean'] == 20.0
        assert stats['speed']['min'] == 10.0
        assert stats['speed']['max'] == 30.0
        assert stats['sample_count'] == 3

    def test_filter_by_speed_range(self):
        """Test filtering by speed range"""
        processor = TelemetryProcessor()
        
        telemetry_list = [
            MockCarTelemetry(speed=5.0),
            MockCarTelemetry(speed=15.0),
            MockCarTelemetry(speed=25.0),
            MockCarTelemetry(speed=35.0),
        ]
        
        filtered = processor.filter_by_speed_range(telemetry_list, 10.0, 30.0)
        
        assert len(filtered) == 2
        assert all(10.0 <= t.speed <= 30.0 for t in filtered)

    def test_detect_anomalies(self):
        """Test anomaly detection"""
        processor = TelemetryProcessor()
        
        # Normal data with one outlier - using more data points for stable statistics
        telemetry_list = [
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=21.0),
            MockCarTelemetry(speed=19.0),
            MockCarTelemetry(speed=20.5),
            MockCarTelemetry(speed=19.5),
            MockCarTelemetry(speed=20.2),
            MockCarTelemetry(speed=19.8),
            MockCarTelemetry(speed=100.0),  # Outlier
        ]
        
        anomalies = processor.detect_anomalies(telemetry_list, threshold_stdev=2.0)
        
        assert len(anomalies) > 0
        assert 7 in anomalies  # Index of outlier

    def test_get_validation_errors(self):
        """Test getting validation errors"""
        processor = TelemetryProcessor()
        telemetry = MockCarTelemetry(speed=-10.0)
        
        processor.validate_telemetry(telemetry)
        errors = processor.get_validation_errors()
        
        assert len(errors) > 0
        assert isinstance(errors, list)
