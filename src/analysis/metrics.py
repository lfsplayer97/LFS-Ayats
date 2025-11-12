"""
Metrics Calculator
Càlcul de mètriques de rendiment per carreres.

Aquest mòdul proporciona càlcul de diverses mètriques utilitzades
per analitzar i avaluar el rendiment en carreres.
"""

import statistics
from typing import List, Dict, Any, Optional

from src.utils import get_logger

logger = get_logger(__name__)


class MetricsCalculator:
    """
    Calculadora de mètriques de rendiment.

    Proporciona càlcul de:
    - Mètriques de consistència
    - Mètriques de velocitat
    - Mètriques de rendiment
    - Índexs compostos

    Exemple:
        >>> calculator = MetricsCalculator()
        >>> consistency = calculator.calculate_consistency([85.5, 85.6, 85.4, 85.7])
        >>> print(f"Consistència: {consistency:.1%}")
    """

    def __init__(self):
        """Inicialitza la calculadora de mètriques."""
        logger.info("MetricsCalculator inicialitzat")

    def calculate_consistency(self, lap_times: List[float]) -> float:
        """
        Calcula la consistència dels temps de volta.

        La consistència es mesura com 1 - CV (coeficient de variació),
        on 1.0 = perfectament consistent, 0.0 = molt inconsistent.

        Args:
            lap_times: Llista de temps de volta

        Returns:
            Puntuació de consistència (0-1)

        Example:
            >>> calculator = MetricsCalculator()
            >>> consistency = calculator.calculate_consistency([85.5, 85.6, 85.4])
            >>> print(f"{consistency:.1%}")
        """
        if len(lap_times) < 2:
            return 1.0

        mean_time = statistics.mean(lap_times)
        stdev_time = statistics.stdev(lap_times)

        if mean_time == 0:
            return 0.0

        # Coeficient de variació
        cv = stdev_time / mean_time

        # Consistència (1 = perfecte, 0 = molt inconsistent)
        consistency = max(0.0, 1.0 - cv)

        return consistency

    def calculate_pace_score(
        self, lap_times: List[float], reference_time: Optional[float] = None
    ) -> float:
        """
        Calcula una puntuació de ritme.

        Args:
            lap_times: Llista de temps de volta
            reference_time: Temps de referència (None = millor temps de la sessió)

        Returns:
            Puntuació de ritme (0-100, on 100 = millor possible)

        Example:
            >>> calculator = MetricsCalculator()
            >>> score = calculator.calculate_pace_score([85.5, 85.6], 85.0)
            >>> print(f"Ritme: {score:.1f}/100")
        """
        if not lap_times:
            return 0.0

        mean_time = statistics.mean(lap_times)
        best_time = min(lap_times)

        # Si no hi ha referència, usar el millor temps propi
        if reference_time is None:
            reference_time = best_time

        if reference_time == 0:
            return 0.0

        # Calcular puntuació (100 = al nivell de referència)
        score = (reference_time / mean_time) * 100

        return min(100.0, max(0.0, score))

    def calculate_improvement_rate(self, lap_times: List[float]) -> float:
        """
        Calcula la taxa de millora al llarg de la sessió.

        Args:
            lap_times: Llista de temps de volta (ordenats cronològicament)

        Returns:
            Taxa de millora (segons/volta), negatiu = millorant

        Example:
            >>> calculator = MetricsCalculator()
            >>> rate = calculator.calculate_improvement_rate([86.0, 85.5, 85.2, 85.0])
            >>> print(f"Millorant {abs(rate):.3f}s per volta")
        """
        if len(lap_times) < 2:
            return 0.0

        # Regressió lineal simple
        n = len(lap_times)
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(lap_times)

        # Calcular pendent
        numerator = sum((x[i] - x_mean) * (lap_times[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        return slope

    def calculate_racecraft_score(
        self,
        overtakes: int,
        defended_positions: int,
        incidents: int,
        laps_completed: int,
    ) -> float:
        """
        Calcula una puntuació de "racecraft" (habilitat de carrera).

        Args:
            overtakes: Nombre d'avançaments realitzats
            defended_positions: Posicions defensades amb èxit
            incidents: Nombre d'incidents (tocs, sortides, etc.)
            laps_completed: Voltes completades

        Returns:
            Puntuació de racecraft (0-100)

        Example:
            >>> calculator = MetricsCalculator()
            >>> score = calculator.calculate_racecraft_score(5, 3, 1, 20)
            >>> print(f"Racecraft: {score:.1f}/100")
        """
        if laps_completed == 0:
            return 0.0

        # Puntuació base per avançaments i defenses
        positive_actions = overtakes * 10 + defended_positions * 5

        # Penalització per incidents
        penalty = incidents * 15

        # Normalitzar per voltes
        score = (positive_actions - penalty) / laps_completed * 10

        # Limitar entre 0 i 100
        return min(100.0, max(0.0, score + 50.0))  # +50 per centrar al voltant de 50

    def calculate_fuel_efficiency(
        self, fuel_used: float, distance_covered: float
    ) -> float:
        """
        Calcula l'eficiència de combustible.

        Args:
            fuel_used: Combustible utilitzat (%)
            distance_covered: Distància coberta (metres)

        Returns:
            Eficiència (metres per % de combustible)

        Example:
            >>> calculator = MetricsCalculator()
            >>> efficiency = calculator.calculate_fuel_efficiency(25.0, 5000.0)
            >>> print(f"{efficiency:.1f} metres per %")
        """
        if fuel_used == 0:
            return 0.0

        return distance_covered / fuel_used

    def calculate_tire_degradation_rate(
        self, initial_pace: float, current_pace: float, laps_on_tires: int
    ) -> float:
        """
        Calcula la taxa de degradació dels pneumàtics.

        Args:
            initial_pace: Ritme inicial amb pneumàtics nous (segons)
            current_pace: Ritme actual (segons)
            laps_on_tires: Voltes amb aquests pneumàtics

        Returns:
            Taxa de degradació (segons perduts per volta)

        Example:
            >>> calculator = MetricsCalculator()
            >>> degradation = calculator.calculate_tire_degradation_rate(85.0, 86.5, 10)
            >>> print(f"Degradació: {degradation:.3f}s per volta")
        """
        if laps_on_tires == 0:
            return 0.0

        pace_loss = current_pace - initial_pace
        rate = pace_loss / laps_on_tires

        return max(0.0, rate)

    def calculate_sector_balance(
        self, sector_times: List[List[float]]
    ) -> Dict[int, float]:
        """
        Calcula l'equilibri de rendiment entre sectors.

        Identifica si un pilot és consistentment més ràpid
        en alguns sectors que en d'altres.

        Args:
            sector_times: Llista de llistes amb temps de sectors per volta

        Returns:
            Diccionari amb puntuacions d'equilibri per sector (0-100)

        Example:
            >>> calculator = MetricsCalculator()
            >>> laps = [[28.5, 31.2, 25.8], [28.3, 31.5, 25.6]]
            >>> balance = calculator.calculate_sector_balance(laps)
        """
        if not sector_times:
            return {}

        # Recopilar temps per sector
        sector_data: Dict[int, List[float]] = {}
        for lap in sector_times:
            for i, time in enumerate(lap):
                if i not in sector_data:
                    sector_data[i] = []
                sector_data[i].append(time)

        # Calcular mitjanes per sector
        sector_means = {i: statistics.mean(times) for i, times in sector_data.items()}
        overall_mean = statistics.mean(
            [t for times in sector_data.values() for t in times]
        )

        # Calcular equilibri (100 = perfectament equilibrat)
        balance = {}
        for sector, mean_time in sector_means.items():
            deviation = abs(mean_time - overall_mean) / overall_mean
            balance[sector + 1] = max(0.0, 100.0 - deviation * 100)

        return balance

    def calculate_performance_index(
        self,
        lap_times: List[float],
        reference_time: float,
        consistency_weight: float = 0.3,
        pace_weight: float = 0.7,
    ) -> float:
        """
        Calcula un índex compost de rendiment.

        Combina consistència i ritme en una sola mètrica.

        Args:
            lap_times: Llista de temps de volta
            reference_time: Temps de referència (e.g., millor del servidor)
            consistency_weight: Pes de la consistència (0-1)
            pace_weight: Pes del ritme (0-1)

        Returns:
            Índex de rendiment (0-100)

        Example:
            >>> calculator = MetricsCalculator()
            >>> index = calculator.calculate_performance_index([85.5, 85.6], 85.0)
            >>> print(f"Rendiment: {index:.1f}/100")
        """
        if not lap_times:
            return 0.0

        # Normalitzar pesos
        total_weight = consistency_weight + pace_weight
        if total_weight > 0:
            consistency_weight /= total_weight
            pace_weight /= total_weight

        # Calcular components
        consistency = self.calculate_consistency(lap_times)
        pace = self.calculate_pace_score(lap_times, reference_time)

        # Combinar
        performance_index = consistency * consistency_weight * 100 + pace * pace_weight

        return min(100.0, max(0.0, performance_index))

    def calculate_z_score(self, value: float, dataset: List[float]) -> float:
        """
        Calcula el z-score d'un valor dins d'un conjunt de dades.

        Args:
            value: Valor a avaluar
            dataset: Conjunt de dades de referència

        Returns:
            Z-score (nombre de desviacions estàndard de la mitjana)

        Example:
            >>> calculator = MetricsCalculator()
            >>> z = calculator.calculate_z_score(85.5, [85.0, 86.0, 85.5, 87.0])
            >>> print(f"Z-score: {z:.2f}")
        """
        if len(dataset) < 2:
            return 0.0

        mean = statistics.mean(dataset)
        stdev = statistics.stdev(dataset)

        if stdev == 0:
            return 0.0

        return (value - mean) / stdev

    def calculate_percentile_rank(self, value: float, dataset: List[float]) -> float:
        """
        Calcula el percentil d'un valor dins d'un conjunt de dades.

        Args:
            value: Valor a avaluar
            dataset: Conjunt de dades de referència

        Returns:
            Percentil (0-100)

        Example:
            >>> calculator = MetricsCalculator()
            >>> percentile = calculator.calculate_percentile_rank(85.5, [85.0, 86.0, 87.0])
            >>> print(f"Top {100-percentile:.1f}%")
        """
        if not dataset:
            return 0.0

        # Per temps de volta, menor és millor
        # Comptar quants són més lents
        slower_count = sum(1 for v in dataset if v > value)
        percentile = (slower_count / len(dataset)) * 100

        return percentile

    def calculate_stability_index(
        self, telemetry_data: List[Dict[str, Any]], metric: str = "speed"
    ) -> float:
        """
        Calcula un índex d'estabilitat per una mètrica telemètrica.

        Args:
            telemetry_data: Llista de punts telemètrics
            metric: Mètrica a analitzar

        Returns:
            Índex d'estabilitat (0-100, on 100 = màxima estabilitat)

        Example:
            >>> calculator = MetricsCalculator()
            >>> data = [{"speed": 50.0}, {"speed": 51.0}, {"speed": 50.5}]
            >>> stability = calculator.calculate_stability_index(data, "speed")
        """
        if not telemetry_data:
            return 0.0

        values = [point.get(metric, 0) for point in telemetry_data if metric in point]

        if len(values) < 2:
            return 100.0

        mean_value = statistics.mean(values)
        stdev_value = statistics.stdev(values)

        if mean_value == 0:
            return 0.0

        # Coeficient de variació invertit
        cv = stdev_value / mean_value
        stability = max(0.0, 100.0 - cv * 100)

        return min(100.0, stability)

    def calculate_aggression_index(
        self,
        overtake_attempts: int,
        successful_overtakes: int,
        defensive_moves: int,
        total_laps: int,
    ) -> float:
        """
        Calcula un índex d'agressivitat en carrera.

        Args:
            overtake_attempts: Intents d'avançament
            successful_overtakes: Avançaments exitosos
            defensive_moves: Moviments defensius
            total_laps: Total de voltes

        Returns:
            Índex d'agressivitat (0-100)

        Example:
            >>> calculator = MetricsCalculator()
            >>> aggression = calculator.calculate_aggression_index(10, 7, 5, 20)
            >>> print(f"Agressivitat: {aggression:.1f}/100")
        """
        if total_laps == 0:
            return 0.0

        # Normalitzar accions per volta
        actions_per_lap = (overtake_attempts + defensive_moves) / total_laps

        # Success rate dels avançaments
        success_rate = (
            successful_overtakes / overtake_attempts if overtake_attempts > 0 else 0.5
        )

        # Combinar factors
        aggression = actions_per_lap * 20 * success_rate

        return min(100.0, max(0.0, aggression))
