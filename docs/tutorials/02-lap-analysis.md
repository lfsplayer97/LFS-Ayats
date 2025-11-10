# Tutorial 2: Anàlisi de Voltes

Aquest tutorial t'ensenyarà a comparar voltes, identificar la millor volta, trobar sectors febles i visualitzar diferències de rendiment.

## Objectius d'Aprenentatge

Al final d'aquest tutorial, sabràs:

- ✅ Identificar la millor volta d'una sessió
- ✅ Comparar dues o més voltes
- ✅ Analitzar sectors i trobar àrees de millora
- ✅ Visualitzar diferències de velocitat i traçada
- ✅ Generar informes d'anàlisi

## Prerequisits

- Tutorial 1 completat
- Fitxers de dades d'una o més sessions
- Coneixements bàsics de visualització amb matplotlib/plotly

## Temps Estimat

45-60 minuts

## Pas 1: Carregar Dades d'una Sessió

Crea un nou script `lap_analysis.py`:

```python
"""
Anàlisi de Voltes
Tutorial per comparar i analitzar voltes de conducció.
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
    Carrega dades d'una sessió des d'un fitxer JSON.
    
    Args:
        filepath: Camí al fitxer JSON
        
    Returns:
        Llista de registres de telemetria
    """
    logger.info(f"Carregant dades: {filepath}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    logger.info(f"✓ Carregades {len(data)} mostres")
    return data
```

## Pas 2: Identificar Voltes Individuals

```python
def extract_laps(telemetry_data: List[Dict]) -> List[List[Dict]]:
    """
    Separa les dades en voltes individuals.
    
    Args:
        telemetry_data: Dades de telemetria completes
        
    Returns:
        Llista de voltes, cada volta és una llista de mostres
    """
    logger.info("Extraient voltes individuals...")
    
    laps = []
    current_lap = []
    last_lap_number = -1
    
    for sample in telemetry_data:
        # Detectar canvi de volta
        lap_number = sample.get('lap', 0)
        
        if lap_number != last_lap_number and current_lap:
            # Nova volta detectada, guardar anterior
            laps.append(current_lap)
            current_lap = []
        
        current_lap.append(sample)
        last_lap_number = lap_number
    
    # Afegir última volta
    if current_lap:
        laps.append(current_lap)
    
    logger.info(f"✓ Trobades {len(laps)} voltes")
    return laps


def calculate_lap_time(lap_data: List[Dict]) -> float:
    """
    Calcula el temps total d'una volta.
    
    Args:
        lap_data: Dades d'una volta
        
    Returns:
        Temps de volta en segons
    """
    if not lap_data:
        return float('inf')
    
    # Buscar registre de volta completada
    for sample in lap_data:
        if sample.get('type') == 'lap' and 'lap_time' in sample:
            return sample['lap_time']
    
    # Si no hi ha registre, calcular per timestamps
    if len(lap_data) >= 2:
        start_time = pd.to_datetime(lap_data[0]['timestamp'])
        end_time = pd.to_datetime(lap_data[-1]['timestamp'])
        return (end_time - start_time).total_seconds()
    
    return float('inf')
```

## Pas 3: Trobar la Millor Volta

```python
def find_best_lap(laps: List[List[Dict]]) -> Tuple[int, List[Dict], float]:
    """
    Identifica la millor volta (més ràpida).
    
    Args:
        laps: Llista de voltes
        
    Returns:
        Tupla (índex, dades, temps) de la millor volta
    """
    logger.info("Buscant la millor volta...")
    
    best_idx = 0
    best_time = float('inf')
    
    for idx, lap in enumerate(laps):
        lap_time = calculate_lap_time(lap)
        
        if lap_time < best_time:
            best_time = lap_time
            best_idx = idx
    
    logger.info(f"✓ Millor volta: #{best_idx + 1} - Temps: {best_time:.3f}s")
    return best_idx, laps[best_idx], best_time


def analyze_all_laps(laps: List[List[Dict]]) -> pd.DataFrame:
    """
    Analitza totes les voltes i retorna estadístiques.
    
    Args:
        laps: Llista de voltes
        
    Returns:
        DataFrame amb estadístiques de cada volta
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
    
    logger.info("\n📊 Resum de Voltes:")
    logger.info(df.to_string(index=False))
    
    return df
```

