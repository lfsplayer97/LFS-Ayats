"""
Exemples d'ús del mòdul d'anàlisi en temps real.

Aquest fitxer demostra com utilitzar els diferents components
del mòdul d'anàlisi de LFS-Ayats.
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
    Exemple 1: Detecció d'anomalies

    Demostra com detectar diferents tipus d'anomalies en dades telemètriques.
    """
    print("=" * 70)
    print("Exemple 1: Detecció d'anomalies")
    print("=" * 70)

    # Crear detector d'anomalies
    detector = AnomalyDetector()

    # Simular dades telemètriques
    current_data = {
        "engine_temp": 102.0,  # Temperatura elevada
        "linear_speed": 50.0,
        "wheel_speed": 60.0,  # Rodes patinen
        "steering_angle": 0.5,
        "actual_rotation": 0.3,  # Subviratge
    }

    # Comprovar anomalies
    alerts = detector.check_telemetry(current_data)

    print(f"\nDades telemètriques:")
    print(f"  - Temperatura motor: {current_data['engine_temp']}°C")
    print(f"  - Velocitat lineal: {current_data['linear_speed']} m/s")
    print(f"  - Velocitat rodes: {current_data['wheel_speed']} m/s")

    print(f"\nAlertes detectades: {len(alerts)}")
    for alert in alerts:
        print(f"  {alert}")

    # Comprovar combustible
    fuel_level = 12.0  # 12% de combustible
    fuel_per_lap = 2.5  # 2.5% per volta
    laps_remaining = 10

    detected, alert = detector.detect_fuel_warning(
        fuel_level, fuel_per_lap, laps_remaining
    )

    if detected:
        print(f"\n{alert}")

    print()


def example_2_performance_prediction():
    """
    Exemple 2: Predicció de rendiment

    Demostra com predir temps de volta i gestionar estratègies.
    """
    print("=" * 70)
    print("Exemple 2: Predicció de rendiment")
    print("=" * 70)

    # Crear predictor
    predictor = PerformancePredictor()

    # Dades històriques de voltes anteriors
    historical_data = [
        {"sector_times": [28.5, 31.2, 25.8]},  # Volta 1: 85.5s
        {"sector_times": [28.3, 31.5, 25.6]},  # Volta 2: 85.4s
        {"sector_times": [28.4, 31.1, 25.7]},  # Volta 3: 85.2s
    ]

    # Sectors completats de la volta actual
    current_sectors = [28.2, 31.0]

    # Predir temps final
    predicted_time = predictor.predict_lap_time(current_sectors, historical_data)

    print(f"\nSectors completats: S1={current_sectors[0]}s, S2={current_sectors[1]}s")
    print(f"Temps de volta predit: {predicted_time:.3f}s")

    # Calcular millor temps teòric
    all_sector_times = [lap["sector_times"] for lap in historical_data]
    theoretical, best_sectors = predictor.calculate_theoretical_best(all_sector_times)

    print(f"\nMillor temps teòric: {theoretical:.3f}s")
    print(f"Millors sectors: {[f'{s:.3f}s' for s in best_sectors]}")

    # Predir pit window
    fuel_consumption = 2.5  # % per volta
    tire_wear = 1.8  # % per volta
    laps_remaining = 20

    pit_lap, reason = predictor.predict_pit_window(
        fuel_consumption, tire_wear, laps_remaining
    )

    print(f"\nPit stop recomanat en {pit_lap} voltes per {reason}")

    print()


def example_3_sector_analysis():
    """
    Exemple 3: Anàlisi de sectors

    Demostra com analitzar el rendiment per sectors i identificar àrees de millora.
    """
    print("=" * 70)
    print("Exemple 3: Anàlisi de sectors")
    print("=" * 70)

    # Crear analitzador
    analyzer = SectorAnalyzer()

    # Simular dades de múltiples voltes
    session_data = [
        {"sector_times": [28.5, 31.2, 25.8]},
        {"sector_times": [28.3, 31.5, 25.6]},
        {"sector_times": [28.4, 31.8, 25.7]},
        {"sector_times": [28.6, 31.4, 25.9]},
        {"sector_times": [28.2, 31.9, 25.5]},
    ]

    # Identificar sectors febles
    weak_sectors = analyzer.identify_weak_sectors(session_data)

    print("\nSectors on es perd més temps:")
    for sector in weak_sectors:
        print(f"  Sector {sector.number}: perdent {sector.time_lost:.3f}s")
        print(f"    Temps mitjà: {sector.time:.3f}s")
        print(f"    Millor temps: {sector.best_time:.3f}s")
        print(f"    Consistència: {sector.consistency:.1%}")

    # Calcular consistència per sector
    consistency = analyzer.calculate_sector_consistency(session_data)

    print("\nConsistència per sector:")
    for sector_num, score in consistency.items():
        print(f"  Sector {sector_num}: {score:.1%}")

    print()


