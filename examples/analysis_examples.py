"""
Real-time analysis module usage examples.

This file demonstrates how to use the different components
of the LFS-Ayats analysis module.
"""

from src.analysis import (
    AnomalyDetector,
    PerformancePredictor,
    SectorAnalyzer,
    AdvancedComparator,
    AlertSystem,
    AlertLevel,
    MetricsCalculator,
)


def example_1_anomaly_detection():
    """
    Example 1: Anomaly Detection

    Demonstrates how to detect different types of anomalies in telemetry data.
    """
    print("=" * 70)
    print("Example 1: Anomaly Detection")
    print("=" * 70)

    # Create anomaly detector
    detector = AnomalyDetector()

    # Simulate telemetry data
    current_data = {
        "engine_temp": 102.0,  # Elevated temperature
        "linear_speed": 50.0,
        "wheel_speed": 60.0,  # Wheels slipping
        "steering_angle": 0.5,
        "actual_rotation": 0.3,  # Understeer
    }

    # Check anomalies
    alerts = detector.check_telemetry(current_data)

    print("\nTelemetry data:")
    print(f"  - Engine temperature: {current_data['engine_temp']}°C")
    print(f"  - Linear speed: {current_data['linear_speed']} m/s")
    print(f"  - Wheel speed: {current_data['wheel_speed']} m/s")

    print(f"\nDetected alerts: {len(alerts)}")
    for alert in alerts:
        print(f"  {alert}")

    # Check fuel
    fuel_level = 12.0  # 12% fuel
    fuel_per_lap = 2.5  # 2.5% per lap
    laps_remaining = 10

    detected, alert = detector.detect_fuel_warning(
        fuel_level, fuel_per_lap, laps_remaining
    )

    if detected:
        print(f"\n{alert}")

    print()


def example_2_performance_prediction():
    """
    Example 2: Performance Prediction

    Demonstrates how to predict lap times and manage strategies.
    """
    print("=" * 70)
    print("Example 2: Performance Prediction")
    print("=" * 70)

    # Create predictor
    predictor = PerformancePredictor()

    # Historical data from previous laps
    historical_data = [
        {"sector_times": [28.5, 31.2, 25.8]},  # Lap 1: 85.5s
        {"sector_times": [28.3, 31.5, 25.6]},  # Lap 2: 85.4s
        {"sector_times": [28.4, 31.1, 25.7]},  # Lap 3: 85.2s
    ]

    # Completed sectors of current lap
    current_sectors = [28.2, 31.0]

    # Predict final time
    predicted_time = predictor.predict_lap_time(current_sectors, historical_data)

    print(f"\nCompleted sectors: S1={current_sectors[0]}s, S2={current_sectors[1]}s")
    print(f"Predicted lap time: {predicted_time:.3f}s")

    # Calculate theoretical best time
    all_sector_times = [lap["sector_times"] for lap in historical_data]
    theoretical, best_sectors = predictor.calculate_theoretical_best(all_sector_times)

    print(f"\nTheoretical best time: {theoretical:.3f}s")
    print(f"Best sectors: {[f'{s:.3f}s' for s in best_sectors]}")

    # Predict pit window
    fuel_consumption = 2.5  # % per lap
    tire_wear = 1.8  # % per lap
    laps_remaining = 20

    pit_lap, reason = predictor.predict_pit_window(
        fuel_consumption, tire_wear, laps_remaining
    )

    print(f"\nRecommended pit stop in {pit_lap} laps due to {reason}")

    print()


def example_3_sector_analysis():
    """
    Example 3: Sector Analysis

    Demonstrates how to analyze performance by sectors and identify areas for improvement.
    """
    print("=" * 70)
    print("Example 3: Sector Analysis")
    print("=" * 70)

    # Create analyzer
    analyzer = SectorAnalyzer()

    # Simulate data from multiple laps
    session_data = [
        {"sector_times": [28.5, 31.2, 25.8]},
        {"sector_times": [28.3, 31.5, 25.6]},
        {"sector_times": [28.4, 31.8, 25.7]},
        {"sector_times": [28.6, 31.4, 25.9]},
        {"sector_times": [28.2, 31.9, 25.5]},
    ]

    # Identify weak sectors
    weak_sectors = analyzer.identify_weak_sectors(session_data)

    print("\nSectors where most time is lost:")
    for sector in weak_sectors:
        print(f"  Sector {sector.number}: losing {sector.time_lost:.3f}s")
        print(f"    Average time: {sector.time:.3f}s")
        print(f"    Best time: {sector.best_time:.3f}s")
        print(f"    Consistency: {sector.consistency:.1%}")

    # Calculate consistency per sector
    consistency = analyzer.calculate_sector_consistency(session_data)

    print("\nConsistency per sector:")
    for sector_num, score in consistency.items():
        print(f"  Sector {sector_num}: {score:.1%}")

    print()


