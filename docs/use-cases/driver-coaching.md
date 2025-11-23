# Use Case: Driver Coaching

Guide for using LFS-Ayats as a training and driver performance improvement tool.

## Scenario

**Racing School** offers personalized training to drivers who want to improve their performance. They need to:
- Analyze each student's driving technique
- Compare with reference drivers (coaches)
- Identify specific areas for improvement
- Track progression over time
- Provide data-driven feedback

## Coaching Objectives

1. **Consistency Analysis**: Identify lap time variability
2. **Racing Line Optimization**: Improve racing line
3. **Tire Management**: Analyze tire degradation
4. **Braking Efficiency**: Optimize braking points and intensity
5. **Power Utilization**: Maximize traction on corner exits

## Coaching Workflow

```
1. Initial Session (Baseline)
   ↓
2. Data Collection
   ↓
3. Automatic Analysis
   ↓
4. Reference Comparison
   ↓
5. Improvement Areas Identification
   ↓
6. Driver Feedback
   ↓
7. Practice Sessions
   ↓
8. Progress Tracking
```

## Step 1: Configure Training Session

`coaching_session.py`:
```python
"""
Coaching system with LFS-Ayats.
Analyzes performance and provides feedback.
"""

from typing import List, Dict
import numpy as np
from pathlib import Path

from src.connection import InSimClient
from src.telemetry import TelemetryCollector
from src.analysis import TelemetryAnalyzer
from src.visualization import LapComparator, create_track_map
from src.utils import setup_logger

logger = setup_logger("coaching", "INFO")


class CoachingSession:
    """Manages coaching session."""
    
    def __init__(self, student_name: str, coach_name: str = None):
        """
        Initialize session.
        
        Args:
            student_name: Student's name
            coach_name: Coach's name (for comparison)
        """
        self.student_name = student_name
        self.coach_name = coach_name
        self.student_laps = []
        self.coach_laps = []
        self.analyzer = TelemetryAnalyzer()
    
    def collect_baseline(self, num_laps: int = 10):
        """
        Collect student's baseline laps.
        
        Args:
            num_laps: Number of laps to collect
        """
        logger.info(f"📊 Collecting {num_laps} baseline laps from {self.student_name}...")
        
        client = InSimClient(host="127.0.0.1", port=29999)
        client.connect()
        client.initialize()
        
        collector = TelemetryCollector(client)
        
        lap_count = 0
        
        def on_lap(lap_data):
            nonlocal lap_count
            if lap_data['player_name'] == self.student_name:
                self.student_laps.append(lap_data)
                lap_count += 1
                logger.info(f"   Lap {lap_count}/{num_laps}: {lap_data['lap_time']:.3f}s")
        
        collector.register_callback('lap', on_lap)
        collector.start()
        
        # Wait until all laps are collected
        import time
        while lap_count < num_laps:
            time.sleep(1)
        
        collector.stop()
        client.disconnect()
        
        logger.info(f"✓ Baseline completed: {len(self.student_laps)} laps")
    
    def analyze_consistency(self) -> Dict:
        """
        Analyze student's consistency.
        
        Returns:
            Dictionary with consistency metrics
        """
        logger.info("\n=== Consistency Analysis ===")
        
        lap_times = [lap['lap_time'] for lap in self.student_laps]
        
        if not lap_times:
            return {}
        
        mean_time = np.mean(lap_times)
        std_dev = np.std(lap_times)
        best_time = min(lap_times)
        worst_time = max(lap_times)
        consistency_score = 100 * (1 - std_dev / mean_time)
        
        results = {
            'mean': mean_time,
            'std_dev': std_dev,
            'best': best_time,
            'worst': worst_time,
            'range': worst_time - best_time,
            'consistency_score': consistency_score
        }
        
        logger.info(f"   Average: {mean_time:.3f}s")
        logger.info(f"   Std Dev: {std_dev:.3f}s")
        logger.info(f"   Best: {best_time:.3f}s")
        logger.info(f"   Worst: {worst_time:.3f}s")
        logger.info(f"   Consistency: {consistency_score:.1f}/100")
        
        # Feedback
        if consistency_score >= 98:
            logger.info("   ✓ Excellent consistency!")
        elif consistency_score >= 95:
            logger.info("   ✓ Good consistency")
        elif consistency_score >= 90:
            logger.info("   ⚠️  Room for improvement - focus on reproducing best lap")
        else:
            logger.info("   ❌ Inconsistent - practice more to stabilize")
        
        return results
    
    def compare_with_coach(self):
        """Compare student's best lap with coach."""
        if not self.coach_laps:
            logger.warning("No coach data available for comparison")
            return
        
        logger.info(f"\n=== Comparison with {self.coach_name} ===")
        
        # Best lap from each
        student_best = min(self.student_laps, key=lambda l: l['lap_time'])
        coach_best = min(self.coach_laps, key=lambda l: l['lap_time'])
        
        time_diff = student_best['lap_time'] - coach_best['lap_time']
        
        logger.info(f"   {self.student_name}: {student_best['lap_time']:.3f}s")
        logger.info(f"   {self.coach_name}: {coach_best['lap_time']:.3f}s")
        logger.info(f"   Difference: {time_diff:+.3f}s")
        
        # Visual comparison
        comparator = LapComparator()
        comparator.add_lap(self.student_name, student_best['telemetry'])
        comparator.add_lap(f"{self.coach_name} (ref)", coach_best['telemetry'])
        
        fig = comparator.create_comparison_plot()
        fig.write_html(f"comparison_{self.student_name}.html")
        
        logger.info(f"   📊 Comparison saved: comparison_{self.student_name}.html")
        
        # Sector-by-sector analysis
        self._analyze_sectors(student_best, coach_best)
    
    def _analyze_sectors(self, student_lap, coach_lap, num_sectors=3):
        """Analyze sectors comparing student and coach."""
        logger.info(f"\n📍 Sector Analysis ({num_sectors} sectors):")
        
        student_sectors = self._split_into_sectors(
            student_lap['telemetry'], 
            num_sectors
        )
        coach_sectors = self._split_into_sectors(
            coach_lap['telemetry'],
            num_sectors
        )
        
        weakest_sectors = []
        
        for i in range(num_sectors):
            student_time = self._calculate_sector_time(student_sectors[i])
            coach_time = self._calculate_sector_time(coach_sectors[i])
            diff = student_time - coach_time
            
            logger.info(f"\n   Sector {i+1}:")
            logger.info(f"      Student: {student_time:.3f}s")
            logger.info(f"      Coach: {coach_time:.3f}s")
            logger.info(f"      Difference: {diff:+.3f}s")
            
            if diff > 0.1:  # Loses more than 0.1s
                weakest_sectors.append((i+1, diff))
                logger.info(f"      ⚠️  IMPROVEMENT AREA")
        
        return weakest_sectors
    
    def _split_into_sectors(self, telemetry, num_sectors):
        """Split telemetry into sectors."""
        sector_size = len(telemetry) // num_sectors
        sectors = []
        
        for i in range(num_sectors):
            start = i * sector_size
            end = start + sector_size if i < num_sectors - 1 else len(telemetry)
            sectors.append(telemetry[start:end])
        
        return sectors
    
    def _calculate_sector_time(self, sector_data):
        """Calculate sector time."""
        if len(sector_data) < 2:
            return 0
        
        from datetime import datetime
        start_time = datetime.fromisoformat(sector_data[0]['timestamp'])
        end_time = datetime.fromisoformat(sector_data[-1]['timestamp'])
        
        return (end_time - start_time).total_seconds()
    
    def identify_improvement_areas(self) -> List[str]:
        """
        Identify specific areas for improvement.
        
        Returns:
            List of recommendations
        """
        logger.info("\n=== Improvement Areas ===")
        
        recommendations = []
        
        # Analyze best lap
        best_lap = min(self.student_laps, key=lambda l: l['lap_time'])
        telemetry = best_lap['telemetry']
        
        # 1. Minimum corner speed
        speeds = [t['speed'] for t in telemetry]
        min_speed = min(speeds)
        
        if min_speed < 60:
            rec = "Low minimum corner speed - improve entry and line"
            recommendations.append(rec)
            logger.info(f"   • {rec}")
        
        # 2. Gear usage
        gears = [t.get('gear', 0) for t in telemetry]
        gear_changes = sum(1 for i in range(1, len(gears)) if gears[i] != gears[i-1])
        
        if gear_changes > 50:  # Too many changes
            rec = "Excessive gear changes - smooth out driving"
            recommendations.append(rec)
            logger.info(f"   • {rec}")
        
        # 3. Speed variability
        speed_std = np.std(speeds)
        if speed_std > 40:
            rec = "High speed variability - maintain more consistent pace"
            recommendations.append(rec)
            logger.info(f"   • {rec}")
        
        # 4. Excessive RPM
        rpms = [t.get('rpm', 0) for t in telemetry]
        max_rpm = max(rpms)
        if max_rpm > 7800:
            rec = "RPM too high - shift earlier to preserve engine"
            recommendations.append(rec)
            logger.info(f"   • {rec}")
        
        if not recommendations:
            logger.info("   ✓ No major issues detected!")
            recommendations.append("Continue practicing to improve consistency")
        
        return recommendations
    
    def generate_coaching_report(self, output_file: str = None):
        """Generate complete coaching report."""
        if output_file is None:
            output_file = f"coaching_report_{self.student_name}.html"
        
        logger.info(f"\n=== Generating Coaching Report ===")
        
        # Collect all analyses
        consistency = self.analyze_consistency()
        improvements = self.identify_improvement_areas()
        
        # Generate HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Coaching Report - {self.student_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; }}
                .metric {{ background: #ecf0f1; padding: 15px; margin: 10px 0; }}
                .good {{ color: #2ecc71; }}
                .warning {{ color: #f39c12; }}
                .bad {{ color: #e74c3c; }}
                ul {{ list-style-type: none; padding-left: 0; }}
                li {{ padding: 8px; margin: 5px 0; background: #f8f9fa; }}
            </style>
        </head>
        <body>
            <h1>Coaching Report: {self.student_name}</h1>
            
            <h2>Consistency</h2>
            <div class="metric">
                <p><strong>Average time:</strong> {consistency.get('mean', 0):.3f}s</p>
                <p><strong>Best lap:</strong> {consistency.get('best', 0):.3f}s</p>
                <p><strong>Worst lap:</strong> {consistency.get('worst', 0):.3f}s</p>
                <p><strong>Consistency score:</strong> 
                   <span class="{'good' if consistency.get('consistency_score', 0) >= 95 else 'warning'}">
                       {consistency.get('consistency_score', 0):.1f}/100
                   </span>
                </p>
            </div>
            
            <h2>Improvement Areas</h2>
            <ul>
                {''.join(f'<li>• {rec}</li>' for rec in improvements)}
            </ul>
            
            <h2>Next Steps</h2>
            <ol>
                <li>Focus on identified weak sectors</li>
                <li>Practice 10-15 more laps focusing on consistency</li>
                <li>Review comparison with reference lap</li>
                <li>Next session: Progress review</li>
            </ol>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"✓ Report saved: {output_file}")
        logger.info(f"   Open with browser to view full details")


def main():
    """Example usage of coaching system."""
    # Create session
    session = CoachingSession(
        student_name="Student1",
        coach_name="Coach_Pro"
    )
    
    # Collect data
    logger.info("Start driving on the track...")
    session.collect_baseline(num_laps=10)
    
    # Analysis
    session.analyze_consistency()
    session.identify_improvement_areas()
    
    # If you have coach data, compare
    # session.compare_with_coach()
    
    # Generate report
    session.generate_coaching_report()
    
    logger.info("\n✓ Coaching session completed!")


if __name__ == "__main__":
    main()
```

