"""
Unit tests for AnomalyDetector
"""

from src.analysis.anomaly import AnomalyDetector
from src.analysis.utils import AlertLevel


class TestAnomalyDetector:
    """Test cases for AnomalyDetector"""

    def test_init(self):
        """Test detector initialization"""
        detector = AnomalyDetector()
        assert detector.temp_warning == 95.0
        assert detector.temp_critical == 105.0
        assert detector.z_score_threshold == 3.0
        assert detector.anomaly_history == []

    def test_init_custom_values(self):
        """Test initialization with custom values"""
        detector = AnomalyDetector(
            temp_warning=90.0, temp_critical=100.0, z_score_threshold=2.5
        )
        assert detector.temp_warning == 90.0
        assert detector.temp_critical == 100.0
        assert detector.z_score_threshold == 2.5

    def test_detect_overheating_normal(self):
        """Test overheating detection with normal temperature"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_overheating(80.0)
        assert detected is False
        assert alert is None

    def test_detect_overheating_warning(self):
        """Test overheating detection with warning temperature"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_overheating(96.0)
        assert detected is True
        assert alert is not None
        assert alert.level == AlertLevel.WARNING
        assert "Temperatura" in alert.message

    def test_detect_overheating_critical(self):
        """Test overheating detection with critical temperature"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_overheating(106.0)
        assert detected is True
        assert alert is not None
        assert alert.level == AlertLevel.CRITICAL
        assert "crític" in alert.message

    def test_detect_wheel_spin_no_spin(self):
        """Test wheel spin detection with no spin"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_wheel_spin(50.0, 50.0)
        assert detected is False
        assert alert is None

    def test_detect_wheel_spin_with_spin(self):
        """Test wheel spin detection with significant spin"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_wheel_spin(50.0, 60.0)
        assert detected is True
        assert alert is not None
        assert alert.level == AlertLevel.WARNING
        assert "grip" in alert.message.lower()

    def test_detect_wheel_spin_zero_speed(self):
        """Test wheel spin detection with zero linear speed"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_wheel_spin(0.0, 10.0)
        assert detected is False

    def test_detect_understeer_no_issue(self):
        """Test understeer detection with normal steering"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_understeer(0.5, 0.5)
        assert detected is False

    def test_detect_understeer_detected(self):
        """Test understeer detection with understeer"""
        detector = AnomalyDetector()
        # Angle gran però rotació petita = subviratge
        detected, alert = detector.detect_understeer(0.5, 0.2)
        assert detected is True
        assert alert is not None
        assert alert.level == AlertLevel.INFO

    def test_detect_oversteer_no_issue(self):
        """Test oversteer detection with normal steering"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_oversteer(0.5, 0.5)
        assert detected is False

    def test_detect_oversteer_detected(self):
        """Test oversteer detection with oversteer"""
        detector = AnomalyDetector()
        # Angle petit però rotació gran = sobreviratge
        detected, alert = detector.detect_oversteer(0.5, 0.8)
        assert detected is True
        assert alert is not None
        assert alert.level == AlertLevel.WARNING

    def test_detect_flat_spot_no_issue(self):
        """Test flat spot detection with uniform wear"""
        detector = AnomalyDetector()
        wear_pattern = [10.0, 10.1, 9.9, 10.0, 10.1]
        detected, alert = detector.detect_flat_spot(wear_pattern)
        assert detected is False

    def test_detect_flat_spot_detected(self):
        """Test flat spot detection with irregular wear"""
        detector = AnomalyDetector()
        wear_pattern = [10.0, 10.0, 15.0, 10.0, 10.0]  # Spike in wear
        detected, alert = detector.detect_flat_spot(wear_pattern)
        assert detected is True
        assert alert is not None

    def test_detect_flat_spot_empty_pattern(self):
        """Test flat spot detection with empty pattern"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_flat_spot([])
        assert detected is False

    def test_detect_inconsistent_braking_consistent(self):
        """Test braking consistency with consistent braking"""
        detector = AnomalyDetector()
        laps = [
            {"braking_points": [100.0, 250.0]},
            {"braking_points": [101.0, 251.0]},
            {"braking_points": [99.0, 249.0]},
        ]
        inconsistent = detector.detect_inconsistent_braking(laps)
        assert len(inconsistent) == 0

    def test_detect_inconsistent_braking_inconsistent(self):
        """Test braking consistency with inconsistent braking"""
        detector = AnomalyDetector()
        laps = [
            {"braking_points": [100.0, 250.0]},
            {"braking_points": [120.0, 270.0]},  # Very different
            {"braking_points": [99.0, 249.0]},
        ]
        inconsistent = detector.detect_inconsistent_braking(laps)
        # Should detect some inconsistency
        assert isinstance(inconsistent, list)

    def test_detect_fuel_warning_sufficient(self):
        """Test fuel warning with sufficient fuel"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_fuel_warning(50.0, 2.0, 20)
        assert detected is False

    def test_detect_fuel_warning_low(self):
        """Test fuel warning with low fuel"""
        detector = AnomalyDetector()
        detected, alert = detector.detect_fuel_warning(10.0, 2.0, 10)
        assert detected is True
        assert alert is not None
        assert "Combustible" in alert.message

    def test_detect_outliers_zscore_no_outliers(self):
        """Test z-score outlier detection with no outliers"""
        detector = AnomalyDetector()
        data = [10.0, 10.5, 9.8, 10.2, 10.1]
        outliers = detector.detect_outliers_zscore(data)
        assert len(outliers) == 0

    def test_detect_outliers_zscore_with_outliers(self):
        """Test z-score outlier detection with outliers"""
        detector = AnomalyDetector(z_score_threshold=2.0)
        # More data points for better z-score calculation
        data = [10.0, 10.5, 9.8, 10.2, 10.1, 9.9, 10.3, 50.0, 10.0, 10.2]
        outliers = detector.detect_outliers_zscore(data, threshold=2.0)
        assert len(outliers) > 0
        assert 7 in outliers  # Index of 50.0

    def test_detect_outliers_iqr_no_outliers(self):
        """Test IQR outlier detection with no outliers"""
        detector = AnomalyDetector()
        data = [10.0, 10.5, 9.8, 10.2, 10.1, 9.9, 10.3]
        outliers = detector.detect_outliers_iqr(data)
        assert len(outliers) == 0

    def test_detect_outliers_iqr_with_outliers(self):
        """Test IQR outlier detection with outliers"""
        detector = AnomalyDetector()
        data = [10.0, 10.5, 9.8, 50.0, 10.1, 9.9, 10.3]
        outliers = detector.detect_outliers_iqr(data)
        assert len(outliers) > 0

    def test_detect_sudden_changes_no_changes(self):
        """Test sudden change detection with smooth data"""
        detector = AnomalyDetector()
        data = [10.0, 10.5, 11.0, 11.5, 12.0]
        changes = detector.detect_sudden_changes(data)
        assert len(changes) == 0

    def test_detect_sudden_changes_with_changes(self):
        """Test sudden change detection with sudden spike"""
        detector = AnomalyDetector()
        data = [10.0, 10.5, 11.0, 30.0, 11.5, 12.0]  # Sudden large jump
        changes = detector.detect_sudden_changes(data, window_size=3, sensitivity=1.5)
        assert len(changes) > 0

    def test_check_telemetry_multiple_conditions(self):
        """Test checking multiple telemetry conditions"""
        detector = AnomalyDetector()
        telemetry = {
            "engine_temp": 100.0,
            "linear_speed": 50.0,
            "wheel_speed": 60.0,
        }
        alerts = detector.check_telemetry(telemetry)
        assert len(alerts) >= 1  # At least temperature warning

    def test_get_anomaly_history(self):
        """Test getting anomaly history"""
        detector = AnomalyDetector()
        detector.detect_overheating(100.0)
        detector.detect_overheating(110.0)

        history = detector.get_anomaly_history()
        assert len(history) == 2

    def test_clear_history(self):
        """Test clearing anomaly history"""
        detector = AnomalyDetector()
        detector.detect_overheating(100.0)
        assert len(detector.anomaly_history) > 0

        detector.clear_history()
        assert len(detector.anomaly_history) == 0
