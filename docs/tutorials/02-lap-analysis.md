# Tutorial 2: Lap Analysis

This tutorial will teach you how to compare laps, identify the best lap, find weak sectors, and visualize performance differences.

## Learning Objectives

By the end of this tutorial, you will know how to:

- ✅ Identify the best lap in a session
- ✅ Compare two or more laps
- ✅ Analyze sectors and find areas for improvement
- ✅ Visualize speed and racing line differences
- ✅ Generate analysis reports

## Prerequisites

- Tutorial 1 completed
- Data files from one or more sessions
- Basic knowledge of visualization with matplotlib/plotly

## Estimated Time

45-60 minutes

## Step 1: Load Session Data

Create a new script `lap_analysis.py`:

```python
"""
Lap Analysis
Tutorial for comparing and analyzing driving laps.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

from src.visualization import LapComparator, create_speed_vs_distance_plot
from src.utils import setup_logger

logger = setup_logger("lap_analysis", "INFO")


def load_session_data(filepath: str) -> List[Dict]:
    """
    Load session data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        List of telemetry records
    """
    logger.info(f"Loading data: {filepath}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    logger.info(f"✓ Loaded {len(data)} samples")
    return data
```

## Step 2: Identify Individual Laps

```python
def extract_laps(telemetry_data: List[Dict]) -> List[List[Dict]]:
    """
    Separate data into individual laps.
    
    Args:
        telemetry_data: Complete telemetry data
        
    Returns:
        List of laps, each lap is a list of samples
    """
    logger.info("Extracting individual laps...")
    
    laps = []
    current_lap = []
    last_lap_number = -1
    
    for sample in telemetry_data:
        # Detect lap change
        lap_number = sample.get('lap', 0)
        
        if lap_number != last_lap_number and current_lap:
            # New lap detected, save previous one
            laps.append(current_lap)
            current_lap = []
        
        current_lap.append(sample)
        last_lap_number = lap_number
    
    # Add last lap
    if current_lap:
        laps.append(current_lap)
    
    logger.info(f"✓ Found {len(laps)} laps")
    return laps


def calculate_lap_time(lap_data: List[Dict]) -> float:
    """
    Calculate the total time for a lap.
    
    Args:
        lap_data: Data from a lap
        
    Returns:
        Lap time in seconds
    """
    if not lap_data:
        return float('inf')
    
    # Look for completed lap record
    for sample in lap_data:
        if sample.get('type') == 'lap' and 'lap_time' in sample:
            return sample['lap_time']
    
    # If no record exists, calculate from timestamps
    if len(lap_data) >= 2:
        start_time = pd.to_datetime(lap_data[0]['timestamp'])
        end_time = pd.to_datetime(lap_data[-1]['timestamp'])
        return (end_time - start_time).total_seconds()
    
    return float('inf')
```

## Step 3: Find the Best Lap

```python
def find_best_lap(laps: List[List[Dict]]) -> Tuple[int, List[Dict], float]:
    """
    Identify the best (fastest) lap.
    
    Args:
        laps: List of laps
        
    Returns:
        Tuple (index, data, time) of the best lap
    """
    logger.info("Finding the best lap...")
    
    best_idx = 0
    best_time = float('inf')
    
    for idx, lap in enumerate(laps):
        lap_time = calculate_lap_time(lap)
        
        if lap_time < best_time:
            best_time = lap_time
            best_idx = idx
    
    logger.info(f"✓ Best lap: #{best_idx + 1} - Time: {best_time:.3f}s")
    return best_idx, laps[best_idx], best_time


def analyze_all_laps(laps: List[List[Dict]]) -> pd.DataFrame:
    """
    Analyze all laps and return statistics.
    
    Args:
        laps: List of laps
        
    Returns:
        DataFrame with statistics for each lap
    """
    stats = []
    
    for idx, lap in enumerate(laps):
        if not lap:
            continue
        
        lap_time = calculate_lap_time(lap)
        speeds = [s.get('speed', 0) for s in lap if 'speed' in s]
        rpms = [s.get('rpm', 0) for s in lap if 'rpm' in s]
        
        stats.append({
            'lap_number': idx + 1,
            'lap_time': lap_time,
            'max_speed': max(speeds) if speeds else 0,
            'avg_speed': np.mean(speeds) if speeds else 0,
            'min_speed': min(speeds) if speeds else 0,
            'max_rpm': max(rpms) if rpms else 0,
            'avg_rpm': np.mean(rpms) if rpms else 0,
            'samples': len(lap)
        })
    
    df = pd.DataFrame(stats)
    
    logger.info("\n📊 Lap Summary:")
    logger.info(df.to_string(index=False))
    
    return df
```