## Pas 4: Comparar Dues Voltes

```python
def compare_laps(lap1_data: List[Dict], lap2_data: List[Dict], 
                 lap1_name: str = "Volta 1", lap2_name: str = "Volta 2"):
    """
    Compara dues voltes i mostra les diferències.
    
    Args:
        lap1_data: Dades de la primera volta
        lap2_data: Dades de la segona volta
        lap1_name: Nom de la primera volta
        lap2_name: Nom de la segona volta
    """
    logger.info(f"\n=== Comparant {lap1_name} vs {lap2_name} ===")
    
    # Temps de volta
    time1 = calculate_lap_time(lap1_data)
    time2 = calculate_lap_time(lap2_data)
    diff = time2 - time1
    
    logger.info(f"\n⏱️  Temps de Volta:")
    logger.info(f"   {lap1_name}: {time1:.3f}s")
    logger.info(f"   {lap2_name}: {time2:.3f}s")
    logger.info(f"   Diferència: {abs(diff):.3f}s ({'+' if diff > 0 else ''}{diff:.3f}s)")
    
    # Velocitats
    speeds1 = [s.get('speed', 0) for s in lap1_data if 'speed' in s]
    speeds2 = [s.get('speed', 0) for s in lap2_data if 'speed' in s]
    
    logger.info(f"\n🏎️  Velocitats:")
    logger.info(f"   {lap1_name}:")
    logger.info(f"      • Màxima: {max(speeds1):.1f} km/h")
    logger.info(f"      • Mitjana: {np.mean(speeds1):.1f} km/h")
    logger.info(f"      • Mínima: {min(speeds1):.1f} km/h")
    logger.info(f"   {lap2_name}:")
    logger.info(f"      • Màxima: {max(speeds2):.1f} km/h")
    logger.info(f"      • Mitjana: {np.mean(speeds2):.1f} km/h")
    logger.info(f"      • Mínima: {min(speeds2):.1f} km/h")
    
    # RPM
    rpms1 = [s.get('rpm', 0) for s in lap1_data if 'rpm' in s]
    rpms2 = [s.get('rpm', 0) for s in lap2_data if 'rpm' in s]
    
    logger.info(f"\n🔧 RPM:")
    logger.info(f"   {lap1_name}: Max {max(rpms1)} | Mitjà {int(np.mean(rpms1))}")
    logger.info(f"   {lap2_name}: Max {max(rpms2)} | Mitjà {int(np.mean(rpms2))}")
```

## Pas 5: Anàlisi de Sectors

```python
def analyze_sectors(lap_data: List[Dict], num_sectors: int = 3) -> List[Dict]:
    """
    Divideix una volta en sectors i analitza cada un.
    
    Args:
        lap_data: Dades de la volta
        num_sectors: Nombre de sectors (per defecte 3)
        
    Returns:
        Llista d'estadístiques per sector
    """
    logger.info(f"\n=== Anàlisi de Sectors ({num_sectors} sectors) ===")
    
    sector_size = len(lap_data) // num_sectors
    sectors = []
    
    for i in range(num_sectors):
        start_idx = i * sector_size
        end_idx = start_idx + sector_size if i < num_sectors - 1 else len(lap_data)
        
        sector_data = lap_data[start_idx:end_idx]
        speeds = [s.get('speed', 0) for s in sector_data if 'speed' in s]
        
        # Calcular temps del sector
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
        logger.info(f"   • Temps: {sector_time:.3f}s")
        logger.info(f"   • Velocitat màxima: {sector_stats['max_speed']:.1f} km/h")
        logger.info(f"   • Velocitat mitjana: {sector_stats['avg_speed']:.1f} km/h")
    
    return sectors


def compare_sectors(lap1_data: List[Dict], lap2_data: List[Dict], 
                   num_sectors: int = 3):
    """
    Compara sectors entre dues voltes.
    
    Args:
        lap1_data: Dades de la primera volta
        lap2_data: Dades de la segona volta
        num_sectors: Nombre de sectors
    """
    logger.info("\n=== Comparació de Sectors ===")
    
    sectors1 = analyze_sectors(lap1_data, num_sectors)
    sectors2 = analyze_sectors(lap2_data, num_sectors)
    
    logger.info("\n📊 Comparació Detallada:")
    
    for s1, s2 in zip(sectors1, sectors2):
        diff = s2['time'] - s1['time']
        logger.info(f"\nSector {s1['sector']}:")
        logger.info(f"   Volta 1: {s1['time']:.3f}s")
        logger.info(f"   Volta 2: {s2['time']:.3f}s")
        logger.info(f"   Diferència: {abs(diff):.3f}s ({'+' if diff > 0 else ''}{diff:.3f}s)")
        
        if diff < -0.1:
            logger.info(f"   ✓ Volta 2 més ràpida en aquest sector")
        elif diff > 0.1:
            logger.info(f"   ✗ Volta 2 més lenta en aquest sector")
        else:
            logger.info(f"   ≈ Temps similar")
```

