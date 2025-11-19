"""
Unit tests for TelemetryProcessor
"""

from dataclasses import dataclass, field
from src.telemetry.processor import TelemetryProcessor


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
            plid=1, speed=50.0, position={"x": 100, "y": 200, "z": 10}
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
        assert "Negative speed" in processor.validation_errors

    def test_validate_telemetry_excessive_speed(self):
        """Test validation with excessive speed"""
        processor = TelemetryProcessor(max_speed=100.0)
        telemetry = MockCarTelemetry(speed=200.0)

        result = processor.validate_telemetry(telemetry)

        assert result is False
        assert any("too high" in err for err in processor.validation_errors)

    def test_validate_telemetry_invalid_plid(self):
        """Test validation with invalid player ID"""
        processor = TelemetryProcessor()
        telemetry = MockCarTelemetry(plid=-1)

        result = processor.validate_telemetry(telemetry)

        assert result is False
        assert any("Invalid Player ID" in err for err in processor.validation_errors)

    def test_validate_telemetry_empty_position(self):
        """Test validation with empty position"""
        processor = TelemetryProcessor()
        telemetry = MockCarTelemetry(position={})

        result = processor.validate_telemetry(telemetry)

        assert result is False
        assert "Empty position" in processor.validation_errors

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
            MockCarTelemetry(speed=10.0, position={"x": 0, "y": 0, "z": 0}),
            MockCarTelemetry(speed=20.0, position={"x": 10, "y": 0, "z": 0}),
            MockCarTelemetry(speed=30.0, position={"x": 20, "y": 0, "z": 0}),
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

        assert "speed" in stats
        assert stats["speed"]["mean"] == 20.0
        assert stats["speed"]["min"] == 10.0
        assert stats["speed"]["max"] == 30.0
        assert stats["sample_count"] == 3

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


