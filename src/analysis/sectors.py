"""
Sector Analyzer
Anàlisi detallada del rendiment per sectors.

Aquest mòdul proporciona eines per analitzar el rendiment en diferents
sectors de la pista, identificar punts febles i optimitzar la línia de carrera.
"""

import logging
import statistics
from typing import List, Dict, Any
from src.analysis.utils import Sector, BrakingPoint, ThrottleAnalysis, RacingLine

logger = logging.getLogger(__name__)


class SectorAnalyzer:
    """
    Analitzador de rendiment per sectors.

    Proporciona anàlisi detallada de sectors incloent:
    - Comparació de temps de sectors
    - Identificació de sectors febles
    - Càlcul de consistència
    - Anàlisi de punts de frenada
    - Anàlisi d'aplicació de gas

    Exemple:
        >>> analyzer = SectorAnalyzer()
        >>> weak_sectors = analyzer.identify_weak_sectors(session_data)
        >>> for sector in weak_sectors:
        ...     print(f"Sector {sector.number}: -{sector.time_lost:.3f}s")
    """

    def __init__(self):
        """Inicialitza l'analitzador de sectors."""
        self.analysis_cache: Dict[str, Any] = {}
        logger.info("SectorAnalyzer inicialitzat")

    def compare_sector_times(
        self, lap_data: Dict[str, Any], reference_lap_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Compara temps de sectors entre dues voltes.

        Args:
            lap_data: Dades de la volta actual
            reference_lap_data: Dades de la volta de referència

        Returns:
            Llista de comparacions per cada sector

        Example:
            >>> analyzer = SectorAnalyzer()
            >>> lap1 = {"sector_times": [28.5, 31.2, 25.8]}
            >>> lap2 = {"sector_times": [28.3, 31.5, 25.6]}
            >>> comparisons = analyzer.compare_sector_times(lap1, lap2)
        """
        if "sector_times" not in lap_data or "sector_times" not in reference_lap_data:
            return []

        lap_sectors = lap_data["sector_times"]
        ref_sectors = reference_lap_data["sector_times"]

        comparisons = []
        for i, (lap_time, ref_time) in enumerate(zip(lap_sectors, ref_sectors)):
            difference = lap_time - ref_time
            percentage = (difference / ref_time * 100) if ref_time > 0 else 0

            comparisons.append(
                {
                    "sector": i + 1,
                    "current": lap_time,
                    "reference": ref_time,
                    "difference": difference,
                    "percentage": percentage,
                    "faster": difference < 0,
                }
            )

        return comparisons

    def identify_weak_sectors(
        self, session_data: List[Dict[str, Any]], percentile: float = 0.9
    ) -> List[Sector]:
        """
        Identifica sectors on el pilot perd més temps.

        Args:
            session_data: Llista de dades de voltes
            percentile: Percentil per considerar un sector "feble" (0.9 = top 10%)

        Returns:
            Llista de sectors febles ordenats per temps perdut

        Example:
            >>> analyzer = SectorAnalyzer()
            >>> laps = [
            ...     {"sector_times": [28.5, 31.2, 25.8]},
            ...     {"sector_times": [28.3, 31.5, 25.6]}
            ... ]
            >>> weak = analyzer.identify_weak_sectors(laps)
        """
        if not session_data:
            return []

        # Recopilar tots els temps per sector
        sector_times: Dict[int, List[float]] = {}

        for lap in session_data:
            if "sector_times" not in lap:
                continue

            for i, time in enumerate(lap["sector_times"]):
                if i not in sector_times:
                    sector_times[i] = []
                sector_times[i].append(time)

        # Analitzar cada sector
        weak_sectors = []

        for sector_num, times in sector_times.items():
            if len(times) < 2:
                continue

            # Calcular estadístiques
            mean_time = statistics.mean(times)
            best_time = min(times)
            # worst_time = max(times)  # Not currently used
            stdev = statistics.stdev(times)

            # Calcular temps perdut respecte al millor
            time_lost = mean_time - best_time

            # Calcular consistència (inversa del coeficient de variació)
            consistency = 1.0 - min(1.0, stdev / mean_time) if mean_time > 0 else 0.0

            # Identificar si és un sector feble
            # Un sector és feble si el temps perdut és significatiu
            if time_lost > stdev * 0.5:  # Més de mitja desviació de diferència
                weak_sectors.append(
                    Sector(
                        number=sector_num + 1,
                        time=mean_time,
                        time_lost=time_lost,
                        consistency=consistency,
                        best_time=best_time,
                    )
                )

        # Ordenar per temps perdut (descendent)
        weak_sectors.sort(key=lambda s: s.time_lost, reverse=True)

        logger.info(f"Identificats {len(weak_sectors)} sectors febles")

        return weak_sectors

    def calculate_sector_consistency(
        self, laps: List[Dict[str, Any]]
    ) -> Dict[int, float]:
        """
        Calcula la consistència per cada sector.

        La consistència es mesura com 1 - CV (coeficient de variació),
        on valors més alts indiquen major consistència.

        Args:
            laps: Llista de dades de voltes

        Returns:
            Diccionari amb consistència per número de sector

        Example:
            >>> analyzer = SectorAnalyzer()
            >>> laps = [{"sector_times": [28.5, 31.2, 25.8]}]
            >>> consistency = analyzer.calculate_sector_consistency(laps)
            >>> print(f"Sector 1: {consistency[1]:.1%}")
        """
        sector_times: Dict[int, List[float]] = {}

        # Recopilar temps per sector
        for lap in laps:
            if "sector_times" not in lap:
                continue

            for i, time in enumerate(lap["sector_times"]):
                if i not in sector_times:
                    sector_times[i] = []
                sector_times[i].append(time)

        # Calcular consistència per sector
        consistency = {}

        for sector_num, times in sector_times.items():
            if len(times) < 2:
                consistency[sector_num + 1] = 1.0
                continue

            mean_time = statistics.mean(times)
            stdev = statistics.stdev(times)

            # Coeficient de variació
            cv = stdev / mean_time if mean_time > 0 else 0

            # Consistència (1 = perfecte, 0 = molt inconsistent)
            consistency[sector_num + 1] = max(0.0, 1.0 - cv)

        return consistency

    def find_optimal_racing_line(
        self, telemetry_points: List[Dict[str, Any]], fast_laps_only: bool = True
    ) -> RacingLine:
        """
        Troba la línia òptima basada en voltes ràpides.

        Args:
            telemetry_points: Llista de punts telemètrics amb posició i velocitat
            fast_laps_only: Si cal considerar només voltes ràpides

        Returns:
            RacingLine amb la trajectòria òptima

        Example:
            >>> analyzer = SectorAnalyzer()
            >>> points = [{"position": {"x": 100, "y": 200}, "speed": 50.0}]
            >>> line = analyzer.find_optimal_racing_line(points)
        """
        if not telemetry_points:
            return RacingLine()

        # Filtrar voltes ràpides si és necessari
        if fast_laps_only:
            # Ordenar per velocitat mitjana i prendre el top 20%
            avg_speeds = []
            for point in telemetry_points:
                if "speed" in point:
                    avg_speeds.append(point["speed"])

            if avg_speeds:
                threshold = statistics.quantiles(avg_speeds, n=5)[3]  # 80th percentile
                telemetry_points = [
                    p for p in telemetry_points if p.get("speed", 0) >= threshold
                ]

        # Extreure punts i velocitats
        points = []
        speeds = []

        for telem in telemetry_points:
            if "position" in telem and "speed" in telem:
                pos = telem["position"]
                if "x" in pos and "y" in pos:
                    points.append({"x": pos["x"], "y": pos["y"]})
                    speeds.append(telem["speed"])

        racing_line = RacingLine(points=points, speeds=speeds)

        logger.debug(f"Línia òptima trobada amb {len(points)} punts")

        return racing_line

    def analyze_braking_points(self, laps: List[Dict[str, Any]]) -> List[BrakingPoint]:
        """
        Analitza punts de frenada òptims.

        Args:
            laps: Llista de dades de voltes amb telemetria

        Returns:
            Llista de punts de frenada analitzats

        Example:
            >>> analyzer = SectorAnalyzer()
            >>> laps = [{"braking_zones": [...]}]
            >>> braking = analyzer.analyze_braking_points(laps)
        """
        braking_points = []

        # Agrupar punts de frenada per zones
        braking_zones: Dict[int, List[Dict[str, Any]]] = {}

        for lap_num, lap in enumerate(laps):
            if "braking_zones" not in lap:
                continue

            for zone in lap["braking_zones"]:
                zone_id = zone.get("zone_id", 0)
                if zone_id not in braking_zones:
                    braking_zones[zone_id] = []

                braking_zones[zone_id].append(
                    {
                        "lap": lap_num + 1,
                        "position": zone.get("position", {}),
                        "distance": zone.get("distance", 0),
                        "speed_before": zone.get("speed_before", 0),
                        "speed_after": zone.get("speed_after", 0),
                        "duration": zone.get("duration", 0),
                    }
                )

        # Analitzar cada zona de frenada
        for zone_id, zones in braking_zones.items():
            if not zones:
                continue

            # Calcular estadístiques
            distances = [z["distance"] for z in zones]
            mean_distance = statistics.mean(distances)
            stdev_distance = statistics.stdev(distances) if len(distances) > 1 else 0

            # Consistència (menor desviació = major consistència)
            consistency = (
                1.0 - min(1.0, stdev_distance / mean_distance)
                if mean_distance > 0
                else 1.0
            )

            # Prendre el punt més representatiu (mitjà)
            braking_point = BrakingPoint(
                position=zones[0]["position"],
                lap=len(zones),
                distance=mean_distance,
                speed_before=statistics.mean([z["speed_before"] for z in zones]),
                speed_after=statistics.mean([z["speed_after"] for z in zones]),
                brake_duration=statistics.mean([z["duration"] for z in zones]),
                consistency_score=consistency,
            )

            braking_points.append(braking_point)

        logger.info(f"Analitzats {len(braking_points)} punts de frenada")

        return braking_points

    def analyze_throttle_application(
        self, corners: List[Dict[str, Any]]
    ) -> List[ThrottleAnalysis]:
        """
        Analitza aplicació de gas a les corbes.

        Args:
            corners: Llista de dades de corbes

        Returns:
            Llista d'anàlisi d'aplicació de gas

        Example:
            >>> analyzer = SectorAnalyzer()
            >>> corners = [{"id": 1, "entry_speed": 50, "apex_speed": 45}]
            >>> throttle = analyzer.analyze_throttle_application(corners)
        """
        throttle_analyses = []

        for corner in corners:
            if "id" not in corner:
                continue

            analysis = ThrottleAnalysis(
                corner_id=corner["id"],
                entry_speed=corner.get("entry_speed", 0),
                apex_speed=corner.get("apex_speed", 0),
                exit_speed=corner.get("exit_speed", 0),
                throttle_application_point=corner.get("throttle_point", 0),
                full_throttle_point=corner.get("full_throttle_point", 0),
                time_in_corner=corner.get("time", 0),
            )

            throttle_analyses.append(analysis)

        logger.debug(f"Analitzades {len(throttle_analyses)} corbes")

        return throttle_analyses

    def calculate_sector_speed_profile(
        self, sector_data: List[Dict[str, Any]]
    ) -> Dict[str, List[float]]:
        """
        Calcula el perfil de velocitat d'un sector.

        Args:
            sector_data: Dades telemètriques del sector

        Returns:
            Diccionari amb distances i velocitats corresponents
        """
        distances = []
        speeds = []

        for point in sector_data:
            if "distance" in point and "speed" in point:
                distances.append(point["distance"])
                speeds.append(point["speed"])

        return {"distances": distances, "speeds": speeds}

    def get_sector_statistics(
        self, laps: List[Dict[str, Any]]
    ) -> Dict[int, Dict[str, float]]:
        """
        Obté estadístiques completes per cada sector.

        Args:
            laps: Llista de dades de voltes

        Returns:
            Diccionari amb estadístiques per número de sector
        """
        sector_times: Dict[int, List[float]] = {}

        for lap in laps:
            if "sector_times" not in lap:
                continue

            for i, time in enumerate(lap["sector_times"]):
                if i not in sector_times:
                    sector_times[i] = []
                sector_times[i].append(time)

        statistics_dict = {}

        for sector_num, times in sector_times.items():
            if not times:
                continue

            stats = {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "min": min(times),
                "max": max(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "count": len(times),
            }

            statistics_dict[sector_num + 1] = stats

        return statistics_dict
