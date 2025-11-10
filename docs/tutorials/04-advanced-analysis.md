# Tutorial 4: Anàlisi Avançada

Aquest tutorial cobreix tècniques avançades d'anàlisi de telemetria: detecció d'anomalies, predicció de temps de volta i optimització de traçada.

## Objectius

- ✅ Detectar anomalies en la conducció
- ✅ Predir temps de volta
- ✅ Identificar punts d'optimització
- ✅ Generar reports automàtics

## Prerequisits

- Tutorials anteriors completats
- Coneixements de pandas i numpy
- Dades de múltiples sessions

## Temps Estimat: 60 minuts

## Pas 1: Detecció d'Anomalies

```python
"""
Anàlisi Avançada de Telemetria
Detecció d'anomalies i prediccions.
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
    Detecta anomalies en les dades de telemetria.
    
    Args:
        telemetry_data: DataFrame amb dades
        contamination: Proporció esperada d'anomalies (0-1)
        
    Returns:
        DataFrame amb columna 'anomaly' (-1 = anomalia, 1 = normal)
    """
    logger.info("Detectant anomalies...")
    
    # Seleccionar característiques
    features = ['speed', 'rpm', 'throttle', 'brake']
    X = telemetry_data[features].fillna(0)
    
    # Model Isolation Forest
    model = IsolationForest(contamination=contamination, random_state=42)
    telemetry_data['anomaly'] = model.fit_predict(X)
    
    anomaly_count = (telemetry_data['anomaly'] == -1).sum()
    logger.info(f"✓ Trobades {anomaly_count} anomalies ({anomaly_count/len(telemetry_data)*100:.1f}%)")
    
    return telemetry_data


def analyze_anomalies(telemetry_data: pd.DataFrame):
    """Analitza les anomalies detectades."""
    anomalies = telemetry_data[telemetry_data['anomaly'] == -1]
    
    if len(anomalies) == 0:
        logger.info("No s'han trobat anomalies")
        return
    
    logger.info(f"\n=== Anàlisi d'Anomalies ===")
    logger.info(f"Total anomalies: {len(anomalies)}")
    logger.info(f"\nEstadístiques d'anomalies:")
    logger.info(anomalies[['speed', 'rpm', 'throttle', 'brake']].describe())
```

## Pas 2: Predicció de Temps de Volta

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def prepare_lap_features(laps_data: List[Dict]) -> pd.DataFrame:
    """
    Prepara característiques per predicció de temps de volta.
    
    Args:
        laps_data: Llista de voltes amb dades
        
    Returns:
        DataFrame amb característiques
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
    Entrena model per predir temps de volta.
    
    Args:
        laps_data: Dades d'entrenament
        
    Returns:
        Model entrenat
    """
    logger.info("Entrenant model de predicció...")
    
    df = prepare_lap_features(laps_data)
    
    # Separar features i target
    X = df[['avg_speed', 'max_speed', 'speed_std', 'avg_rpm']]
    y = df['lap_time']
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Entrenar model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Avaluar
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    logger.info(f"✓ Model entrenat")
    logger.info(f"   Train R²: {train_score:.3f}")
    logger.info(f"   Test R²: {test_score:.3f}")
    
    return model


def predict_lap_time(model: LinearRegression, 
                    avg_speed: float, 
                    max_speed: float,
                    speed_std: float,
                    avg_rpm: float) -> float:
    """Prediu temps de volta basant-se en característiques."""
    features = np.array([[avg_speed, max_speed, speed_std, avg_rpm]])
    predicted_time = model.predict(features)[0]
    return predicted_time
```

## Pas 3: Optimització de Traçada

```python
def find_optimal_racing_line(telemetry_data: pd.DataFrame,
                            speed_threshold: float = 150.0) -> pd.DataFrame:
    """
    Identifica la línia de cursa òptima basant-se en velocitat.
    
    Args:
        telemetry_data: Dades de telemetria
        speed_threshold: Velocitat mínima per considerar òptim
        
    Returns:
        DataFrame amb segments òptims
    """
    logger.info("Buscant línia de cursa òptima...")
    
    # Filtrar per velocitat alta
    optimal_segments = telemetry_data[telemetry_data['speed'] >= speed_threshold]
    
    logger.info(f"✓ Trobats {len(optimal_segments)} punts òptims")
    
    return optimal_segments


