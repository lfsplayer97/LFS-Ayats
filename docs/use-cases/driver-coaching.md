# Cas d'Ús: Entrenament de Pilots (Driver Coaching)

Guia per utilitzar LFS-Ayats com a eina d'entrenament i millora del rendiment de pilots.

## Escenari

**Racing School** ofereix entrenament personalitzat a pilots que volen millorar el seu rendiment. Necessiten:
- Analitzar tècnica de conducció de cada alumne
- Comparar amb pilots de referència (coaches)
- Identificar àrees específiques de millora
- Seguir progressió al llarg del temps
- Proporcionar feedback basat en dades

## Objectius de Coaching

1. **Anàlisi de Consistència**: Identificar variabilitat en voltes
2. **Optimització de Traçada**: Millorar línia de cursa
3. **Gestió de Pneumàtics**: Analitzar degradació
4. **Eficiència de Frenada**: Optimitzar punts i intensitat de frenada
5. **Utilització de Potència**: Maximitzar tracció a la sortida de corbes

## Workflow de Coaching

```
1. Sessió Inicial (Baseline)
   ↓
2. Recollida de Dades
   ↓
3. Anàlisi Automàtica
   ↓
4. Comparació amb Referència
   ↓
5. Identificació d'Àrees de Millora
   ↓
6. Feedback al Pilot
   ↓
7. Sessions de Pràctica
   ↓
8. Seguiment de Progressió
```

## Pas 1: Configurar Sessió d'Entrenament

