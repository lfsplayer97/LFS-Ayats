# Real-Time Analysis Module

Advanced analysis module for LFS-Ayats with anomaly detection, performance prediction, and sector analysis capabilities.

## 📋 Features

### 🔍 Anomaly Detection (`anomaly.py`)
- **Engine overheating**: Detection with WARNING and CRITICAL levels
- **Wheel spin**: Linear speed vs rotational speed comparison
- **Understeer/Oversteer**: Steering behavior analysis
- **Flat spots**: Irregular tire wear detection
- **Inconsistent braking**: Braking point variability analysis
- **Fuel warning**: Insufficient fuel prediction
- **Statistical methods**: Z-score, IQR, moving averages

### 📊 Performance Prediction (`predictor.py`)
- **Lap time**: Prediction based on completed sectors
- **Pit stop window**: Optimal calculation based on fuel and tires
- **Tire lifespan**: Remaining laps estimation
- **Optimal pace**: Fuel management to finish exactly
- **Position changes**: Prediction based on competitor pace
- **Theoretical best time**: Combination of best sectors

### 📏 Sector Analysis (`sectors.py`)
- **Sector comparison**: Between different laps
- **Weak sectors**: Identification of improvement areas
- **Consistency**: Calculation for each sector
- **Optimal line**: Based on fast laps
- **Braking points**: Analysis and consistency
- **Throttle application**: Analysis per corner

### 🔄 Advanced Comparator (`comparator.py`)
- **Complete comparison**: Between two laps
- **Point-to-point delta**: Time gained/lost
- **Speed traces**: Detailed comparison
- **Racing lines**: Trajectory differences
- **Suggestions**: Automatic improvement recommendations

### 🔔 Alert System (`alerts.py`)
- **Multiple handlers**: Console, Log, custom Callback
- **Filtering**: Avoid duplicates with minimum intervals
- **History**: With statistics and search
- **Automatic conditions**: Telemetry verification

### 📐 Metrics Calculation (`metrics.py`)
- **Consistency**: Measure of time regularity
- **Pace score**: Comparison with reference
- **Improvement rate**: Evolution during session
- **Racecraft**: Racing skill evaluation
- **Efficiency**: Fuel and degradation
- **Composite indices**: Combination of multiple metrics

## 🚀 Installation

The module is included in LFS-Ayats. Make sure you have the dependencies installed:

```bash
pip install -r requirements.txt
pip install -e .
```

## 💡 Usage Examples

### Example 1: Anomaly Detection

```python
from src.analysis import AnomalyDetector

# Create detector
detector = AnomalyDetector()

# Check telemetry
current_data = {
    "engine_temp": 102.0,
    "linear_speed": 50.0,
    "wheel_speed": 60.0,
}

alerts = detector.check_telemetry(current_data)
for alert in alerts:
    print(alert)
```

### Example 2: Lap Time Prediction

```python
from src.analysis import PerformancePredictor

# Create predictor
predictor = PerformancePredictor()

# Historical data
historical_data = [
    {"sector_times": [28.5, 31.2, 25.8]},
    {"sector_times": [28.3, 31.5, 25.6]},
]

# Predict time with 2 completed sectors
predicted_time = predictor.predict_lap_time(
    current_sector_times=[28.2, 31.0],
    historical_data=historical_data
)

print(f"Predicted time: {predicted_time:.3f}s")
```

### Example 3: Sector Analysis

```python
from src.analysis import SectorAnalyzer

# Create analyzer
analyzer = SectorAnalyzer()

# Multiple laps data
session_data = [
    {"sector_times": [28.5, 31.2, 25.8]},
    {"sector_times": [28.3, 31.5, 25.6]},
    {"sector_times": [28.4, 31.8, 25.7]},
]

# Identify weak sectors
weak_sectors = analyzer.identify_weak_sectors(session_data)
for sector in weak_sectors:
    print(f"Sector {sector.number}: losing {sector.time_lost:.3f}s")
```

### Example 4: Alert System

```python
from src.analysis import AlertSystem, AlertLevel
from src.analysis.alerts import ConsoleAlertHandler

# Create system
system = AlertSystem()
system.register_handler(ConsoleAlertHandler())

# Generate alert
system.create_and_trigger(
    AlertLevel.WARNING,
    "High temperature",
    {"temp": 98.0}
)

# Check conditions
telemetry = {"engine_temp": 110.0, "fuel": 4.0}
alerts = system.check_conditions(telemetry)
```

### Example 5: Lap Comparison

```python
from src.analysis import AdvancedComparator

# Create comparator
comparator = AdvancedComparator()

# Lap data
lap1 = {
    "lap_id": 5,
    "total_time": 85.5,
    "sector_times": [28.5, 31.2, 25.8]
}

lap2 = {
    "lap_id": 8,
    "total_time": 85.2,
    "sector_times": [28.3, 31.5, 25.4]
}

# Compare
comparison = comparator.compare_laps(lap1, lap2)
print(f"Difference: {comparison.time_difference:+.3f}s")

for suggestion in comparison.suggestions:
    print(f"• {suggestion}")
```