def example_4_lap_comparison():
    """
    Example 4: Lap Comparison

    Demostra com comparar dues voltes en detall.
    """
    print("=" * 70)
    print("Example 4: Lap Comparison")
    print("=" * 70)

    # Create comparator
    comparator = AdvancedComparator()

    # Data for two laps
    lap1 = {
        "lap_id": 5,
        "total_time": 85.5,
        "sector_times": [28.5, 31.2, 25.8],
        "max_speed": 180.0,
    }

    lap2 = {
        "lap_id": 8,
        "total_time": 85.2,
        "sector_times": [28.3, 31.5, 25.4],
        "max_speed": 182.0,
    }

    # Compare laps
    comparison = comparator.compare_laps(lap1, lap2)

    print(f"\nComparison: Lap {lap1['lap_id']} vs Lap {lap2['lap_id']}")
    print(f"Total difference: {comparison.time_difference:+.3f}s")

    print("\nSector comparison:")
    for sector_comp in comparison.sector_comparisons:
        symbol = "✓" if sector_comp.difference < 0 else "✗"
        print(
            f"  {symbol} Sector {sector_comp.sector_number}: "
            f"{sector_comp.difference:+.3f}s "
            f"({sector_comp.percentage_diff:+.1f}%)"
        )

    print("\nImprovement suggestions:")
    for suggestion in comparison.suggestions:
        print(f"  • {suggestion}")

    print()


def example_5_alert_system():
    """
    Example 5: Alert System

    Demonstrates how to configure and use the alert system.
    """
    print("=" * 70)
    print("Example 5: Alert System")
    print("=" * 70)

    # Create alert system
    system = AlertSystem()

    # Add console handler to view alerts
    from src.analysis.alerts import ConsoleAlertHandler

    system.register_handler(ConsoleAlertHandler())

    # Generate different types of alerts
    system.create_and_trigger(
        AlertLevel.INFO,
        "Telemetry session started",
        {"timestamp": "2024-01-10 10:00:00"},
    )

    system.create_and_trigger(
        AlertLevel.WARNING, "Engine temperature elevated: 98°C", {"temperature": 98.0}
    )

    # Check automatic conditions
    telemetry_data = {
        "engine_temp": 110.0,
        "fuel": 4.0,
        "tire_wear": 85.0,
    }

    print("\nChecking telemetry conditions...")
    system.check_conditions(telemetry_data)

    # Get statistics
    stats = system.get_statistics()
    print("\nSystem statistics:")
    print(f"  Total alerts: {stats['total_alerts']}")
    print(f"  Counter by type: {stats['alert_counts']}")

    print()


def example_6_metrics_calculation():
    """
    Example 6: Metrics Calculation

    Demonstrates how to calculate different performance metrics.
    """
    print("=" * 70)
    print("Example 6: Metrics Calculation")
    print("=" * 70)

    # Create calculator
    calculator = MetricsCalculator()

    # Lap times from a session
    lap_times = [86.5, 86.2, 85.9, 85.7, 85.5, 85.6, 85.4, 85.5, 85.3, 85.4]
    reference_time = 85.0  # Best server time

    # Calculate consistency
    consistency = calculator.calculate_consistency(lap_times)
    print(f"\nConsistency: {consistency:.1%}")

    # Calculate pace score
    pace_score = calculator.calculate_pace_score(lap_times, reference_time)
    print(f"Pace score: {pace_score:.1f}/100")

    # Calculate improvement rate
    improvement_rate = calculator.calculate_improvement_rate(lap_times)
    if improvement_rate < 0:
        print(f"Improvement rate: {abs(improvement_rate):.3f}s per lap (improving)")
    else:
        print(f"Improvement rate: {improvement_rate:.3f}s per lap (worsening)")

    # Calculate composite performance index
    performance_index = calculator.calculate_performance_index(
        lap_times, reference_time, consistency_weight=0.3, pace_weight=0.7
    )
    print(f"Performance index: {performance_index:.1f}/100")

    # Calculate percentile
    all_times = [85.0, 85.5, 86.0, 86.5, 87.0, 85.8, 85.4]
    avg_time = sum(lap_times) / len(lap_times)
    percentile = calculator.calculate_percentile_rank(avg_time, all_times)
    print(f"Percentile: Top {100-percentile:.1f}%")

    print()


def main():
    """Execute all examples."""
    print("\n" + "=" * 70)
    print("ANALYSIS MODULE USAGE EXAMPLES - LFS-Ayats")
    print("=" * 70 + "\n")

    example_1_anomaly_detection()
    example_2_performance_prediction()
    example_3_sector_analysis()
    example_4_lap_comparison()
    example_5_alert_system()
    example_6_metrics_calculation()

    print("=" * 70)
    print("End of examples")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
