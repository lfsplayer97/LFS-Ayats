# Mòdul d'Anàlisi en Temps Real

Mòdul d'anàlisi avançada per LFS-Ayats amb capacitats de detecció d'anomalies, predicció de rendiment i anàlisi de sectors.

## 📋 Característiques

### 🔍 Detecció d'Anomalies (`anomaly.py`)
- **Sobreescalfament del motor**: Detecció amb nivells WARNING i CRITICAL
- **Patinatge de rodes**: Comparació velocitat lineal vs rotacional
- **Subviratge/Sobreviratge**: Anàlisi de comportament de direcció
- **Flat spots**: Detecció de desgast irregular als pneumàtics
- **Frenades inconsistents**: Anàlisi de variabilitat en punts de frenada
- **Avís de combustible**: Predicció de combustible insuficient
- **Mètodes estadístics**: Z-score, IQR, mitjanes mòbils

### 📊 Predicció de Rendiment (`predictor.py`)
- **Temps de volta**: Predicció basada en sectors completats
- **Finestra de pit stop**: Càlcul òptim segons combustible i pneumàtics
- **Vida útil pneumàtics**: Estimació de voltes restants
- **Ritme òptim**: Gestió de combustible per arribar just
- **Canvis de posició**: Predicció basada en ritmes dels competidors
- **Millor temps teòric**: Combinació dels millors sectors

### 📏 Anàlisi de Sectors (`sectors.py`)
- **Comparació de sectors**: Entre diferents voltes
- **Sectors febles**: Identificació d'àrees de millora
- **Consistència**: Càlcul per cada sector
- **Línia òptima**: Basada en voltes ràpides
- **Punts de frenada**: Anàlisi i consistència
- **Aplicació de gas**: Anàlisi per corbes

### 🔄 Comparador Avançat (`comparator.py`)
- **Comparació completa**: Entre dues voltes
- **Delta punt a punt**: Temps guanyat/perdut
- **Traces de velocitat**: Comparació detallada
- **Línies de carrera**: Diferències de trajectòria
- **Suggeriments**: Recomanacions automàtiques de millora

### 🔔 Sistema d'Alertes (`alerts.py`)
- **Gestors múltiples**: Console, Log, Callback personalitzats
- **Filtratge**: Evitar duplicats amb intervals mínims
- **Historial**: Amb estadístiques i cerca
- **Condicions automàtiques**: Verificació de telemetria

### 📐 Càlcul de Mètriques (`metrics.py`)
- **Consistència**: Mesura de regularitat en temps
- **Puntuació de ritme**: Comparació amb referència
- **Taxa de millora**: Evolució durant la sessió
- **Racecraft**: Avaluació d'habilitat en carrera
- **Eficiència**: Combustible i degradació
- **Índexs compostos**: Combinació de múltiples mètriques

## 🚀 Instal·lació

El mòdul està inclòs en LFS-Ayats. Assegura't que tens instal·lades les dependències:

```bash
pip install -r requirements.txt
pip install -e .
```

## 💡 Exemples d'Ús

### Exemple 1: Detecció d'Anomalies

```python
from src.analysis import AnomalyDetector

# Crear detector
detector = AnomalyDetector()

# Comprovar telemetria
current_data = {
    "engine_temp": 102.0,
    "linear_speed": 50.0,
    "wheel_speed": 60.0,
}

alerts = detector.check_telemetry(current_data)
for alert in alerts:
    print(alert)
```

### Exemple 2: Predicció de Temps de Volta

```python
from src.analysis import PerformancePredictor

# Crear predictor
predictor = PerformancePredictor()

# Dades històriques
historical_data = [
    {"sector_times": [28.5, 31.2, 25.8]},
    {"sector_times": [28.3, 31.5, 25.6]},
]

# Predir temps amb 2 sectors completats
predicted_time = predictor.predict_lap_time(
    current_sector_times=[28.2, 31.0],
    historical_data=historical_data
)

print(f"Temps predit: {predicted_time:.3f}s")
```

### Exemple 3: Anàlisi de Sectors

```python
from src.analysis import SectorAnalyzer

# Crear analitzador
analyzer = SectorAnalyzer()

# Dades de múltiples voltes
session_data = [
    {"sector_times": [28.5, 31.2, 25.8]},
    {"sector_times": [28.3, 31.5, 25.6]},
    {"sector_times": [28.4, 31.8, 25.7]},
]

# Identificar sectors febles
weak_sectors = analyzer.identify_weak_sectors(session_data)
for sector in weak_sectors:
    print(f"Sector {sector.number}: perdent {sector.time_lost:.3f}s")
```

### Exemple 4: Sistema d'Alertes