def calculate_corner_speeds(telemetry_data: pd.DataFrame,
                           corner_threshold: float = 100.0) -> List[Dict]:
    """
    Analitza velocitats en corbes (zones de baixa velocitat).
    
    Args:
        telemetry_data: Dades de telemetria
        corner_threshold: Velocitat màxima per considerar corba
        
    Returns:
        Llista de corbes amb estadístiques
    """
    logger.info("Analitzant velocitats en corbes...")
    
    corners = []
    in_corner = False
    corner_data = []
    
    for idx, row in telemetry_data.iterrows():
        speed = row['speed']
        
        if speed < corner_threshold:
            in_corner = True
            corner_data.append(row)
        elif in_corner and speed >= corner_threshold:
            # Fi de corba
            if len(corner_data) > 5:  # Mínim 5 punts
                corners.append({
                    'entry_speed': corner_data[0]['speed'],
                    'min_speed': min(c['speed'] for c in corner_data),
                    'exit_speed': corner_data[-1]['speed'],
                    'avg_speed': np.mean([c['speed'] for c in corner_data]),
                    'length': len(corner_data)
                })
            corner_data = []
            in_corner = False
    
    logger.info(f"✓ Identificades {len(corners)} corbes")
    
    return corners
```

## Pas 4: Generació de Reports

```python
def generate_analysis_report(telemetry_data: pd.DataFrame,
                            laps_data: List[Dict],
                            output_file: str = "analysis_report.html"):
    """
    Genera report HTML complet d'anàlisi.
    
    Args:
        telemetry_data: Dades de telemetria
        laps_data: Dades de voltes
        output_file: Fitxer de sortida
    """
    logger.info("Generant report d'anàlisi...")
    
    # Detectar anomalies
    telemetry_data = detect_anomalies(telemetry_data)
    
    # Entrenar predictor
    model = train_lap_predictor(laps_data)
    
    # Analitzar corbes
    corners = calculate_corner_speeds(telemetry_data)
    
    # Crear HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Report d'Anàlisi Avançada</title>
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
        <h1>Report d'Anàlisi Avançada de Telemetria</h1>
        
        <h2>Resum General</h2>
        <div class="stat">
            <p><strong>Total de mostres:</strong> {len(telemetry_data)}</p>
            <p><strong>Total de voltes:</strong> {len(laps_data)}</p>
            <p><strong>Anomalies detectades:</strong> {(telemetry_data['anomaly'] == -1).sum()}</p>
        </div>
        
        <h2>Anàlisi de Corbes</h2>
        <div class="stat">
            <p><strong>Corbes identificades:</strong> {len(corners)}</p>
            <p><strong>Velocitat mitjana en corbes:</strong> 
               {np.mean([c['avg_speed'] for c in corners]):.1f} km/h</p>
        </div>
        
        <h2>Prediccions</h2>
        <div class="stat">
            <p>Model de predicció entrenat amb {len(laps_data)} voltes</p>
            <p>Utilitza el model per predir temps de futures voltes</p>
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"✓ Report guardat: {output_file}")
```

## Pas 5: Funció Principal

```python
def main():
    """Funció principal d'anàlisi avançada."""
    logger.info("=== Anàlisi Avançada de Telemetria ===\n")
    
    # Carregar dades
    df = pd.read_csv("data/session_20240115_143022.csv")
    laps = extract_laps_from_dataframe(df)
    
    # 1. Detecció d'anomalies
    df = detect_anomalies(df)
    analyze_anomalies(df)
    
    # 2. Predicció de temps de volta
    model = train_lap_predictor(laps)
    
    # Predir temps de volta següent
    next_lap_time = predict_lap_time(
        model, 
        avg_speed=145.0, 
        max_speed=200.0,
        speed_std=35.0,
        avg_rpm=5500
    )
    logger.info(f"\n🔮 Predicció per següent volta: {next_lap_time:.2f}s")
    
    # 3. Optimització de traçada
    optimal_line = find_optimal_racing_line(df, speed_threshold=150.0)
    corners = calculate_corner_speeds(df)
    
    # 4. Generar report
    generate_analysis_report(df, laps, "advanced_analysis_report.html")
    
    logger.info("\n✓ Anàlisi avançada completada!")


if __name__ == "__main__":
    main()
```

## Exercicis

1. **Millora del Model**: Afegeix més característiques (throttle, brake, gear)
2. **Clustering**: Agrupa voltes similars amb K-means
3. **Anàlisi Temporal**: Detecta tendències en el temps

## Consells

- Necessites múltiples sessions per models precisos
- Normalitza les característiques per millors resultats
- Valida models amb dades no vistes

## Recursos

- [scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas User Guide](https://pandas.pydata.org/)
- [Documentació d'Anàlisi](../analysis_module.md)

---

Ara domines l'anàlisi avançada! 🎓