def example_4_lap_comparison():
    """
    Exemple 4: Comparació de voltes

    Demostra com comparar dues voltes en detall.
    """
    print("=" * 70)
    print("Exemple 4: Comparació de voltes")
    print("=" * 70)

    # Crear comparador
    comparator = AdvancedComparator()

    # Dades de dues voltes
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

    # Comparar voltes
    comparison = comparator.compare_laps(lap1, lap2)

    print(f"\nComparació: Volta {lap1['lap_id']} vs Volta {lap2['lap_id']}")
    print(f"Diferència total: {comparison.time_difference:+.3f}s")

    print("\nComparació per sectors:")
    for sector_comp in comparison.sector_comparisons:
        symbol = "✓" if sector_comp.difference < 0 else "✗"
        print(
            f"  {symbol} Sector {sector_comp.sector_number}: {sector_comp.difference:+.3f}s ({sector_comp.percentage_diff:+.1f}%)"
        )

    print("\nSuggeriments de millora:")
    for suggestion in comparison.suggestions:
        print(f"  • {suggestion}")

    print()


def example_5_alert_system():
    """
    Exemple 5: Sistema d'alertes

    Demostra com configurar i utilitzar el sistema d'alertes.
    """
    print("=" * 70)
    print("Exemple 5: Sistema d'alertes")
    print("=" * 70)

    # Crear sistema d'alertes
    system = AlertSystem()

    # Afegir gestor de consola per veure alertes
    from src.analysis.alerts import ConsoleAlertHandler

    system.register_handler(ConsoleAlertHandler())

    # Generar diferents tipus d'alertes
    system.create_and_trigger(
        AlertLevel.INFO,
        "Sessió de telemetria iniciada",
        {"timestamp": "2024-01-10 10:00:00"},
    )

    system.create_and_trigger(
        AlertLevel.WARNING, "Temperatura del motor elevada: 98°C", {"temperature": 98.0}
    )

    # Comprovar condicions automàtiques
    telemetry_data = {
        "engine_temp": 110.0,
        "fuel": 4.0,
        "tire_wear": 85.0,
    }

    print("\nComprovant condicions telemètriques...")
    alerts = system.check_conditions(telemetry_data)

    # Obtenir estadístiques
    stats = system.get_statistics()
    print(f"\nEstadístiques del sistema:")
    print(f"  Total d'alertes: {stats['total_alerts']}")
    print(f"  Comptador per tipus: {stats['alert_counts']}")

    print()


def example_6_metrics_calculation():
    """
    Exemple 6: Càlcul de mètriques

    Demostra com calcular diferents mètriques de rendiment.
    """
    print("=" * 70)
    print("Exemple 6: Càlcul de mètriques")
    print("=" * 70)

    # Crear calculadora
    calculator = MetricsCalculator()

    # Temps de voltes d'una sessió
    lap_times = [86.5, 86.2, 85.9, 85.7, 85.5, 85.6, 85.4, 85.5, 85.3, 85.4]
    reference_time = 85.0  # Millor temps del servidor

    # Calcular consistència
    consistency = calculator.calculate_consistency(lap_times)
    print(f"\nConsistència: {consistency:.1%}")

    # Calcular puntuació de ritme
    pace_score = calculator.calculate_pace_score(lap_times, reference_time)
    print(f"Puntuació de ritme: {pace_score:.1f}/100")

    # Calcular taxa de millora
    improvement_rate = calculator.calculate_improvement_rate(lap_times)
    if improvement_rate < 0:
        print(f"Taxa de millora: {abs(improvement_rate):.3f}s per volta (millorant)")
    else:
        print(f"Taxa de millora: {improvement_rate:.3f}s per volta (empitjorant)")

    # Calcular índex de rendiment compost
    performance_index = calculator.calculate_performance_index(
        lap_times, reference_time, consistency_weight=0.3, pace_weight=0.7
    )
    print(f"Índex de rendiment: {performance_index:.1f}/100")

    # Calcular percentil
    all_times = [85.0, 85.5, 86.0, 86.5, 87.0, 85.8, 85.4]
    avg_time = sum(lap_times) / len(lap_times)
    percentile = calculator.calculate_percentile_rank(avg_time, all_times)
    print(f"Percentil: Top {100-percentile:.1f}%")

    print()


def main():
    """Executar tots els exemples."""
    print("\n" + "=" * 70)
    print("EXEMPLES D'ÚS DEL MÒDUL D'ANÀLISI - LFS-Ayats")
    print("=" * 70 + "\n")

    example_1_anomaly_detection()
    example_2_performance_prediction()
    example_3_sector_analysis()
    example_4_lap_comparison()
    example_5_alert_system()
    example_6_metrics_calculation()

    print("=" * 70)
    print("Fi dels exemples")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
