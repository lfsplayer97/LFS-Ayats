"""
Advanced Comparator
Comparació avançada de laps i anàlisi de diferències.

Aquest mòdul proporciona eines per comparar laps en detall,
identificar diferències de rendiment i generar suggeriments de millora.
"""

import logging
import statistics
from typing import List, Dict, Any, Optional
from src.analysis.utils import LapComparison, SectorComparison, TimeDelta

logger = logging.getLogger(__name__)


class AdvancedComparator:
    """
    Advanced lap comparator.

    Provides detailed lap comparison including:
    - Sector time comparison
    - Point-to-point time delta
    - Racing line comparison
    - Key difference identification
    - Improvement suggestion generation

    Example:
        >>> comparator = AdvancedComparator()
        >>> comparison = comparator.compare_laps(lap1_data, lap2_data)
        >>> print(f"Difference: {comparison.time_difference:+.3f}s")
    """

    def __init__(self):
        """Initialize the advanced comparator."""
        self.comparison_cache: Dict[str, LapComparison] = {}
        logger.info("AdvancedComparator initialized")

    def compare_laps(
        self, lap1_data: Dict[str, Any], lap2_data: Dict[str, Any]
    ) -> LapComparison:
        """
        Complete comparison between two laps.

        Args:
            lap1_data: Data from the first lap
            lap2_data: Data from the second lap

        Returns:
            LapComparison with all comparison details

        Example:
            >>> comparator = AdvancedComparator()
            >>> lap1 = {"lap_id": 1, "total_time": 85.5, "sector_times": [28.5, 31.2, 25.8]}
            >>> lap2 = {"lap_id": 2, "total_time": 85.2, "sector_times": [28.3, 31.5, 25.4]}
            >>> comparison = comparator.compare_laps(lap1, lap2)
        """
        lap1_id = lap1_data.get("lap_id", 0)
        lap2_id = lap2_data.get("lap_id", 0)

        # Comparar temps total
        lap1_time = lap1_data.get("total_time", 0)
        lap2_time = lap2_data.get("total_time", 0)
        time_difference = lap1_time - lap2_time

        # Comparar sectors
        sector_comparisons = self._compare_sectors(lap1_data, lap2_data)

        # Comparar traces de velocitat
        speed_comparison = self._compare_speed_traces(lap1_data, lap2_data)

        # Comparar línies de carrera
        line_difference = self._compare_racing_lines(lap1_data, lap2_data)

        # Generar suggeriments
        suggestions = self._generate_suggestions(
            sector_comparisons, speed_comparison, line_difference
        )

        comparison = LapComparison(
            lap1_id=lap1_id,
            lap2_id=lap2_id,
            time_difference=time_difference,
            sector_comparisons=sector_comparisons,
            speed_trace_comparison=speed_comparison,
            racing_line_difference=line_difference,
            suggestions=suggestions,
        )

        # Cache the comparison
        cache_key = f"{lap1_id}_{lap2_id}"
        self.comparison_cache[cache_key] = comparison

        logger.info(
            f"Comparison completed: lap {lap1_id} vs {lap2_id}, "
            f"difference: {time_difference:+.3f}s"
        )

        return comparison

    def _compare_sectors(
        self, lap1_data: Dict[str, Any], lap2_data: Dict[str, Any]
    ) -> List[SectorComparison]:
        """
        Compara sector times entre dues laps.

        Args:
            lap1_data: Data from the first lap
            lap2_data: Data from the second lap

        Returns:
            List of SectorComparison
        """
        sector_comparisons = []

        lap1_sectors = lap1_data.get("sector_times", [])
        lap2_sectors = lap2_data.get("sector_times", [])

        for i, (s1, s2) in enumerate(zip(lap1_sectors, lap2_sectors)):
            difference = s1 - s2
            percentage_diff = (difference / s2 * 100) if s2 > 0 else 0

            sector_comp = SectorComparison(
                sector_number=i + 1,
                lap1_time=s1,
                lap2_time=s2,
                difference=difference,
                percentage_diff=percentage_diff,
            )

            sector_comparisons.append(sector_comp)

        return sector_comparisons

    def _compare_speed_traces(
        self, lap1_data: Dict[str, Any], lap2_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compara traces de velocitat entre dues laps.

        Args:
            lap1_data: Data from the first lap
            lap2_data: Data from the second lap

        Returns:
            Dictionary amb comparació de velocitats
        """
        lap1_telemetry = lap1_data.get("telemetry", [])
        lap2_telemetry = lap2_data.get("telemetry", [])

        if not lap1_telemetry or not lap2_telemetry:
            return {}

        # Extreure velocitats
        lap1_speeds = [t.get("speed", 0) for t in lap1_telemetry]
        lap2_speeds = [t.get("speed", 0) for t in lap2_telemetry]

        # Calculate estadístiques
        comparison = {
            "lap1_avg_speed": statistics.mean(lap1_speeds) if lap1_speeds else 0,
            "lap2_avg_speed": statistics.mean(lap2_speeds) if lap2_speeds else 0,
            "lap1_max_speed": max(lap1_speeds) if lap1_speeds else 0,
            "lap2_max_speed": max(lap2_speeds) if lap2_speeds else 0,
            "lap1_min_speed": min(lap1_speeds) if lap1_speeds else 0,
            "lap2_min_speed": min(lap2_speeds) if lap2_speeds else 0,
        }

        comparison["avg_speed_diff"] = (
            comparison["lap1_avg_speed"] - comparison["lap2_avg_speed"]
        )

        return comparison

    def _compare_racing_lines(
        self, lap1_data: Dict[str, Any], lap2_data: Dict[str, Any]
    ) -> float:
        """
        Compara les línies de carrera entre dues laps.

        Args:
            lap1_data: Data from the first lap
            lap2_data: Data from the second lap

        Returns:
            Average difference en metres between trajectories
        """
        lap1_telemetry = lap1_data.get("telemetry", [])
        lap2_telemetry = lap2_data.get("telemetry", [])

        if not lap1_telemetry or not lap2_telemetry:
            return 0.0

        # Extreure posicions
        lap1_positions = [
            t.get("position", {}) for t in lap1_telemetry if "position" in t
        ]
        lap2_positions = [
            t.get("position", {}) for t in lap2_telemetry if "position" in t
        ]

        if not lap1_positions or not lap2_positions:
            return 0.0

        # Calculate diferències de posició
        # (simplificat: comparar punts corresponents)
        min_length = min(len(lap1_positions), len(lap2_positions))
        differences = []

        for i in range(min_length):
            pos1 = lap1_positions[i]
            pos2 = lap2_positions[i]

            if "x" in pos1 and "y" in pos1 and "x" in pos2 and "y" in pos2:
                dx = pos1["x"] - pos2["x"]
                dy = pos1["y"] - pos2["y"]
                distance = (dx**2 + dy**2) ** 0.5
                differences.append(distance)

        if differences:
            return statistics.mean(differences)

        return 0.0

    def _generate_suggestions(
        self,
        sector_comparisons: List[SectorComparison],
        speed_comparison: Dict[str, Any],
        line_difference: float,
    ) -> List[str]:
        """
        Generate improvement suggestions based on the comparison.

        Args:
            sector_comparisons: Comparacions de sectors
            speed_comparison: Comparació de velocitats
            line_difference: Racing line difference

        Returns:
            List of suggeriments
        """
        suggestions = []

        # Suggestions based on sectors
        for sector in sector_comparisons:
            if sector.difference > 0.1:  # Perdre més de 0.1s
                suggestions.append(
                    f"Millorar sector {sector.sector_number}: "
                    f"perdent {sector.difference:.3f}s ({sector.percentage_diff:+.1f}%)"
                )

        # Suggestions based on speed
        if speed_comparison:
            avg_diff = speed_comparison.get("avg_speed_diff", 0)
            if avg_diff < -1.0:  # Lower average speed
                suggestions.append(
                    f"Increase average speed: "
                    f"currently {abs(avg_diff):.1f} m/s slower"
                )

        # Suggestions based on racing line
        if line_difference > 2.0:  # Significant difference (>2m)
            suggestions.append(
                f"Adjust racing line: average difference of {line_difference:.1f}m"
            )

        return suggestions

    def calculate_time_delta(
        self, lap1_data: Dict[str, Any], lap2_data: Dict[str, Any]
    ) -> TimeDelta:
        """
        Calcula delta de temps punt a punt.

        Args:
            lap1_data: Data from the first lap
            lap2_data: Data from the second lap

        Returns:
            TimeDelta amb delta punt a punt

        Example:
            >>> comparator = AdvancedComparator()
            >>> delta = comparator.calculate_time_delta(lap1, lap2)
            >>> print(f"Màxim gain: {delta.max_gain:.3f}s")
        """
        lap1_telemetry = lap1_data.get("telemetry", [])
        lap2_telemetry = lap2_data.get("telemetry", [])

        if not lap1_telemetry or not lap2_telemetry:
            return TimeDelta()

        # Extreure timestamps i distàncies
        lap1_times = [t.get("timestamp", 0) for t in lap1_telemetry]
        lap2_times = [t.get("timestamp", 0) for t in lap2_telemetry]
        lap1_distances = [t.get("distance", i) for i, t in enumerate(lap1_telemetry)]
        # lap2_distances not used but kept for potential future comparison

        # Calculate deltas (simplificat)
        min_length = min(len(lap1_times), len(lap2_times))
        deltas = []
        distances = []

        for i in range(min_length):
            delta = lap1_times[i] - lap2_times[i]
            deltas.append(delta)
            distances.append(lap1_distances[i])

        if not deltas:
            return TimeDelta()

        return TimeDelta(
            distance_points=distances,
            time_deltas=deltas,
            max_gain=min(deltas) if deltas else 0,
            max_loss=max(deltas) if deltas else 0,
            average_delta=statistics.mean(deltas) if deltas else 0,
        )

    def find_performance_differences(
        self, lap1_data: Dict[str, Any], lap2_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identifica diferències clau de rendiment.

        Args:
            lap1_data: Data from the first lap
            lap2_data: Data from the second lap

        Returns:
            List of diferències significatives

        Example:
            >>> comparator = AdvancedComparator()
            >>> diffs = comparator.find_performance_differences(lap1, lap2)
            >>> for diff in diffs:
            ...     print(diff['description'])
        """
        differences = []

        # Comparar temps total
        time_diff = lap1_data.get("total_time", 0) - lap2_data.get("total_time", 0)
        if abs(time_diff) > 0.05:
            differences.append(
                {
                    "type": "total_time",
                    "value": time_diff,
                    "description": f"Diferència de temps total: {time_diff:+.3f}s",
                    "significant": abs(time_diff) > 0.5,
                }
            )

        # Comparar sectors
        lap1_sectors = lap1_data.get("sector_times", [])
        lap2_sectors = lap2_data.get("sector_times", [])

        for i, (s1, s2) in enumerate(zip(lap1_sectors, lap2_sectors)):
            sector_diff = s1 - s2
            if abs(sector_diff) > 0.05:
                differences.append(
                    {
                        "type": "sector",
                        "sector": i + 1,
                        "value": sector_diff,
                        "description": f"Sector {i+1}: {sector_diff:+.3f}s",
                        "significant": abs(sector_diff) > 0.2,
                    }
                )

        # Comparar velocitats màximes
        lap1_max_speed = lap1_data.get("max_speed", 0)
        lap2_max_speed = lap2_data.get("max_speed", 0)
        speed_diff = lap1_max_speed - lap2_max_speed

        if abs(speed_diff) > 1.0:
            differences.append(
                {
                    "type": "max_speed",
                    "value": speed_diff,
                    "description": f"Velocitat màxima: {speed_diff:+.1f} m/s",
                    "significant": abs(speed_diff) > 5.0,
                }
            )

        return differences

    def get_comparison(self, lap1_id: int, lap2_id: int) -> Optional[LapComparison]:
        """
        Get a comparison from cache.

        Args:
            lap1_id: ID of the first lap
            lap2_id: ID de la segona lap

        Returns:
            LapComparison si existeix, None altrament
        """
        cache_key = f"{lap1_id}_{lap2_id}"
        return self.comparison_cache.get(cache_key)

    def clear_cache(self) -> None:
        """Clear the comparisons cache."""
        self.comparison_cache.clear()
        logger.debug("Comparisons cache cleared")