## Pas 6: Visualització de Comparació

```python
def visualize_lap_comparison(lap1_data: List[Dict], lap2_data: List[Dict],
                             output_file: str = "lap_comparison.html"):
    """
    Crea visualització interactiva de comparació de voltes.
    
    Args:
        lap1_data: Dades de la primera volta
        lap2_data: Dades de la segona volta
        output_file: Fitxer de sortida HTML
    """
    logger.info(f"\n=== Creant Visualització ===")
    
    # Utilitzar el comparador de voltes
    comparator = LapComparator()
    comparator.add_lap("Millor Volta", lap1_data)
    comparator.add_lap("Volta Actual", lap2_data)
    
    # Crear gràfic de comparació
    fig = comparator.create_comparison_plot()
    
    # Guardar com HTML interactiu
    fig.write_html(output_file)
    logger.info(f"✓ Visualització guardada: {output_file}")
    logger.info(f"   Obre amb el navegador per veure la comparació interactiva")


def create_speed_heatmap(lap_data: List[Dict], output_file: str = "speed_heatmap.html"):
    """
    Crea un mapa de calor de velocitat per la volta.
    
    Args:
        lap_data: Dades de la volta
        output_file: Fitxer de sortida
    """
    import plotly.graph_objects as go
    
    # Extreure posicions i velocitats
    positions_x = [s.get('pos_x', 0) for s in lap_data if 'pos_x' in s]
    positions_y = [s.get('pos_y', 0) for s in lap_data if 'pos_y' in s]
    speeds = [s.get('speed', 0) for s in lap_data if 'speed' in s]
    
    # Crear gràfic
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
            colorbar=dict(title="Velocitat (km/h)")
        ),
        line=dict(width=1, color='rgba(0,0,0,0.3)'),
        name='Traçada'
    ))
    
    fig.update_layout(
        title="Mapa de Velocitat del Circuit",
        xaxis_title="Posició X",
        yaxis_title="Posició Y",
        hovermode='closest'
    )
    
    fig.write_html(output_file)
    logger.info(f"✓ Mapa de calor guardat: {output_file}")
```

## Pas 7: Funció Principal Completa

