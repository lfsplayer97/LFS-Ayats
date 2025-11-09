"""
Telemetry Monitor Example
Exemple de monitor de telemetria en temps real.

Referència: https://en.lfsmanual.net/wiki/InSim.txt
"""

import sys
import time
from pathlib import Path

# Afegir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection import InSimClient
from telemetry import TelemetryCollector, TelemetryProcessor
from utils import setup_logger

# Configurar logging
logger = setup_logger("telemetry_monitor", "INFO")


def display_telemetry(telemetry):
    """Mostra telemetria a la consola."""
    print(f"\n=== Telemetria - PLID {telemetry.plid} ===")
    print(f"Volta: {telemetry.lap}")
    print(f"Node: {telemetry.node}")
    print(f"Velocitat: {telemetry.speed:.2f} m/s ({telemetry.speed * 3.6:.2f} km/h)")
    print(f"Posició: X={telemetry.position.get('x', 0)}, Y={telemetry.position.get('y', 0)}, Z={telemetry.position.get('z', 0)}")


def main():
    """Exemple de monitor de telemetria."""
    logger.info("=== Monitor de Telemetria LFS ===")
    
    # Configuració
    HOST = "127.0.0.1"
    PORT = 29999
    DURATION = 30  # segons
    
    try:
        # Crear client i connectar
        logger.info(f"Connectant a {HOST}:{PORT}...")
        client = InSimClient(host=HOST, port=PORT, app_name="TelemetryMon")
        client.connect()
        
        # Crear col·lector de telemetria
        collector = TelemetryCollector(client)
        
        # Registrar callback per actualitzacions de cotxe
        collector.register_callback('car_update', display_telemetry)
        
        # Iniciar recollida
        logger.info(f"Recollint telemetria durant {DURATION} segons...")
        collector.start(interval=100)  # 10 Hz
        
        # Esperar
        time.sleep(DURATION)
        
        # Aturar recollida
        collector.stop()
        
        # Mostrar estadístiques
        stats = collector.get_statistics()
        logger.info("\n=== Estadístiques ===")
        logger.info(f"Jugadors rastrejar: {stats['total_players']}")
        logger.info(f"Total mostres: {stats['total_samples']}")
        
        for plid, count in stats['players'].items():
            logger.info(f"  PLID {plid}: {count} mostres")
            
            # Processar telemetria
            processor = TelemetryProcessor()
            history = collector.get_telemetry_history(plid)
            processed = processor.process_telemetry(history)
            
            logger.info(f"    Velocitat mitjana: {processed.avg_speed:.2f} m/s")
            logger.info(f"    Velocitat màxima: {processed.max_speed:.2f} m/s")
            logger.info(f"    Distància total: {processed.total_distance:.2f} m")
        
        # Desconnectar
        client.disconnect()
        logger.info("Finalitzat!")
        
    except ConnectionError as e:
        logger.error(f"Error de connexió: {e}")
        logger.info("Assegura't que LFS està executant-se amb InSim habilitat")
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