class TestTelemetryProcessorEdgeCases:
    """Test edge cases for TelemetryProcessor"""

    def test_process_telemetry_all_invalid(self):
        """Test processing telemetry with all invalid data"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=-10.0),  # Invalid negative speed
            MockCarTelemetry(speed=-20.0),  # Invalid negative speed
        ]

        result = processor.process_telemetry(telemetry_list)

        assert result.sample_count == 0
        assert result.avg_speed == 0.0

    def test_process_telemetry_mixed_validity(self):
        """Test processing telemetry with mix of valid and invalid data"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=20.0, position={"x": 0, "y": 0, "z": 0}),
            MockCarTelemetry(speed=-10.0),  # Invalid
            MockCarTelemetry(speed=30.0, position={"x": 10, "y": 0, "z": 0}),
        ]

        result = processor.process_telemetry(telemetry_list)

        assert result.sample_count == 2  # Only valid ones
        assert result.avg_speed == 25.0

    def test_calculate_statistics_empty_list(self):
        """Test calculating statistics with empty list"""
        processor = TelemetryProcessor()

        stats = processor.calculate_statistics([])

        assert stats == {}

    def test_calculate_statistics_all_invalid(self):
        """Test calculating statistics with all invalid data"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=-10.0),
            MockCarTelemetry(speed=-20.0),
        ]

        stats = processor.calculate_statistics(telemetry_list)

        assert stats == {}

    def test_calculate_statistics_single_point(self):
        """Test calculating statistics with single data point"""
        processor = TelemetryProcessor()

        telemetry_list = [MockCarTelemetry(speed=50.0)]

        stats = processor.calculate_statistics(telemetry_list)

        assert "speed" in stats
        assert stats["speed"]["mean"] == 50.0
        assert stats["speed"]["stdev"] == 0  # Single point has 0 stdev

    def test_filter_by_speed_range_no_max(self):
        """Test filtering by speed range without maximum"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=5.0),
            MockCarTelemetry(speed=15.0),
            MockCarTelemetry(speed=25.0),
            MockCarTelemetry(speed=100.0),
        ]

        filtered = processor.filter_by_speed_range(telemetry_list, min_speed=10.0)

        assert len(filtered) == 3
        assert all(t.speed >= 10.0 for t in filtered)

    def test_filter_by_speed_range_all_excluded(self):
        """Test filtering where all data is excluded"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=5.0),
            MockCarTelemetry(speed=15.0),
            MockCarTelemetry(speed=25.0),
        ]

        filtered = processor.filter_by_speed_range(
            telemetry_list, min_speed=30.0, max_speed=50.0
        )

        assert len(filtered) == 0

    def test_filter_by_speed_range_boundary_values(self):
        """Test filtering with boundary values"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=10.0),
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=30.0),
        ]

        # Exact boundaries should be included
        filtered = processor.filter_by_speed_range(
            telemetry_list, min_speed=10.0, max_speed=30.0
        )

        assert len(filtered) == 3

    def test_detect_anomalies_too_few_samples(self):
        """Test anomaly detection with too few samples"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=21.0),
        ]

        anomalies = processor.detect_anomalies(telemetry_list)

        assert len(anomalies) == 0  # Not enough samples

    def test_detect_anomalies_no_outliers(self):
        """Test anomaly detection with no outliers"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=21.0),
            MockCarTelemetry(speed=19.0),
            MockCarTelemetry(speed=20.5),
        ]

        anomalies = processor.detect_anomalies(telemetry_list, threshold_stdev=3.0)

        assert len(anomalies) == 0

    def test_detect_anomalies_zero_stdev(self):
        """Test anomaly detection when all values are the same (zero stdev)"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=20.0),
        ]

        anomalies = processor.detect_anomalies(telemetry_list)

        assert len(anomalies) == 0

    def test_detect_anomalies_custom_threshold(self):
        """Test anomaly detection with custom threshold"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=20.0),
            MockCarTelemetry(speed=21.0),
            MockCarTelemetry(speed=19.0),
            MockCarTelemetry(speed=20.5),
            MockCarTelemetry(speed=50.0),  # Moderate outlier
        ]

        # With low threshold, should detect outlier
        anomalies_low = processor.detect_anomalies(telemetry_list, threshold_stdev=1.5)
        assert len(anomalies_low) > 0

        # With high threshold, may not detect
        anomalies_high = processor.detect_anomalies(telemetry_list, threshold_stdev=5.0)
        assert len(anomalies_high) == 0

    def test_validate_telemetry_plid_at_boundary(self):
        """Test validation with player ID at boundaries"""
        processor = TelemetryProcessor()

        # Valid boundaries
        telemetry_0 = MockCarTelemetry(plid=0)
        telemetry_255 = MockCarTelemetry(plid=255)

        assert processor.validate_telemetry(telemetry_0) is True
        assert processor.validate_telemetry(telemetry_255) is True

        # Invalid boundaries
        telemetry_neg = MockCarTelemetry(plid=-1)
        telemetry_high = MockCarTelemetry(plid=256)

        assert processor.validate_telemetry(telemetry_neg) is False
        assert processor.validate_telemetry(telemetry_high) is False

    def test_validate_telemetry_clears_previous_errors(self):
        """Test that validation clears previous errors"""
        processor = TelemetryProcessor()

        # First validation with error
        bad_telemetry = MockCarTelemetry(speed=-10.0)
        processor.validate_telemetry(bad_telemetry)
        assert len(processor.validation_errors) > 0

        # Second validation with valid data should clear errors
        good_telemetry = MockCarTelemetry(speed=20.0)
        processor.validate_telemetry(good_telemetry)
        assert len(processor.validation_errors) == 0

    def test_process_telemetry_distance_calculation(self):
        """Test distance calculation in process_telemetry"""
        processor = TelemetryProcessor()

        # Create telemetry with known positions
        telemetry_list = [
            MockCarTelemetry(speed=10.0, position={"x": 0, "y": 0, "z": 0}),
            MockCarTelemetry(speed=10.0, position={"x": 3, "y": 4, "z": 0}),  # 5 units away
        ]

        result = processor.process_telemetry(telemetry_list)

        # Distance should be approximately 5 (3-4-5 triangle)
        assert result.total_distance > 4.9
        assert result.total_distance < 5.1

    def test_process_telemetry_missing_position_fields(self):
        """Test processing telemetry with missing position fields"""
        processor = TelemetryProcessor()

        telemetry_list = [
            MockCarTelemetry(speed=10.0, position={"x": 0}),  # Missing y, z
            MockCarTelemetry(speed=20.0, position={"x": 10}),
        ]

        result = processor.process_telemetry(telemetry_list)

        # Should still calculate statistics even with incomplete positions
        assert result.sample_count == 2
        assert result.avg_speed == 15.0

    def test_get_validation_errors_returns_copy(self):
        """Test that get_validation_errors returns a copy"""
        processor = TelemetryProcessor()
        telemetry = MockCarTelemetry(speed=-10.0)

        processor.validate_telemetry(telemetry)
        errors1 = processor.get_validation_errors()
        errors2 = processor.get_validation_errors()

        # Should be equal but different objects
        assert errors1 == errors2
        assert errors1 is not errors2