## Step 4: Compare Two Laps

```python
def compare_laps(lap1_data: List[Dict], lap2_data: List[Dict], 
                 lap1_name: str = "Lap 1", lap2_name: str = "Lap 2"):
    """
    Compare two laps and show the differences.
    
    Args:
        lap1_data: Data from the first lap
        lap2_data: Data from the second lap
        lap1_name: Name of the first lap
        lap2_name: Name of the second lap
    """
    logger.info(f"\n=== Comparing {lap1_name} vs {lap2_name} ===")
    
    # Lap times
    time1 = calculate_lap_time(lap1_data)
    time2 = calculate_lap_time(lap2_data)
    diff = time2 - time1
    
    logger.info(f"\n⏱️  Lap Time:")
    logger.info(f"   {lap1_name}: {time1:.3f}s")
    logger.info(f"   {lap2_name}: {time2:.3f}s")
    logger.info(f"   Difference: {abs(diff):.3f}s ({'+' if diff > 0 else ''}{diff:.3f}s)")
    
    # Speeds
    speeds1 = [s.get('speed', 0) for s in lap1_data if 'speed' in s]
    speeds2 = [s.get('speed', 0) for s in lap2_data if 'speed' in s]
    
    logger.info(f"\n🏎️  Speeds:")
    logger.info(f"   {lap1_name}:")
    logger.info(f"      • Maximum: {max(speeds1):.1f} km/h")
    logger.info(f"      • Average: {np.mean(speeds1):.1f} km/h")
    logger.info(f"      • Minimum: {min(speeds1):.1f} km/h")
    logger.info(f"   {lap2_name}:")
    logger.info(f"      • Maximum: {max(speeds2):.1f} km/h")
    logger.info(f"      • Average: {np.mean(speeds2):.1f} km/h")
    logger.info(f"      • Minimum: {min(speeds2):.1f} km/h")
    
    # RPM
    rpms1 = [s.get('rpm', 0) for s in lap1_data if 'rpm' in s]
    rpms2 = [s.get('rpm', 0) for s in lap2_data if 'rpm' in s]
    
    logger.info(f"\n🔧 RPM:")
    logger.info(f"   {lap1_name}: Max {max(rpms1)} | Avg {int(np.mean(rpms1))}")
    logger.info(f"   {lap2_name}: Max {max(rpms2)} | Avg {int(np.mean(rpms2))}")
```

## Step 5: Sector Analysis