```python
def main():
    """Funció principal d'anàlisi de voltes."""
    logger.info("=== Anàlisi de Voltes ===\n")
    
    # 1. Carregar dades
    data_file = "data/session_20240115_143022.json"  # Ajusta al teu fitxer
    
    if not Path(data_file).exists():
        logger.error(f"✗ Fitxer no trobat: {data_file}")
        logger.info("   Executa primer el Tutorial 1 per generar dades")
        return
    
    telemetry_data = load_session_data(data_file)
    
    # 2. Extreure voltes
    laps = extract_laps(telemetry_data)
    
    if len(laps) < 2:
        logger.warning("⚠️  Es necessiten almenys 2 voltes per comparar")
        return
    
    # 3. Analitzar totes les voltes
    lap_stats = analyze_all_laps(laps)
    
    # 4. Trobar la millor volta
    best_idx, best_lap, best_time = find_best_lap(laps)
    
    # 5. Comparar millor volta amb última volta
    last_lap = laps[-1]
    compare_laps(best_lap, last_lap, 
                f"Millor Volta #{best_idx + 1}",
                f"Última Volta #{len(laps)}")
    
    # 6. Anàlisi de sectors
    compare_sectors(best_lap, last_lap, num_sectors=3)
    
    # 7. Visualitzacions
    visualize_lap_comparison(best_lap, last_lap, "comparison.html")
    create_speed_heatmap(best_lap, "best_lap_heatmap.html")
    
    logger.info("\n✓ Anàlisi completada!")
    logger.info("\n📁 Fitxers generats:")
    logger.info("   • comparison.html - Comparació interactiva")
    logger.info("   • best_lap_heatmap.html - Mapa de velocitat")


if __name__ == "__main__":
    main()
```

## Executar l'Anàlisi

```bash
python lap_analysis.py
```

## Sortida Esperada

```
INFO - === Anàlisi de Voltes ===
INFO - Carregant dades: data/session_20240115_143022.json
INFO - ✓ Carregades 3000 mostres
INFO - Extraient voltes individuals...
INFO - ✓ Trobades 5 voltes
INFO - 
📊 Resum de Voltes:
 lap_number  lap_time  max_speed  avg_speed  min_speed  max_rpm  avg_rpm  samples
          1     95.34      198.5      142.3       45.2     7800     5234      612
          2     93.12      201.3      145.8       42.1     7900     5412      598
          3     94.56      199.7      143.9       43.5     7850     5298      605
          4     92.87      203.1      147.2       41.8     8000     5456      591
          5     93.45      200.8      144.6       42.9     7920     5387      594

INFO - Buscant la millor volta...
INFO - ✓ Millor volta: #4 - Temps: 92.870s

INFO - === Comparant Millor Volta #4 vs Última Volta #5 ===
INFO - 
⏱️  Temps de Volta:
   Millor Volta #4: 92.870s
   Última Volta #5: 93.450s
   Diferència: 0.580s (+0.580s)
...
INFO - ✓ Anàlisi completada!
```

## Exercicis Pràctics

### Exercici 1: Anàlisi de Consistència

Crea una funció que calculi la consistència del pilot basant-se en la desviació estàndard dels temps de volta.

<details>
<summary>Veure solució</summary>

```python
def calculate_consistency(laps: List[List[Dict]]) -> Dict:
    """Calcula la consistència del pilot."""
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

### Exercici 2: Identificar Zones de Pèrdua de Temps

Crea una funció que identifiqui automàticament on es perd més temps en comparació amb la millor volta.

### Exercici 3: Comparació de Múltiples Voltes

Estén el codi per comparar 3 o més voltes simultàniament.

## Consells Professionals

### 💡 Consell 1: Focus en Sectors
Els sectors són clau per identificar àrees de millora. Practica sector per sector.

### 💡 Consell 2: Consistència vs Velocitat
Una volta consistent és millor que voltes ràpides però inconsistents.

### 💡 Consell 3: Referència Externa
Compara amb voltes de pilots més ràpids per identificar diferències en traçada i velocitats.

### 💡 Consell 4: Dades de Múltiples Sessions
Compara voltes de diferents sessions per veure progressió al llarg del temps.

## Pròxims Passos

1. **[Tutorial 3: Dashboard en Temps Real](03-real-time-dashboard.md)** - Visualització en temps real
2. **[Tutorial 4: Anàlisi Avançada](04-advanced-analysis.md)** - Tècniques avançades
3. **[Cas d'Ús: Driver Coaching](../use-cases/driver-coaching.md)** - Aplicació pràctica

## Recursos

- [Documentació LapComparator](../api_reference.md#lapcomparator)
- [Visualització Avançada](../visualization.md)
- [Anàlisi de Telemetria](../analysis_module.md)

---

Ara pots analitzar voltes com un professional! 🏆
