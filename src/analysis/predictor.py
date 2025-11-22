"""
Performance Predictor
Performance and lap time prediction for Live for Speed.

This module uses statistical and machine learning techniques
to predict lap times, pit stops, tire wear, and other
performance metrics.
"""

import logging
import statistics
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class PerformancePredictor:
    """
    Race performance predictor.

    Uses historical and current data to predict:
    - Final lap times
    - Optimal pit stop windows
    - Tire life
    - Optimal pace for fuel management
    - Predicted position changes

    Example:
        >>> predictor = PerformancePredictor()
        >>> predicted_time = predictor.predict_lap_time([28.5, 31.2], historical_data)
        >>> print(f"Predicted time: {predicted_time:.3f}s")
    """

    def __init__(self):
        """Initialize the performance predictor."""
        self.historical_predictions: List[Dict[str, Any]] = []
        logger.info("PerformancePredictor initialized")

    def predict_lap_time(
        self,
        current_sector_times: List[float],
        historical_data: Optional[List[Dict[str, Any]]] = None,
    ) -> float:
        """
        Prediu el lap time final basat en sectors actuals.

        Uses the completed sector times i historical data
        to predict el lap time final.

        Args:
            current_sector_times: Temps dels sectors completats fins ara
            historical_data: Dades històriques de laps anteriors

        Returns:
            Lap time predit (segons)

        Example:
            >>> predictor = PerformancePredictor()
            >>> # Amb 2 sectors completats
            >>> predicted = predictor.predict_lap_time([28.5, 31.2])
            >>> print(f"Temps predit: {predicted:.3f}s")
        """
        if not current_sector_times:
            return 0.0

        # Si tenim tots els sectors, retornar la suma
        num_sectors = len(current_sector_times)

        # Si no hi ha historical data, fer estimació simple
        if not historical_data or len(historical_data) == 0:
            # Estimate remaining sectors based on the average of completed ones
            avg_sector = statistics.mean(current_sector_times)
            total_sectors = 3  # Assumir 3 sectors per defecte
            remaining_sectors = max(0, total_sectors - num_sectors)
            return sum(current_sector_times) + (avg_sector * remaining_sectors)

        # Analitzar historical data
        sector_averages: Dict[int, List[float]] = {}
        for lap in historical_data:
            if "sector_times" in lap:
                for i, sector_time in enumerate(lap["sector_times"]):
                    if i not in sector_averages:
                        sector_averages[i] = []
                    sector_averages[i].append(sector_time)

        # Calculate historical averages for each sector
        historical_means = {
            i: statistics.mean(times) for i, times in sector_averages.items()
        }

        # Predict remaining sectors
        predicted_total = sum(current_sector_times)
        for i in range(num_sectors, len(historical_means)):
            if i in historical_means:
                predicted_total += historical_means[i]

        logger.debug(
            f"Temps predit: {predicted_total:.3f}s "
            f"(sectors completats: {num_sectors})"
        )

        return predicted_total

    def predict_pit_window(
        self, fuel_consumption: float, tire_wear: float, laps_remaining: int
    ) -> Tuple[int, str]:
        """
        Prediu quan cal fer pit stop.

        Analyzes fuel i desgast of tires
        to determine the optimal window optimala de pit stop.

        Args:
            fuel_consumption: Fuel consumption per lap (%)
            tire_wear: Tire wear per lap (%)
            laps_remaining: Remaining laps a la cursa

        Returns:
            Tuple with (laps fins pit stop, raó principal)

        Example:
            >>> predictor = PerformancePredictor()
            >>> laps, reason = predictor.predict_pit_window(2.5, 1.8, 20)
            >>> print(f"Pit stop en {laps} laps per {reason}")
        """
        if fuel_consumption <= 0 or tire_wear <= 0:
            return laps_remaining, "No pit stop necessary"

        # Calculate available laps based on fuel (assume 100% initial)
        fuel_laps = 100.0 / fuel_consumption

        # Calculate available laps based on tires (assume 100% life)
        tire_laps = 100.0 / tire_wear

        # Determine limiting factor
        if fuel_laps < tire_laps:
            pit_lap = max(1, int(fuel_laps * 0.9))  # 90% safety margin
            reason = "fuel"
        else:
            pit_lap = max(1, int(tire_laps * 0.9))  # 90% safety margin
            reason = "tires"

        # Adjust if it is beyond the remaining laps
        pit_lap = min(pit_lap, laps_remaining)

        logger.info(
            f"Pit stop predit en {pit_lap} laps per {reason} "
            f"(fuel: {fuel_laps:.1f}, tires: {tire_laps:.1f})"
        )

        return pit_lap, reason

    def estimate_tire_life(
        self, current_wear: float, laps_completed: int
    ) -> Tuple[int, float]:
        """
        Estimate how many more laps can last the tires.

        Args:
            current_wear: Current tire wear (%)
            laps_completed: Laps completed with these tires

        Returns:
            Tuple with (remaining laps, confidence of the estimate 0-1)

        Example:
            >>> predictor = PerformancePredictor()
            >>> laps, confidence = predictor.estimate_tire_life(25.0, 5)
            >>> print(f"Resten {laps} laps (confiança: {confidence:.0%})")
        """
        if current_wear <= 0 or laps_completed <= 0:
            return 0, 0.0

        # Calculate taxa of wear per lap
        wear_per_lap = current_wear / laps_completed

        # Calculate remaining laps until 100% of wear
        remaining_wear = 100.0 - current_wear
        laps_remaining = int(remaining_wear / wear_per_lap)

        # Calculate confiança basada en mostres
        # Més laps completades = més confiança
        confidence = min(1.0, laps_completed / 10.0)

        logger.debug(
            f"Tire life: {laps_remaining} laps "
            f"(desgast: {current_wear:.1f}%, confiança: {confidence:.0%})"
        )

        return max(0, laps_remaining), confidence

    def calculate_optimal_pace(
        self, fuel_target: float, laps_remaining: int, current_fuel: float
    ) -> float:
        """
        Calculate the optimal pace to arrive with the right fuel.

        Args:
            fuel_target: Target fuel at finish (%)
            laps_remaining: Remaining laps
            current_fuel: Combustible actual (%)

        Returns:
            Fuel consumption per lap recomanat (%)

        Example:
            >>> predictor = PerformancePredictor()
            >>> pace = predictor.calculate_optimal_pace(5.0, 20, 55.0)
            >>> print(f"Consum recomanat: {pace:.2f}% per lap")
        """
        if laps_remaining <= 0:
            return 0.0

        # Calculate fuel available to spend
        available_fuel = current_fuel - fuel_target

        # Calculate optimal consumption per lap
        optimal_consumption = available_fuel / laps_remaining

        logger.debug(
            f"Optimal pace: {optimal_consumption:.2f}% per lap "
            f"(fuel disponible: {available_fuel:.1f}%)"
        )

        return max(0.0, optimal_consumption)

    def predict_position_change(
        self,
        current_pace: float,
        competitors_pace: List[Tuple[int, float]],
        laps_remaining: int,
    ) -> Dict[str, Any]:
        """
        Prediu canvis de posició based on ritmes.

        Args:
            current_pace: Current pace (segons per lap)
            competitors_pace: List of (posició, ritme) dels competidors
            laps_remaining: Remaining laps

        Returns:
            Dictionary amb predicció de posició final i canvis esperats

        Example:
            >>> predictor = PerformancePredictor()
            >>> competitors = [(1, 85.2), (2, 85.8), (3, 86.1)]
            >>> prediction = predictor.predict_position_change(85.5, competitors, 10)
            >>> print(f"Posició predita: {prediction['final_position']}")
        """
        if not competitors_pace or laps_remaining <= 0:
            return {"final_position": None, "changes": []}

        # Calculate temps total per cada competidor
        time_projections = []
        for position, pace in competitors_pace:
            total_time = pace * laps_remaining
            time_projections.append((position, total_time))

        # Calculate temps propi
        own_time = current_pace * laps_remaining
        time_projections.append((0, own_time))  # 0 = posició pròpia

        # Ordenar per temps
        sorted_times = sorted(time_projections, key=lambda x: x[1])

        # Trobar posició predita
        final_position = None
        for i, (pos, _) in enumerate(sorted_times):
            if pos == 0:
                final_position = i + 1
                break

        # Identificar canvis de posició
        changes = []
        if final_position:
            for pos, pace in competitors_pace:
                # Calculate gain/loss de temps per lap
                time_diff_per_lap = pace - current_pace
                total_diff = time_diff_per_lap * laps_remaining

                if abs(total_diff) > 1.0:  # Significant difference
                    changes.append(
                        {
                            "position": pos,
                            "time_diff": total_diff,
                            "can_overtake": total_diff > 0,
                        }
                    )

        result = {
            "final_position": final_position,
            "changes": changes,
            "own_pace": current_pace,
            "laps_remaining": laps_remaining,
        }

        logger.info(
            f"Posició predita: {final_position} " f"(possibles canvis: {len(changes)})"
        )

        return result

    def predict_with_linear_regression(
        self, x_data: List[float], y_data: List[float], x_predict: float
    ) -> float:
        """
        Prediction using simple linear regression.

        Args:
            x_data: X values (e.g., lap number)
            y_data: Y values (e.g., lap time)
            x_predict: X value to predict

        Returns:
            Predicted Y value

        Example:
            >>> predictor = PerformancePredictor()
            >>> laps = [1, 2, 3, 4, 5]
            >>> times = [86.5, 86.2, 85.9, 85.7, 85.5]
            >>> predicted = predictor.predict_with_linear_regression(laps, times, 6)
        """
        if len(x_data) != len(y_data) or len(x_data) < 2:
            return 0.0

        # Calculate averages
        x_mean = statistics.mean(x_data)
        y_mean = statistics.mean(y_data)

        # Calculate slope (slope)
        numerator = sum(
            (x_data[i] - x_mean) * (y_data[i] - y_mean) for i in range(len(x_data))
        )
        denominator = sum((x - x_mean) ** 2 for x in x_data)

        if denominator == 0:
            return y_mean

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Predir
        prediction = slope * x_predict + intercept

        return prediction

    def predict_trend(
        self, historical_values: List[float], periods_ahead: int = 1
    ) -> List[float]:
        """
        Predict trend future based on historical values.

        Uses a weighted average that gives more importance
        to recent values.

        Args:
            historical_values: Historical values (ordered chronologically)
            periods_ahead: Number of periods to predict

        Returns:
            List of predicted values

        Example:
            >>> predictor = PerformancePredictor()
            >>> times = [86.5, 86.2, 85.9, 85.7, 85.5]
            >>> future = predictor.predict_trend(times, 3)
            >>> print(future)  # [85.3, 85.1, 84.9] (aproximat)
        """
        if not historical_values or periods_ahead <= 0:
            return []

        # Calculate exponential weights (more weight to recent values)
        n = len(historical_values)
        weights = [2**i for i in range(n)]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]

        # Calculate average ponderada
        weighted_mean = sum(
            historical_values[i] * normalized_weights[i] for i in range(n)
        )

        # Calculate trend (slope)
        if n >= 2:
            recent_change = historical_values[-1] - historical_values[-2]
        else:
            recent_change = 0

        # Predir valors futurs
        predictions = []
        last_value = historical_values[-1]

        for i in range(periods_ahead):
            # Combine trend amb regression to the average
            trend_component = recent_change * 0.7  # 70% of the trend
            mean_component = (weighted_mean - last_value) * 0.3  # 30% towards the average

            next_value = last_value + trend_component + mean_component
            predictions.append(next_value)
            last_value = next_value

        return predictions

    def calculate_theoretical_best(
        self, sector_times_per_lap: List[List[float]]
    ) -> Tuple[float, List[float]]:
        """
        Calculate the best theoretical time combining the best sectors.

        Args:
            sector_times_per_lap: List of lists with sector times per lap

        Returns:
            Tuple with (theoretical time, best times per sector)

        Example:
            >>> predictor = PerformancePredictor()
            >>> laps = [[28.5, 31.2, 25.8], [28.3, 31.5, 25.6]]
            >>> theoretical, best_sectors = predictor.calculate_theoretical_best(laps)
            >>> print(f"Best theoretical: {theoretical:.3f}s")
        """
        if not sector_times_per_lap:
            return 0.0, []

        # Determinar number of sectors
        num_sectors = max(len(lap) for lap in sector_times_per_lap)

        # Find best time per cada sector
        best_sectors = []
        for sector_idx in range(num_sectors):
            sector_times = [
                lap[sector_idx] for lap in sector_times_per_lap if sector_idx < len(lap)
            ]
            if sector_times:
                best_sectors.append(min(sector_times))

        # Calculate theoretical time
        theoretical_best = sum(best_sectors)

        logger.info(
            f"Best theoretical time: {theoretical_best:.3f}s "
            f"(sectors: {[f'{t:.3f}' for t in best_sectors]})"
        )

        return theoretical_best, best_sectors

    def get_prediction_history(self) -> List[Dict[str, Any]]:
        """
        Retorna l'historial de prediccions realitzades.

        Returns:
            List of prediccions històriques
        """
        return self.historical_predictions.copy()
