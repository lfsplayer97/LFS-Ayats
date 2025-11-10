"""
Unit tests for PerformancePredictor
"""

from src.analysis.predictor import PerformancePredictor


class TestPerformancePredictor:
    """Test cases for PerformancePredictor"""

    def test_init(self):
        """Test predictor initialization"""
        predictor = PerformancePredictor()
        assert predictor.historical_predictions == []

    def test_predict_lap_time_no_sectors(self):
        """Test lap time prediction with no sectors"""
        predictor = PerformancePredictor()
        predicted = predictor.predict_lap_time([])
        assert predicted == 0.0

    def test_predict_lap_time_simple(self):
        """Test lap time prediction without historical data"""
        predictor = PerformancePredictor()
        predicted = predictor.predict_lap_time([28.5, 31.2])
        assert predicted > 0
        # Should estimate remaining sector based on average
        assert predicted > 28.5 + 31.2

    def test_predict_lap_time_with_history(self):
        """Test lap time prediction with historical data"""
        predictor = PerformancePredictor()
        historical = [
            {"sector_times": [28.5, 31.2, 25.8]},
            {"sector_times": [28.3, 31.5, 25.6]},
        ]
        predicted = predictor.predict_lap_time([28.4, 31.3], historical)
        assert predicted > 0
        assert predicted > 28.4 + 31.3

    def test_predict_pit_window_fuel_limited(self):
        """Test pit window prediction limited by fuel"""
        predictor = PerformancePredictor()
        laps, reason = predictor.predict_pit_window(3.0, 1.0, 50)
        assert laps > 0
        assert laps < 50
        assert reason == "combustible"

    def test_predict_pit_window_tire_limited(self):
        """Test pit window prediction limited by tires"""
        predictor = PerformancePredictor()
        laps, reason = predictor.predict_pit_window(1.0, 3.0, 50)
        assert laps > 0
        assert laps < 50
        assert reason == "pneumàtics"

    def test_estimate_tire_life(self):
        """Test tire life estimation"""
        predictor = PerformancePredictor()
        laps, confidence = predictor.estimate_tire_life(25.0, 5)
        assert laps > 0
        assert 0.0 <= confidence <= 1.0

    def test_estimate_tire_life_zero_wear(self):
        """Test tire life estimation with zero wear"""
        predictor = PerformancePredictor()
        laps, confidence = predictor.estimate_tire_life(0.0, 5)
        assert laps == 0
        assert confidence == 0.0

    def test_calculate_optimal_pace(self):
        """Test optimal pace calculation"""
        predictor = PerformancePredictor()
        pace = predictor.calculate_optimal_pace(5.0, 20, 55.0)
        assert pace > 0
        # Should be (55 - 5) / 20 = 2.5
        assert abs(pace - 2.5) < 0.01

    def test_calculate_optimal_pace_zero_laps(self):
        """Test optimal pace with zero laps remaining"""
        predictor = PerformancePredictor()
        pace = predictor.calculate_optimal_pace(5.0, 0, 55.0)
        assert pace == 0.0

    def test_predict_position_change(self):
        """Test position change prediction"""
        predictor = PerformancePredictor()
        competitors = [(1, 85.2), (2, 85.8), (3, 86.1)]
        prediction = predictor.predict_position_change(85.5, competitors, 10)

        assert "final_position" in prediction
        assert "changes" in prediction
        assert prediction["final_position"] is not None

    def test_predict_position_change_empty(self):
        """Test position change with no competitors"""
        predictor = PerformancePredictor()
        prediction = predictor.predict_position_change(85.5, [], 10)
        assert prediction["final_position"] is None

    def test_predict_with_linear_regression(self):
        """Test linear regression prediction"""
        predictor = PerformancePredictor()
        x_data = [1, 2, 3, 4, 5]
        y_data = [86.5, 86.2, 85.9, 85.7, 85.5]
        predicted = predictor.predict_with_linear_regression(x_data, y_data, 6)
        assert predicted > 0
        # Should continue the downward trend
        assert predicted < 85.5

    def test_predict_with_linear_regression_insufficient_data(self):
        """Test linear regression with insufficient data"""
        predictor = PerformancePredictor()
        predicted = predictor.predict_with_linear_regression([1], [85.5], 2)
        assert predicted == 0.0

    def test_predict_trend(self):
        """Test trend prediction"""
        predictor = PerformancePredictor()
        historical = [86.5, 86.2, 85.9, 85.7, 85.5]
        future = predictor.predict_trend(historical, 3)
        assert len(future) == 3
        assert all(isinstance(v, float) for v in future)

    def test_predict_trend_empty(self):
        """Test trend prediction with empty data"""
        predictor = PerformancePredictor()
        future = predictor.predict_trend([], 3)
        assert future == []

    def test_calculate_theoretical_best(self):
        """Test theoretical best calculation"""
        predictor = PerformancePredictor()
        laps = [
            [28.5, 31.2, 25.8],
            [28.3, 31.5, 25.6],
            [28.4, 31.0, 25.7],
        ]
        theoretical, best_sectors = predictor.calculate_theoretical_best(laps)
        assert theoretical > 0
        assert len(best_sectors) == 3
        assert best_sectors[0] == 28.3  # Best sector 1
        assert best_sectors[1] == 31.0  # Best sector 2
        assert best_sectors[2] == 25.6  # Best sector 3

    def test_calculate_theoretical_best_empty(self):
        """Test theoretical best with no laps"""
        predictor = PerformancePredictor()
        theoretical, best_sectors = predictor.calculate_theoretical_best([])
        assert theoretical == 0.0
        assert best_sectors == []

    def test_get_prediction_history(self):
        """Test getting prediction history"""
        predictor = PerformancePredictor()
        history = predictor.get_prediction_history()
        assert isinstance(history, list)
