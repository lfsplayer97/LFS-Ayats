"""
Unit tests for analysis module initialization
"""

from src.analysis import (
    AnomalyDetector,
    PerformancePredictor,
    SectorAnalyzer,
    AdvancedComparator,
    AlertSystem,
    Alert,
    AlertLevel,
    MetricsCalculator,
)


class TestAnalysisModuleImports:
    """Test that all analysis components can be imported."""

    def test_anomaly_detector_import(self):
        """Test AnomalyDetector can be instantiated."""
        detector = AnomalyDetector()
        assert detector is not None

    def test_performance_predictor_import(self):
        """Test PerformancePredictor can be instantiated."""
        predictor = PerformancePredictor()
        assert predictor is not None

    def test_sector_analyzer_import(self):
        """Test SectorAnalyzer can be instantiated."""
        analyzer = SectorAnalyzer()
        assert analyzer is not None

    def test_advanced_comparator_import(self):
        """Test AdvancedComparator can be instantiated."""
        comparator = AdvancedComparator()
        assert comparator is not None

    def test_alert_system_import(self):
        """Test AlertSystem can be instantiated."""
        system = AlertSystem()
        assert system is not None

    def test_metrics_calculator_import(self):
        """Test MetricsCalculator can be instantiated."""
        calculator = MetricsCalculator()
        assert calculator is not None

    def test_alert_model_import(self):
        """Test Alert model can be instantiated."""
        alert = Alert(level=AlertLevel.INFO, message="Test")
        assert alert is not None
        assert alert.level == AlertLevel.INFO
        assert alert.message == "Test"
