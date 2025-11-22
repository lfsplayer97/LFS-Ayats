# Tutorial 4: Advanced Analysis

This tutorial covers advanced telemetry analysis techniques: anomaly detection, lap time prediction, and racing line optimization.

## Objectives

- ✅ Detect anomalies in driving
- ✅ Predict lap times
- ✅ Identify optimization points
- ✅ Generate automated reports

## Prerequisites

- Previous tutorials completed
- Knowledge of pandas and numpy
- Data from multiple sessions

## Estimated Time: 60 minutes

## Step 1: Anomaly Detection

```python
"""
Advanced Telemetry Analysis
Anomaly detection and predictions.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Tuple

from src.analysis import TelemetryAnalyzer
from src.utils import setup_logger

logger = setup_logger("advanced_analysis", "INFO")


def detect_anomalies(telemetry_data: pd.DataFrame, 
                    contamination: float = 0.05) -> pd.DataFrame:
    """
    Detects anomalies in telemetry data.
    
    Args:
        telemetry_data: DataFrame with data
        contamination: Expected proportion of anomalies (0-1)
        
    Returns:
        DataFrame with 'anomaly' column (-1 = anomaly, 1 = normal)
    """
    logger.info("Detecting anomalies...")
    
    # Select features
    features = ['speed', 'rpm', 'throttle', 'brake']
    X = telemetry_data[features].fillna(0)
    
    # Isolation Forest model
    model = IsolationForest(contamination=contamination, random_state=42)
    telemetry_data['anomaly'] = model.fit_predict(X)
    
    anomaly_count = (telemetry_data['anomaly'] == -1).sum()
    logger.info(f"✓ Found {anomaly_count} anomalies ({anomaly_count/len(telemetry_data)*100:.1f}%)")
    
    return telemetry_data


def analyze_anomalies(telemetry_data: pd.DataFrame):
    """Analyzes detected anomalies."""
    anomalies = telemetry_data[telemetry_data['anomaly'] == -1]
    
    if len(anomalies) == 0:
        logger.info("No anomalies found")
        return
    
    logger.info(f"\n=== Anomaly Analysis ===")
    logger.info(f"Total anomalies: {len(anomalies)}")
    logger.info(f"\nAnomaly statistics:")
    logger.info(anomalies[['speed', 'rpm', 'throttle', 'brake']].describe())
```

## Step 2: Lap Time Prediction

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def prepare_lap_features(laps_data: List[Dict]) -> pd.DataFrame:
    """
    Prepares features for lap time prediction.
    
    Args:
        laps_data: List of laps with data
        
    Returns:
        DataFrame with features
    """
    features = []
    
    for lap in laps_data:
        if not lap:
            continue
        
        speeds = [s.get('speed', 0) for s in lap if 'speed' in s]
        rpms = [s.get('rpm', 0) for s in lap if 'rpm' in s]
        
        features.append({
            'avg_speed': np.mean(speeds),
            'max_speed': max(speeds) if speeds else 0,
            'min_speed': min(speeds) if speeds else 0,
            'speed_std': np.std(speeds),
            'avg_rpm': np.mean(rpms),
            'max_rpm': max(rpms) if rpms else 0,
            'lap_time': calculate_lap_time(lap)
        })
    
    return pd.DataFrame(features)


def train_lap_predictor(laps_data: List[Dict]) -> LinearRegression:
    """
    Trains model to predict lap times.
    
    Args:
        laps_data: Training data
        
    Returns:
        Trained model
    """
    logger.info("Training prediction model...")
    
    df = prepare_lap_features(laps_data)
    
    # Separate features and target
    X = df[['avg_speed', 'max_speed', 'speed_std', 'avg_rpm']]
    y = df['lap_time']
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    logger.info(f"✓ Model trained")
    logger.info(f"   Train R²: {train_score:.3f}")
    logger.info(f"   Test R²: {test_score:.3f}")
    
    return model


def predict_lap_time(model: LinearRegression, 
                    avg_speed: float, 
                    max_speed: float,
                    speed_std: float,
                    avg_rpm: float) -> float:
    """Predicts lap time based on features."""
    features = np.array([[avg_speed, max_speed, speed_std, avg_rpm]])
    predicted_time = model.predict(features)[0]
    return predicted_time
```

## Step 3: Racing Line Optimization

```python
def find_optimal_racing_line(telemetry_data: pd.DataFrame,
                            speed_threshold: float = 150.0) -> pd.DataFrame:
    """
    Identifies optimal racing line based on speed.
    
    Args:
        telemetry_data: Telemetry data
        speed_threshold: Minimum speed to consider optimal
        
    Returns:
        DataFrame with optimal segments
    """
    logger.info("Searching for optimal racing line...")
    
    # Filter by high speed
    optimal_segments = telemetry_data[telemetry_data['speed'] >= speed_threshold]
    
    logger.info(f"✓ Found {len(optimal_segments)} optimal points")
    
    return optimal_segments