```python
from src.analysis import AlertSystem, AlertLevel
from src.analysis.alerts import ConsoleAlertHandler

# Crear sistema
system = AlertSystem()
system.register_handler(ConsoleAlertHandler())

# Generar alerta
system.create_and_trigger(
    AlertLevel.WARNING,
    "Temperatura elevada",
    {"temp": 98.0}
)

# Comprovar condicions
telemetry = {"engine_temp": 110.0, "fuel": 4.0}
alerts = system.check_conditions(telemetry)
```

### Exemple 5: Comparació de Voltes

```python
from src.analysis import AdvancedComparator

# Crear comparador
comparator = AdvancedComparator()

# Dades de voltes
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

# Comparar
comparison = comparator.compare_laps(lap1, lap2)
print(f"Diferència: {comparison.time_difference:+.3f}s")

for suggestion in comparison.suggestions:
    print(f"• {suggestion}")
```

### Exemple 6: Mètriques de Rendiment

```python
from src.analysis import MetricsCalculator

# Crear calculadora
calculator = MetricsCalculator()

# Temps de voltes
lap_times = [86.5, 86.2, 85.9, 85.7, 85.5]
reference = 85.0

# Calcular mètriques
consistency = calculator.calculate_consistency(lap_times)
pace_score = calculator.calculate_pace_score(lap_times, reference)
performance = calculator.calculate_performance_index(lap_times, reference)

print(f"Consistència: {consistency:.1%}")
print(f"Ritme: {pace_score:.1f}/100")
print(f"Rendiment: {performance:.1f}/100")
```

## 📚 Executar Exemples Complets

```bash
cd /path/to/LFS-Ayats
PYTHONPATH=. python3 examples/analysis_examples.py
```

## 🧪 Tests

El mòdul inclou 69 tests unitaris amb cobertura completa:

```bash
# Executar tests del mòdul
pytest tests/unit/analysis/ -v

# Amb cobertura
pytest tests/unit/analysis/ --cov=src/analysis --cov-report=html
```

## 📖 Documentació d'API

### Classes Principals

#### `AnomalyDetector`
```python
detector = AnomalyDetector(
    temp_warning=95.0,      # Temperatura d'avís (°C)
    temp_critical=105.0,    # Temperatura crítica (°C)
    z_score_threshold=3.0   # Llindar per detecció outliers
)
```

**Mètodes principals:**
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

**Mètodes principals:**
- `predict_lap_time(current_sector_times, historical_data)` → float
- `predict_pit_window(fuel_consumption, tire_wear, laps_remaining)` → (int, str)
- `estimate_tire_life(current_wear, laps_completed)` → (int, float)
- `calculate_optimal_pace(fuel_target, laps_remaining, current_fuel)` → float
- `calculate_theoretical_best(sector_times_per_lap)` → (float, List[float])

#### `SectorAnalyzer`
```python
analyzer = SectorAnalyzer()
```

**Mètodes principals:**
- `compare_sector_times(lap_data, reference_lap_data)` → List[Dict]
- `identify_weak_sectors(session_data)` → List[Sector]
- `calculate_sector_consistency(laps)` → Dict[int, float]
- `analyze_braking_points(laps)` → List[BrakingPoint]

#### `AdvancedComparator`
```python
comparator = AdvancedComparator()
```

**Mètodes principals:**
- `compare_laps(lap1_data, lap2_data)` → LapComparison
- `calculate_time_delta(lap1_data, lap2_data)` → TimeDelta
- `find_performance_differences(lap1, lap2)` → List[Dict]

#### `AlertSystem`
```python
system = AlertSystem(
    max_history=1000,       # Màxim d'alertes a l'historial
    enable_filtering=True   # Filtratge de duplicats
)
```

**Mètodes principals:**
- `register_handler(handler)` → None
- `trigger_alert(alert, min_interval)` → bool
- `create_and_trigger(level, message, data, min_interval)` → bool
- `check_conditions(telemetry_data)` → List[Alert]
- `get_history(level, limit)` → List[Alert]

#### `MetricsCalculator`
```python
calculator = MetricsCalculator()
```

**Mètodes principals:**
- `calculate_consistency(lap_times)` → float
- `calculate_pace_score(lap_times, reference_time)` → float
- `calculate_improvement_rate(lap_times)` → float
- `calculate_performance_index(lap_times, reference_time)` → float
- `calculate_percentile_rank(value, dataset)` → float

## 🔧 Models de Dades

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

## 🤝 Contribuir

Consulta [CONTRIBUTING.md](../CONTRIBUTING.md) per a guies de contribució.

## 📝 Llicència

Aquest projecte està sota llicència MIT. Consulta [LICENSE](../LICENSE) per més detalls.

## 🙏 Crèdits

Desenvolupat com a part del projecte LFS-Ayats per proporcionar anàlisi avançada de telemetria per Live for Speed.