`coaching_session.py`:
```python
"""
Sistema de coaching amb LFS-Ayats.
Analitza rendiment i proporciona feedback.
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
    """Gestiona sessió de coaching."""
    
    def __init__(self, student_name: str, coach_name: str = None):
        """
        Inicialitza sessió.
        
        Args:
            student_name: Nom de l'alumne
            coach_name: Nom del coach (per comparació)
        """
        self.student_name = student_name
        self.coach_name = coach_name
        self.student_laps = []
        self.coach_laps = []
        self.analyzer = TelemetryAnalyzer()
    
    def collect_baseline(self, num_laps: int = 10):
        """
        Recull voltes de baseline de l'alumne.
        
        Args:
            num_laps: Nombre de voltes a recollir
        """
        logger.info(f"📊 Recollint {num_laps} voltes baseline de {self.student_name}...")
        
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
                logger.info(f"   Volta {lap_count}/{num_laps}: {lap_data['lap_time']:.3f}s")
        
        collector.register_callback('lap', on_lap)
        collector.start()
        
        # Esperar fins tenir totes les voltes
        import time
        while lap_count < num_laps:
            time.sleep(1)
        
        collector.stop()
        client.disconnect()
        
        logger.info(f"✓ Baseline completat: {len(self.student_laps)} voltes")
    
    def analyze_consistency(self) -> Dict:
        """
        Analitza consistència de l'alumne.
        
        Returns:
            Diccionari amb mètriques de consistència
        """
        logger.info("\n=== Anàlisi de Consistència ===")
        
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
        
        logger.info(f"   Mitjana: {mean_time:.3f}s")
        logger.info(f"   Desviació: {std_dev:.3f}s")
        logger.info(f"   Millor: {best_time:.3f}s")
        logger.info(f"   Pitjor: {worst_time:.3f}s")
        logger.info(f"   Consistència: {consistency_score:.1f}/100")
        
        # Feedback
        if consistency_score >= 98:
            logger.info("   ✓ Excel·lent consistència!")
        elif consistency_score >= 95:
            logger.info("   ✓ Bona consistència")
        elif consistency_score >= 90:
            logger.info("   ⚠️  Millorable - focus en reproduir millor volta")
        else:
            logger.info("   ❌ Inconsistent - practica més per estabilitzar")
        
        return results
    
    def compare_with_coach(self):
        """Compara millor volta d'alumne amb coach."""
        if not self.coach_laps:
            logger.warning("No hi ha dades del coach per comparar")
            return
        
        logger.info(f"\n=== Comparació amb {self.coach_name} ===")
        
        # Millor volta de cada un
        student_best = min(self.student_laps, key=lambda l: l['lap_time'])
        coach_best = min(self.coach_laps, key=lambda l: l['lap_time'])
        
        time_diff = student_best['lap_time'] - coach_best['lap_time']
        
        logger.info(f"   {self.student_name}: {student_best['lap_time']:.3f}s")
        logger.info(f"   {self.coach_name}: {coach_best['lap_time']:.3f}s")
        logger.info(f"   Diferència: {time_diff:+.3f}s")
        
        # Comparació visual
        comparator = LapComparator()
        comparator.add_lap(self.student_name, student_best['telemetry'])
        comparator.add_lap(f"{self.coach_name} (ref)", coach_best['telemetry'])
        
        fig = comparator.create_comparison_plot()
        fig.write_html(f"comparison_{self.student_name}.html")
        
        logger.info(f"   📊 Comparació guardada: comparison_{self.student_name}.html")
        
        # Anàlisi sector per sector
        self._analyze_sectors(student_best, coach_best)
    
    def _analyze_sectors(self, student_lap, coach_lap, num_sectors=3):
        """Analitza sectors comparant alumne i coach."""
        logger.info(f"\n📍 Anàlisi per Sectors ({num_sectors} sectors):")
        
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
            logger.info(f"      Alumne: {student_time:.3f}s")
            logger.info(f"      Coach: {coach_time:.3f}s")
            logger.info(f"      Diferència: {diff:+.3f}s")
            
            if diff > 0.1:  # Perd més de 0.1s
                weakest_sectors.append((i+1, diff))
                logger.info(f"      ⚠️  ÀREA DE MILLORA")
        
        return weakest_sectors
    
    def _split_into_sectors(self, telemetry, num_sectors):
        """Divideix telemetria en sectors."""
        sector_size = len(telemetry) // num_sectors
        sectors = []
        
        for i in range(num_sectors):
            start = i * sector_size
            end = start + sector_size if i < num_sectors - 1 else len(telemetry)
            sectors.append(telemetry[start:end])
        
        return sectors
    
    def _calculate_sector_time(self, sector_data):
        """Calcula temps d'un sector."""
        if len(sector_data) < 2:
            return 0
        
        from datetime import datetime
        start_time = datetime.fromisoformat(sector_data[0]['timestamp'])
        end_time = datetime.fromisoformat(sector_data[-1]['timestamp'])
        
        return (end_time - start_time).total_seconds()
    
    def identify_improvement_areas(self) -> List[str]:
        """
        Identifica àrees específiques de millora.
        
        Returns:
            Llista de recomanacions
        """
        logger.info("\n=== Àrees de Millora ===")
        
        recommendations = []
        
        # Analitzar millor volta
        best_lap = min(self.student_laps, key=lambda l: l['lap_time'])
        telemetry = best_lap['telemetry']
        
        # 1. Velocitat mínima en corbes
        speeds = [t['speed'] for t in telemetry]
        min_speed = min(speeds)
        
        if min_speed < 60:
            rec = "Velocitat mínima baixa en corbes - millora entrada i línia"
            recommendations.append(rec)
            logger.info(f"   • {rec}")
        
        # 2. Ús de marxa
        gears = [t.get('gear', 0) for t in telemetry]
        gear_changes = sum(1 for i in range(1, len(gears)) if gears[i] != gears[i-1])
        
        if gear_changes > 50:  # Molts canvis
            rec = "Excessius canvis de marxa - suavitza conducció"
            recommendations.append(rec)
            logger.info(f"   • {rec}")
        
        # 3. Variabilitat de velocitat
        speed_std = np.std(speeds)
        if speed_std > 40:
            rec = "Alta variabilitat de velocitat - mantingues ritme més constant"
            recommendations.append(rec)
            logger.info(f"   • {rec}")
        
        # 4. RPM excessiu
        rpms = [t.get('rpm', 0) for t in telemetry]
        max_rpm = max(rpms)
        if max_rpm > 7800:
            rec = "RPM massa alts - canvia de marxa abans per preservar motor"
            recommendations.append(rec)
            logger.info(f"   • {rec}")
        
        if not recommendations:
            logger.info("   ✓ No s'han detectat problemes majors!")
            recommendations.append("Continua practicant per millorar consistència")
        
        return recommendations
    
    def generate_coaching_report(self, output_file: str = None):
        """Genera report complet de coaching."""
        if output_file is None:
            output_file = f"coaching_report_{self.student_name}.html"
        
        logger.info(f"\n=== Generant Report de Coaching ===")
        
        # Recollir totes les anàlisis
        consistency = self.analyze_consistency()
        improvements = self.identify_improvement_areas()
        
        # Generar HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Report de Coaching - {self.student_name}</title>
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
            <h1>Report de Coaching: {self.student_name}</h1>
            
            <h2>Consistència</h2>
            <div class="metric">
                <p><strong>Temps mitjà:</strong> {consistency.get('mean', 0):.3f}s</p>
                <p><strong>Millor volta:</strong> {consistency.get('best', 0):.3f}s</p>
                <p><strong>Pitjor volta:</strong> {consistency.get('worst', 0):.3f}s</p>
                <p><strong>Score de consistència:</strong> 
                   <span class="{'good' if consistency.get('consistency_score', 0) >= 95 else 'warning'}">
                       {consistency.get('consistency_score', 0):.1f}/100
                   </span>
                </p>
            </div>
            
            <h2>Àrees de Millora</h2>
            <ul>
                {''.join(f'<li>• {rec}</li>' for rec in improvements)}
            </ul>
            
            <h2>Pròxims Passos</h2>
            <ol>
                <li>Focus en sectors identificats com a febles</li>
                <li>Practica 10-15 voltes més centrant-te en consistència</li>
                <li>Revisa comparació amb volta de referència</li>
                <li>Següent sessió: Revisió de progressió</li>
            </ol>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"✓ Report guardat: {output_file}")
        logger.info(f"   Obre amb navegador per veure detalls complets")


def main():
    """Exemple d'ús del sistema de coaching."""
    # Crear sessió
    session = CoachingSession(
        student_name="Alumne1",
        coach_name="Coach_Pro"
    )
    
    # Recollir dades
    logger.info("Comença a conduir al circuit...")
    session.collect_baseline(num_laps=10)
    
    # Anàlisi
    session.analyze_consistency()
    session.identify_improvement_areas()
    
    # Si tens dades del coach, comparar
    # session.compare_with_coach()
    
    # Generar report
    session.generate_coaching_report()
    
    logger.info("\n✓ Sessió de coaching completada!")


if __name__ == "__main__":
    main()
```