def calculate_corner_speeds(telemetry_data: pd.DataFrame,
                           corner_threshold: float = 100.0) -> List[Dict]:
    """
    Analyzes speeds in corners (low speed zones).
    
    Args:
        telemetry_data: Telemetry data
        corner_threshold: Maximum speed to consider a corner
        
    Returns:
        List of corners with statistics
    """
    logger.info("Analyzing corner speeds...")
    
    corners = []
    in_corner = False
    corner_data = []
    
    for idx, row in telemetry_data.iterrows():
        speed = row['speed']
        
        if speed < corner_threshold:
            in_corner = True
            corner_data.append(row)
        elif in_corner and speed >= corner_threshold:
            # End of corner
            if len(corner_data) > 5:  # Minimum 5 points
                corners.append({
                    'entry_speed': corner_data[0]['speed'],
                    'min_speed': min(c['speed'] for c in corner_data),
                    'exit_speed': corner_data[-1]['speed'],
                    'avg_speed': np.mean([c['speed'] for c in corner_data]),
                    'length': len(corner_data)
                })
            corner_data = []
            in_corner = False
    
    logger.info(f"✓ Identified {len(corners)} corners")
    
    return corners
```

## Step 4: Report Generation

```python
def generate_analysis_report(telemetry_data: pd.DataFrame,
                            laps_data: List[Dict],
                            output_file: str = "analysis_report.html"):
    """
    Generates complete HTML analysis report.
    
    Args:
        telemetry_data: Telemetry data
        laps_data: Lap data
        output_file: Output file
    """
    logger.info("Generating analysis report...")
    
    # Detect anomalies
    telemetry_data = detect_anomalies(telemetry_data)
    
    # Train predictor
    model = train_lap_predictor(laps_data)
    
    # Analyze corners
    corners = calculate_corner_speeds(telemetry_data)
    
    # Create HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Advanced Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            .stat {{ background: #ecf0f1; padding: 15px; margin: 10px 0; }}
            .warning {{ color: #e74c3c; }}
            .success {{ color: #2ecc71; }}
        </style>
    </head>
    <body>
        <h1>Advanced Telemetry Analysis Report</h1>
        
        <h2>General Summary</h2>
        <div class="stat">
            <p><strong>Total samples:</strong> {len(telemetry_data)}</p>
            <p><strong>Total laps:</strong> {len(laps_data)}</p>
            <p><strong>Anomalies detected:</strong> {(telemetry_data['anomaly'] == -1).sum()}</p>
        </div>
        
        <h2>Corner Analysis</h2>
        <div class="stat">
            <p><strong>Corners identified:</strong> {len(corners)}</p>
            <p><strong>Average corner speed:</strong> 
               {np.mean([c['avg_speed'] for c in corners]):.1f} km/h</p>
        </div>
        
        <h2>Predictions</h2>
        <div class="stat">
            <p>Prediction model trained with {len(laps_data)} laps</p>
            <p>Use the model to predict future lap times</p>
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"✓ Report saved: {output_file}")
```

## Step 5: Main Function

```python
def main():
    """Main advanced analysis function."""
    logger.info("=== Advanced Telemetry Analysis ===\n")
    
    # Load data
    df = pd.read_csv("data/session_20240115_143022.csv")
    laps = extract_laps_from_dataframe(df)
    
    # 1. Anomaly detection
    df = detect_anomalies(df)
    analyze_anomalies(df)
    
    # 2. Lap time prediction
    model = train_lap_predictor(laps)
    
    # Predict next lap time
    next_lap_time = predict_lap_time(
        model, 
        avg_speed=145.0, 
        max_speed=200.0,
        speed_std=35.0,
        avg_rpm=5500
    )
    logger.info(f"\n🔮 Prediction for next lap: {next_lap_time:.2f}s")
    
    # 3. Racing line optimization
    optimal_line = find_optimal_racing_line(df, speed_threshold=150.0)
    corners = calculate_corner_speeds(df)
    
    # 4. Generate report
    generate_analysis_report(df, laps, "advanced_analysis_report.html")
    
    logger.info("\n✓ Advanced analysis completed!")


if __name__ == "__main__":
    main()
```

## Exercises

1. **Model Improvement**: Add more features (throttle, brake, gear)
2. **Clustering**: Group similar laps with K-means
3. **Temporal Analysis**: Detect trends over time

## Tips

- You need multiple sessions for accurate models
- Normalize features for better results
- Validate models with unseen data

## Resources

- [scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas User Guide](https://pandas.pydata.org/)
- [Analysis Documentation](../analysis_module.md)

---

You now master advanced analysis! 🎓
