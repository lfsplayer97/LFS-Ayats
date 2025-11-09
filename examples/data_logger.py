"""
Data Logger Example
Exemple de logger de dades amb exportació.

Referència: https://en.lfsmanual.net/wiki/InSim.txt
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Afegir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection import InSimClient
from telemetry import TelemetryCollector
from export import CSVExporter, JSONExporter
from utils import setup_logger

# Configurar logging
logger = setup_logger("data_logger", "INFO")


def main():
    """Exemple de logger de dades."""
    logger.info("=== Data Logger LFS ===")
    
    # Configuració
    HOST = "127.0.0.1"
    PORT = 29999
    DURATION = 60  # segons
    
    # Crear directoris de sortida
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Crear client i connectar
        logger.info(f"Connectant a {HOST}:{PORT}...")
        client = InSimClient(host=HOST, port=PORT, app_name="DataLogger")
        client.connect()
        
        # Crear col·lector
        collector = TelemetryCollector(client)
        
        # Iniciar recollida
        logger.info(f"Recollint dades durant {DURATION} segons...")
        collector.start(interval=100)
        
        # Esperar
        time.sleep(DURATION)
        
        # Aturar recollida
        collector.stop()
        
        # Exportar dades
        logger.info("\nExportant dades...")
        
        for plid in collector.car_telemetry.keys():
            history = collector.get_telemetry_history(plid)
            
            if history:
                # Exportar a CSV
                csv_file = output_dir / f"telemetry_plid{plid}_{timestamp}.csv"
                csv_exporter = CSVExporter(str(csv_file))
                if csv_exporter.export(history):
                    logger.info(f"Dades exportades a {csv_file}")
                
                # Exportar a JSON
                json_file = output_dir / f"telemetry_plid{plid}_{timestamp}.json"
                json_exporter = JSONExporter(str(json_file))
                metadata = {
                    'plid': plid,
                    'duration': DURATION,
                    'sample_count': len(history)
                }
                if json_exporter.export(history, metadata):
                    logger.info(f"Dades exportades a {json_file}")
        
        # Desconnectar
        client.disconnect()
        logger.info("Finalitzat!")
        
    except ConnectionError as e:
        logger.error(f"Error de connexió: {e}")
        return 1
    
    except KeyboardInterrupt:
        logger.info("\nInterromput per l'usuari")
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