```python
def analyze_sectors(lap_data: List[Dict], num_sectors: int = 3) -> List[Dict]:
    """
    Divide a lap into sectors and analyze each one.
    
    Args:
        lap_data: Lap data
        num_sectors: Number of sectors (default 3)
        
    Returns:
        List of statistics per sector
    """
    logger.info(f"\n=== Sector Analysis ({num_sectors} sectors) ===")
    
    sector_size = len(lap_data) // num_sectors
    sectors = []
    
    for i in range(num_sectors):
        start_idx = i * sector_size
        end_idx = start_idx + sector_size if i < num_sectors - 1 else len(lap_data)
        
        sector_data = lap_data[start_idx:end_idx]
        speeds = [s.get('speed', 0) for s in sector_data if 'speed' in s]
        
        # Calculate sector time
        if len(sector_data) >= 2:
            start_time = pd.to_datetime(sector_data[0]['timestamp'])
            end_time = pd.to_datetime(sector_data[-1]['timestamp'])
            sector_time = (end_time - start_time).total_seconds()
        else:
            sector_time = 0
        
        sector_stats = {
            'sector': i + 1,
            'time': sector_time,
            'max_speed': max(speeds) if speeds else 0,
            'avg_speed': np.mean(speeds) if speeds else 0,
            'samples': len(sector_data)
        }
        
        sectors.append(sector_stats)
        
        logger.info(f"\n📍 Sector {i + 1}:")
        logger.info(f"   • Time: {sector_time:.3f}s")
        logger.info(f"   • Maximum speed: {sector_stats['max_speed']:.1f} km/h")
        logger.info(f"   • Average speed: {sector_stats['avg_speed']:.1f} km/h")
    
    return sectors


def compare_sectors(lap1_data: List[Dict], lap2_data: List[Dict], 
                   num_sectors: int = 3):
    """
    Compare sectors between two laps.
    
    Args:
        lap1_data: Data from the first lap
        lap2_data: Data from the second lap
        num_sectors: Number of sectors
    """
    logger.info("\n=== Sector Comparison ===")
    
    sectors1 = analyze_sectors(lap1_data, num_sectors)
    sectors2 = analyze_sectors(lap2_data, num_sectors)
    
    logger.info("\n📊 Detailed Comparison:")
    
    for s1, s2 in zip(sectors1, sectors2):
        diff = s2['time'] - s1['time']
        logger.info(f"\nSector {s1['sector']}:")
        logger.info(f"   Lap 1: {s1['time']:.3f}s")
        logger.info(f"   Lap 2: {s2['time']:.3f}s")
        logger.info(f"   Difference: {abs(diff):.3f}s ({'+' if diff > 0 else ''}{diff:.3f}s)")
        
        if diff < -0.1:
            logger.info(f"   ✓ Lap 2 faster in this sector")
        elif diff > 0.1:
            logger.info(f"   ✗ Lap 2 slower in this sector")
        else:
            logger.info(f"   ≈ Similar time")
```

## Step 6: Comparison Visualization

```python
def visualize_lap_comparison(lap1_data: List[Dict], lap2_data: List[Dict],
                             output_file: str = "lap_comparison.html"):
    """
    Create interactive visualization for lap comparison.
    
    Args:
        lap1_data: Data from the first lap
        lap2_data: Data from the second lap
        output_file: HTML output file
    """
    logger.info(f"\n=== Creating Visualization ===")
    
    # Use the lap comparator
    comparator = LapComparator()
    comparator.add_lap("Best Lap", lap1_data)
    comparator.add_lap("Current Lap", lap2_data)
    
    # Create comparison plot
    fig = comparator.create_comparison_plot()
    
    # Save as interactive HTML
    fig.write_html(output_file)
    logger.info(f"✓ Visualization saved: {output_file}")
    logger.info(f"   Open with browser to view interactive comparison")


def create_speed_heatmap(lap_data: List[Dict], output_file: str = "speed_heatmap.html"):
    """
    Create a speed heatmap for the lap.
    
    Args:
        lap_data: Lap data
        output_file: Output file
    """
    import plotly.graph_objects as go
    
    # Extract positions and speeds
    positions_x = [s.get('pos_x', 0) for s in lap_data if 'pos_x' in s]
    positions_y = [s.get('pos_y', 0) for s in lap_data if 'pos_y' in s]
    speeds = [s.get('speed', 0) for s in lap_data if 'speed' in s]
    
    # Create plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=positions_x,
        y=positions_y,
        mode='markers+lines',
        marker=dict(
            size=6,
            color=speeds,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Speed (km/h)")
        ),
        line=dict(width=1, color='rgba(0,0,0,0.3)'),
        name='Racing Line'
    ))
    
    fig.update_layout(
        title="Track Speed Map",
        xaxis_title="Position X",
        yaxis_title="Position Y",
        hovermode='closest'
    )
    
    fig.write_html(output_file)
    logger.info(f"✓ Heatmap saved: {output_file}")
```

## Step 7: Complete Main Function