### Example 6: Performance Metrics

```python
from src.analysis import MetricsCalculator

# Create calculator
calculator = MetricsCalculator()

# Lap times
lap_times = [86.5, 86.2, 85.9, 85.7, 85.5]
reference = 85.0

# Calculate metrics
consistency = calculator.calculate_consistency(lap_times)
pace_score = calculator.calculate_pace_score(lap_times, reference)
performance = calculator.calculate_performance_index(lap_times, reference)

print(f"Consistency: {consistency:.1%}")
print(f"Pace: {pace_score:.1f}/100")
print(f"Performance: {performance:.1f}/100")
```

## 📚 Running Complete Examples

```bash
cd /path/to/LFS-Ayats
PYTHONPATH=. python3 examples/analysis_examples.py
```

## 🧪 Tests

The module includes 69 unit tests with complete coverage:

```bash
# Run module tests
pytest tests/unit/analysis/ -v

# With coverage
pytest tests/unit/analysis/ --cov=src/analysis --cov-report=html
```

## 📖 API Documentation

### Main Classes

#### `AnomalyDetector`
```python
detector = AnomalyDetector(
    temp_warning=95.0,      # Warning temperature (°C)
    temp_critical=105.0,    # Critical temperature (°C)
    z_score_threshold=3.0   # Threshold for outlier detection
)
```

**Main methods:**
- `detect_overheating(engine_temp)` → (bool, Alert)
- `detect_wheel_spin(linear_speed, wheel_speed)` → (bool, Alert)
- `detect_understeer(steering_angle, actual_rotation)` → (bool, Alert)
- `detect_fuel_warning(fuel_level, fuel_per_lap, laps_remaining)` → (bool, Alert)
- `detect_outliers_zscore(data, threshold)` → List[int]
- `check_telemetry(telemetry_data)` → List[Alert]

#### `PerformancePredictor`
```python
predictor = PerformancePredictor()
```

**Main methods:**
- `predict_lap_time(current_sector_times, historical_data)` → float
- `predict_pit_window(fuel_consumption, tire_wear, laps_remaining)` → (int, str)
- `estimate_tire_life(current_wear, laps_completed)` → (int, float)
- `calculate_optimal_pace(fuel_target, laps_remaining, current_fuel)` → float
- `calculate_theoretical_best(sector_times_per_lap)` → (float, List[float])

#### `SectorAnalyzer`
```python
analyzer = SectorAnalyzer()
```

**Main methods:**
- `compare_sector_times(lap_data, reference_lap_data)` → List[Dict]
- `identify_weak_sectors(session_data)` → List[Sector]
- `calculate_sector_consistency(laps)` → Dict[int, float]
- `analyze_braking_points(laps)` → List[BrakingPoint]

#### `AdvancedComparator`
```python
comparator = AdvancedComparator()
```

**Main methods:**
- `compare_laps(lap1_data, lap2_data)` → LapComparison
- `calculate_time_delta(lap1_data, lap2_data)` → TimeDelta
- `find_performance_differences(lap1, lap2)` → List[Dict]

#### `AlertSystem`
```python
system = AlertSystem(
    max_history=1000,       # Maximum alerts in history
    enable_filtering=True   # Duplicate filtering
)
```

**Main methods:**
- `register_handler(handler)` → None
- `trigger_alert(alert, min_interval)` → bool
- `create_and_trigger(level, message, data, min_interval)` → bool
- `check_conditions(telemetry_data)` → List[Alert]
- `get_history(level, limit)` → List[Alert]

#### `MetricsCalculator`
```python
calculator = MetricsCalculator()
```

**Main methods:**
- `calculate_consistency(lap_times)` → float
- `calculate_pace_score(lap_times, reference_time)` → float
- `calculate_improvement_rate(lap_times)` → float
- `calculate_performance_index(lap_times, reference_time)` → float
- `calculate_percentile_rank(value, dataset)` → float

## 🔧 Data Models

### `Alert`
```python
@dataclass
class Alert:
    level: AlertLevel          # INFO, WARNING, ERROR, CRITICAL
    message: str
    timestamp: float
    data: Dict[str, Any]
```

### `SectorComparison`
```python
@dataclass
class SectorComparison:
    sector_number: int
    lap1_time: float
    lap2_time: float
    difference: float
    percentage_diff: float
```

### `LapComparison`
```python
@dataclass
class LapComparison:
    lap1_id: int
    lap2_id: int
    time_difference: float
    sector_comparisons: List[SectorComparison]
    speed_trace_comparison: Dict[str, Any]
    racing_line_difference: float
    suggestions: List[str]
```

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## 📝 License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for more details.

## 🙏 Credits

Developed as part of the LFS-Ayats project to provide advanced telemetry analysis for Live for Speed.