## Step 2: Progress Tracking

`track_progress.py`:
```python
"""
Track a driver's progression over time.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def track_progress(student_name: str):
    """Show student's progression."""
    # Load historical sessions
    sessions = load_student_sessions(student_name)
    
    # Extract best lap time per session
    progress_data = []
    for session in sessions:
        date = session['date']
        best_lap = min(lap['time'] for lap in session['laps'])
        consistency = session['consistency_score']
        
        progress_data.append({
            'date': date,
            'best_lap': best_lap,
            'consistency': consistency
        })
    
    df = pd.DataFrame(progress_data)
    
    # Progress chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Best lap time
    ax1.plot(df['date'], df['best_lap'], marker='o')
    ax1.set_title(f'{student_name} Progression')
    ax1.set_ylabel('Best Time (s)')
    ax1.grid(True)
    
    # Consistency
    ax2.plot(df['date'], df['consistency'], marker='o', color='green')
    ax2.set_ylabel('Consistency (%)')
    ax2.set_xlabel('Date')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'progress_{student_name}.png')
    print(f"✓ Progress chart saved")
```

## Tips for Coaches

1. **Establish Baseline**: Always start with 10 laps to have a reference
2. **Focus on 1-2 Areas**: Don't try to improve everything at once
3. **Measure Progression**: Weekly sessions to see improvement
4. **Use Objective Data**: Base feedback on numbers, not impressions
5. **Compare with Reference**: Have an ideal lap as a goal

## Key Metrics

- **Consistency**: >95% is excellent
- **Sector Times**: Identify where most time is lost
- **Corner Speed**: Minimum speed in corners
- **Throttle Control**: Smoothness on exit

---

Data-driven coaching for maximum improvement! 🏎️📈
