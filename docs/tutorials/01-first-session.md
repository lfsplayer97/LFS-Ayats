# Tutorial 1: Primera Sessió de Telemetria

Aquest tutorial t'ensenyarà a recollir, analitzar i exportar dades telemètriques d'una sessió completa de conducció a Live for Speed.

## Objectius d'Aprenentatge

Al final d'aquest tutorial, sabràs:

- ✅ Configurar una sessió de recollida de telemetria
- ✅ Recollir dades en temps real durant la conducció
- ✅ Exportar dades a formats CSV i JSON
- ✅ Analitzar les dades recollides
- ✅ Identificar la millor volta de la sessió

## Prerequisits

- LFS-Ayats instal·lat i configurat (veure [Guia d'Inici Ràpid](../quick-start.md))
- Live for Speed en execució amb InSim activat
- Coneixements bàsics de Python

## Temps Estimat

30-45 minuts

## Pas 1: Preparar l'Entorn de Treball

Crea un nou script Python per la teva primera sessió:

```bash
cd LFS-Ayats
touch my_first_session.py
```

O utilitza el teu editor preferit per crear `my_first_session.py`.

## Pas 2: Importar Mòduls Necessaris

```python
"""
Primera Sessió de Telemetria
Tutorial complet per recollir dades d'una sessió de conducció.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Importar mòduls de LFS-Ayats
from src.connection import InSimClient, PacketHandler
from src.telemetry import TelemetryCollector
from src.export import CSVExporter, JSONExporter
from src.utils import setup_logger

# Configurar logging
logger = setup_logger("first_session", "INFO")
```

## Pas 3: Configurar la Connexió InSim

```python
def setup_connection():
    """
    Configura i estableix connexió amb LFS.
    
    Returns:
        InSimClient: Client InSim connectat
    """
    logger.info("=== Primera Sessió de Telemetria ===")
    
    # Configuració de connexió
    HOST = "127.0.0.1"
    PORT = 29999
    APP_NAME = "FirstSession"
    
    try:
        # Crear i connectar client
        client = InSimClient(
            host=HOST,
            port=PORT,
            admin_password="",
            app_name=APP_NAME
        )
        
        client.connect()
        logger.info(f"✓ Connectat a {HOST}:{PORT}")
        
        # Inicialitzar InSim
        client.initialize()
        logger.info("✓ InSim inicialitzat")
        
        return client
        
    except ConnectionError as e:
        logger.error(f"✗ Error de connexió: {e}")
        logger.error("  Verifica que LFS està executant amb InSim activat")
        sys.exit(1)
```

## Pas 4: Configurar el Col·lector de Telemetria

```python
def setup_telemetry_collector(client):
    """
    Configura el col·lector de telemetria.
    
    Args:
        client: Client InSim connectat
        
    Returns:
        TelemetryCollector: Col·lector configurat
    """
    collector = TelemetryCollector(client)
    
    # Registrar callback per notificacions
    def on_lap_completed(lap_data):
        """Callback quan es completa una volta."""
        logger.info(f"🏁 Volta completada: {lap_data['lap_time']:.2f}s")
    
    def on_telemetry_update(telemetry_data):
        """Callback per actualitzacions de telemetria."""
        if telemetry_data:
            speed = telemetry_data.get('speed', 0)
            rpm = telemetry_data.get('rpm', 0)
            gear = telemetry_data.get('gear', 0)
            logger.debug(f"📊 Velocitat: {speed:.1f} km/h | RPM: {rpm} | Marxa: {gear}")
    
    # Registrar callbacks
    collector.register_callback("lap", on_lap_completed)
    collector.register_callback("telemetry", on_telemetry_update)
    
    logger.info("✓ Col·lector de telemetria configurat")
    return collector
```

## Pas 5: Recollir Dades de la Sessió

```python
def collect_session_data(collector, duration_seconds=300):
    """
    Recull dades durant un temps determinat.
    
    Args:
        collector: Col·lector de telemetria
        duration_seconds: Durada de la sessió en segons (per defecte 5 minuts)
    """
    logger.info(f"🏁 Iniciant recollida de dades durant {duration_seconds} segons")
    logger.info("   Comença a conduir pel circuit!")
    
    # Iniciar recollida
    collector.start()
    
    start_time = time.time()
    last_update = start_time
    
    try:
        while time.time() - start_time < duration_seconds:
            # Mostrar progrés cada 30 segons
            current_time = time.time()
            if current_time - last_update >= 30:
                elapsed = int(current_time - start_time)
                remaining = duration_seconds - elapsed
                logger.info(f"⏱️  Temps transcorregut: {elapsed}s | Restant: {remaining}s")
                last_update = current_time
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Recollida interrompuda per l'usuari")
    
    finally:
        # Aturar recollida
        collector.stop()
        logger.info("✓ Recollida de dades finalitzada")
```

## Pas 6: Analitzar les Dades Recollides

```python
def analyze_session_data(collector):
    """
    Analitza les dades recollides de la sessió.
    
    Args:
        collector: Col·lector amb dades
        
    Returns:
        dict: Estadístiques de la sessió
    """
    logger.info("\n=== Analitzant Dades de la Sessió ===")
    
    # Obtenir estadístiques
    stats = collector.get_statistics()
    
    if not stats:
        logger.warning("⚠️  No s'han recollit dades durant la sessió")
        return None
    
    # Mostrar estadístiques generals
    logger.info("\n📊 Estadístiques Generals:")
    logger.info(f"   • Total de mostres: {stats.get('total_samples', 0)}")
    logger.info(f"   • Jugadors detectats: {stats.get('player_count', 0)}")
    
    # Estadístiques per jugador
    for player_id, player_stats in stats.get('players', {}).items():
        logger.info(f"\n👤 Jugador {player_id}:")
        logger.info(f"   • Mostres: {player_stats.get('sample_count', 0)}")
        logger.info(f"   • Velocitat màxima: {player_stats.get('max_speed', 0):.1f} km/h")
        logger.info(f"   • Velocitat mitjana: {player_stats.get('avg_speed', 0):.1f} km/h")
        logger.info(f"   • RPM màxim: {player_stats.get('max_rpm', 0)}")
    
    return stats
```

## Pas 7: Exportar les Dades

```python
def export_session_data(collector):
    """
    Exporta les dades de la sessió a CSV i JSON.
    
    Args:
        collector: Col·lector amb dades
    """
    logger.info("\n=== Exportant Dades ===")
    
    # Obtenir totes les dades
    all_data = collector.get_telemetry_history()
    
    if not all_data:
        logger.warning("⚠️  No hi ha dades per exportar")
        return
    
    # Crear directori de dades si no existeix
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generar nom de fitxer amb timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Exportar a CSV
    csv_filename = data_dir / f"session_{timestamp}.csv"
    csv_exporter = CSVExporter(str(csv_filename))
    csv_exporter.export(all_data)
    logger.info(f"✓ Dades exportades a CSV: {csv_filename}")
    
    # Exportar a JSON
    json_filename = data_dir / f"session_{timestamp}.json"
    json_exporter = JSONExporter(str(json_filename))
    json_exporter.export(all_data)
    logger.info(f"✓ Dades exportades a JSON: {json_filename}")
    
    logger.info(f"\n📁 Fitxers generats:")
    logger.info(f"   • CSV: {csv_filename}")
    logger.info(f"   • JSON: {json_filename}")
```

## Pas 8: Funció Principal

```python
def main():
    """Funció principal del programa."""
    try:
        # 1. Configurar connexió
        client = setup_connection()
        
        # 2. Configurar col·lector
        collector = setup_telemetry_collector(client)
        
        # 3. Recollir dades (5 minuts)
        collect_session_data(collector, duration_seconds=300)
        
        # 4. Analitzar dades
        stats = analyze_session_data(collector)
        
        # 5. Exportar dades
        if stats:
            export_session_data(collector)
        
        # 6. Desconnectar
        client.disconnect()
        logger.info("\n✓ Sessió finalitzada correctament")
        
    except Exception as e:
        logger.error(f"✗ Error durant la sessió: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Executar la Sessió

Amb LFS en execució i en una sessió de conducció:

```bash
python my_first_session.py
```

## Sortida Esperada

```
INFO - === Primera Sessió de Telemetria ===
INFO - ✓ Connectat a 127.0.0.1:29999
INFO - ✓ InSim inicialitzat
INFO - ✓ Col·lector de telemetria configurat
INFO - 🏁 Iniciant recollida de dades durant 300 segons
INFO -    Comença a conduir pel circuit!
INFO - 🏁 Volta completada: 95.34s
INFO - ⏱️  Temps transcorregut: 30s | Restant: 270s
INFO - 🏁 Volta completada: 93.12s
INFO - ⏱️  Temps transcorregut: 60s | Restant: 240s
...
INFO - === Analitzant Dades de la Sessió ===
INFO - 📊 Estadístiques Generals:
INFO -    • Total de mostres: 3000
INFO -    • Jugadors detectats: 1
INFO - 👤 Jugador 1:
INFO -    • Mostres: 3000
INFO -    • Velocitat màxima: 198.5 km/h
INFO -    • Velocitat mitjana: 142.3 km/h
INFO -    • RPM màxim: 7800
INFO - === Exportant Dades ===
INFO - ✓ Dades exportades a CSV: data/session_20240115_143022.csv
INFO - ✓ Dades exportades a JSON: data/session_20240115_143022.json
INFO - ✓ Sessió finalitzada correctament
```

## Analitzar les Dades Exportades

### Obrir el CSV amb Excel/LibreOffice

Les dades CSV es poden obrir directament amb Excel o LibreOffice Calc per fer anàlisi visual.

**Columnes del CSV**:
- `timestamp`: Moment de la mostra
- `player_id`: ID del jugador
- `speed`: Velocitat en km/h
- `rpm`: Revolucions per minut
- `gear`: Marxa actual
- `pos_x`, `pos_y`, `pos_z`: Posició al circuit
- `heading`: Direcció del vehicle

### Analitzar amb Python/Pandas

```python
import pandas as pd
import matplotlib.pyplot as plt

# Carregar dades
df = pd.read_csv('data/session_20240115_143022.csv')

# Estadístiques bàsiques
print(df.describe())

# Gràfic de velocitat vs temps
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['speed'])
plt.xlabel('Temps')
plt.ylabel('Velocitat (km/h)')
plt.title('Velocitat durant la Sessió')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('speed_analysis.png')
print("Gràfic guardat: speed_analysis.png")
```

## Exercicis Pràctics

### Exercici 1: Identificar la Millor Volta

Modifica el codi per identificar automàticament quina va ser la volta més ràpida de la sessió.

<details>
<summary>Veure solució</summary>

```python
def find_best_lap(collector):
    """Troba la millor volta de la sessió."""
    history = collector.get_telemetry_history()
    
    laps = [item for item in history if item.get('type') == 'lap']
    
    if not laps:
        return None
    
    best_lap = min(laps, key=lambda x: x.get('lap_time', float('inf')))
    return best_lap

# Afegir a la funció main():
best_lap = find_best_lap(collector)
if best_lap:
    logger.info(f"\n🏆 Millor volta: {best_lap['lap_time']:.2f}s")
```
</details>

### Exercici 2: Alertes de Límit de Velocitat

Afegeix un callback que generi una alerta quan la velocitat superi un llindar (per exemple, 200 km/h).

<details>
<summary>Veure solució</summary>

```python
def on_telemetry_update(telemetry_data):
    """Callback amb alerta de velocitat."""
    if telemetry_data:
        speed = telemetry_data.get('speed', 0)
        if speed > 200:
            logger.warning(f"⚠️  Velocitat alta: {speed:.1f} km/h!")
```
</details>

### Exercici 3: Exportació Personalitzada

Crea un format d'exportació personalitzat que només guardi les dades de les voltes completades.

<details>
<summary>Veure solució</summary>

```python
def export_laps_only(collector, filename):
    """Exporta només les dades de voltes."""
    history = collector.get_telemetry_history()
    laps = [item for item in history if item.get('type') == 'lap']
    
    json_exporter = JSONExporter(filename)
    json_exporter.export(laps)
    logger.info(f"✓ Voltes exportades: {filename}")
```
</details>

## Consells i Bones Pràctiques

### 💡 Consell 1: Durada de la Sessió
Per a sessions de pràctica, 5-10 minuts són suficients. Per carreres completes, ajusta `duration_seconds` segons necessitat.

### 💡 Consell 2: Gestió de Memòria
Si la sessió és molt llarga, considera utilitzar buffers amb límit de mida per evitar problemes de memòria:

```python
collector = TelemetryCollector(client, max_history=10000)
```

### 💡 Consell 3: Verificació de Dades
Sempre comprova que s'estan rebent dades abans d'exportar. Pots fer-ho amb:

```python
stats = collector.get_statistics()
if stats.get('total_samples', 0) == 0:
    logger.warning("No s'han recollit dades!")
```

### 💡 Consell 4: Gestió d'Errors
Utilitza sempre blocs try-except per gestionar errors de connexió o d'exportació.

## Problemes Comuns

### No es reben dades de telemetria

**Causa**: El vehicle està aturat o en parc tancat.

**Solució**: Condueix activament pel circuit. InSim només envia telemetria quan hi ha activitat.

### Fitxers no es guarden

**Causa**: Permisos d'escriptura o directori inexistent.

**Solució**: Verifica que el directori `data/` existeix i tens permisos d'escriptura.

### Connexió perduda durant la sessió

**Causa**: LFS tancat o pèrdua de connexió de xarxa.

**Solució**: El codi inclou gestió d'errors. Les dades recollides fins al moment es guardaran.

## Pròxims Passos

Ara que saps recollir dades d'una sessió, estàs preparat per:

1. **[Tutorial 2: Anàlisi de Voltes](02-lap-analysis.md)** - Aprèn a comparar voltes i identificar àrees de millora
2. **[Tutorial 3: Dashboard en Temps Real](03-real-time-dashboard.md)** - Crea un dashboard personalitzat
3. **[Tutorial 4: Anàlisi Avançada](04-advanced-analysis.md)** - Utilitza tècniques avançades d'anàlisi

## Recursos Addicionals

- [Documentació de TelemetryCollector](../api_reference.md#telemetrycollector)
- [Formats d'Exportació](../api_reference.md#export-formats)
- [Protocol InSim](../insim_protocol.md)
- [Exemples Avançats](../../examples/)

---

**¡Felicitats!** Has completat el teu primer tutorial. Ara tens les bases per començar a treballar amb telemetria de LFS! 🏎️

Per dubtes o problemes, consulta la [FAQ](../faq.md) o obre un [issue a GitHub](https://github.com/lfsplayer97/LFS-Ayats/issues).