## Pas 2: Seguiment de Progressió

`track_progress.py`:
```python
"""
Segueix progressió d'un pilot al llarg del temps.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def track_progress(student_name: str):
    """Mostra progressió d'un alumne."""
    # Carregar sessions històriques
    sessions = load_student_sessions(student_name)
    
    # Extreure temps de millor volta per sessió
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
    
    # Gràfic de progressió
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Millor temps de volta
    ax1.plot(df['date'], df['best_lap'], marker='o')
    ax1.set_title(f'Progressió de {student_name}')
    ax1.set_ylabel('Millor Temps (s)')
    ax1.grid(True)
    
    # Consistència
    ax2.plot(df['date'], df['consistency'], marker='o', color='green')
    ax2.set_ylabel('Consistència (%)')
    ax2.set_xlabel('Data')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'progress_{student_name}.png')
    print(f"✓ Gràfic de progressió guardat")
```

## Consells per Coaches

1. **Estableix Baseline**: Sempre comença amb 10 voltes per tenir referència
2. **Focus en 1-2 Àrees**: No intentar millorar tot alhora
3. **Mesura Progressió**: Sessions setmanals per veure millora
4. **Utilitza Dades Objectives**: Basar feedback en números, no impressions
5. **Compara amb Referència**: Tenir volta ideal com a objectiu

## Mètriques Clau

- **Consistència**: >95% és excel·lent
- **Sector Times**: Identificar on es perd més temps
- **Corner Speed**: Velocitat mínima en corbes
- **Throttle Control**: Suavitat a la sortida

---

Coaching basat en dades per màxima millora! 🏎️📈