```python
def main():
    """Main function for lap analysis."""
    logger.info("=== Lap Analysis ===\n")
    
    # 1. Load data
    data_file = "data/session_20240115_143022.json"  # Adjust to your file
    
    if not Path(data_file).exists():
        logger.error(f"✗ File not found: {data_file}")
        logger.info("   Run Tutorial 1 first to generate data")
        return
    
    telemetry_data = load_session_data(data_file)
    
    # 2. Extract laps
    laps = extract_laps(telemetry_data)
    
    if len(laps) < 2:
        logger.warning("⚠️  At least 2 laps are needed for comparison")
        return
    
    # 3. Analyze all laps
    lap_stats = analyze_all_laps(laps)
    
    # 4. Find the best lap
    best_idx, best_lap, best_time = find_best_lap(laps)
    
    # 5. Compare best lap with last lap
    last_lap = laps[-1]
    compare_laps(best_lap, last_lap, 
                f"Best Lap #{best_idx + 1}",
                f"Last Lap #{len(laps)}")
    
    # 6. Sector analysis
    compare_sectors(best_lap, last_lap, num_sectors=3)
    
    # 7. Visualizations
    visualize_lap_comparison(best_lap, last_lap, "comparison.html")
    create_speed_heatmap(best_lap, "best_lap_heatmap.html")
    
    logger.info("\n✓ Analysis completed!")
    logger.info("\n📁 Generated files:")
    logger.info("   • comparison.html - Interactive comparison")
    logger.info("   • best_lap_heatmap.html - Speed map")


if __name__ == "__main__":
    main()
```

## Run the Analysis

```bash
python lap_analysis.py
```

## Expected Output

```
INFO - === Lap Analysis ===
INFO - Loading data: data/session_20240115_143022.json
INFO - ✓ Loaded 3000 samples
INFO - Extracting individual laps...
INFO - ✓ Found 5 laps
INFO - 
📊 Lap Summary:
 lap_number  lap_time  max_speed  avg_speed  min_speed  max_rpm  avg_rpm  samples
          1     95.34      198.5      142.3       45.2     7800     5234      612
          2     93.12      201.3      145.8       42.1     7900     5412      598
          3     94.56      199.7      143.9       43.5     7850     5298      605
          4     92.87      203.1      147.2       41.8     8000     5456      591
          5     93.45      200.8      144.6       42.9     7920     5387      594

INFO - Finding the best lap...
INFO - ✓ Best lap: #4 - Time: 92.870s

INFO - === Comparing Best Lap #4 vs Last Lap #5 ===
INFO - 
⏱️  Lap Time:
   Best Lap #4: 92.870s
   Last Lap #5: 93.450s
   Difference: 0.580s (+0.580s)
...
INFO - ✓ Analysis completed!
```

## Practical Exercises

### Exercise 1: Consistency Analysis

Create a function that calculates driver consistency based on the standard deviation of lap times.

<details>
<summary>View solution</summary>

```python
def calculate_consistency(laps: List[List[Dict]]) -> Dict:
    """Calculate driver consistency."""
    lap_times = [calculate_lap_time(lap) for lap in laps]
    lap_times = [t for t in lap_times if t != float('inf')]
    
    if not lap_times:
        return {}
    
    return {
        'mean': np.mean(lap_times),
        'std': np.std(lap_times),
        'min': min(lap_times),
        'max': max(lap_times),
        'range': max(lap_times) - min(lap_times),
        'consistency_score': 100 * (1 - np.std(lap_times) / np.mean(lap_times))
    }
```
</details>

### Exercise 2: Identify Time Loss Zones

Create a function that automatically identifies where the most time is lost compared to the best lap.

### Exercise 3: Multiple Lap Comparison

Extend the code to compare 3 or more laps simultaneously.

## Professional Tips

### 💡 Tip 1: Focus on Sectors
Sectors are key to identifying areas for improvement. Practice sector by sector.

### 💡 Tip 2: Consistency vs Speed
A consistent lap is better than fast but inconsistent laps.

### 💡 Tip 3: External Reference
Compare with laps from faster drivers to identify differences in racing line and speeds.

### 💡 Tip 4: Multi-Session Data
Compare laps from different sessions to see progression over time.

## Next Steps

1. **[Tutorial 3: Real-Time Dashboard](03-real-time-dashboard.md)** - Real-time visualization
2. **[Tutorial 4: Advanced Analysis](04-advanced-analysis.md)** - Advanced techniques
3. **[Use Case: Driver Coaching](../use-cases/driver-coaching.md)** - Practical application

## Resources

- [LapComparator Documentation](../api_reference.md#lapcomparator)
- [Advanced Visualization](../visualization.md)
- [Telemetry Analysis](../analysis_module.md)

---

Now you can analyze laps like a professional! 🏆
