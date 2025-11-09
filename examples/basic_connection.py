"""
Basic Connection Example
Exemple bàsic de connexió a LFS mitjançant InSim.

Referència: https://en.lfsmanual.net/wiki/InSim.txt
"""

import sys
import time
from pathlib import Path

# Afegir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection import InSimClient, PacketHandler
from utils import setup_logger

# Configurar logging
logger = setup_logger("basic_connection", "DEBUG")


def main():
    """Exemple bàsic de connexió."""
    logger.info("=== Exemple Bàsic de Connexió InSim ===")
    
    # Configuració
    HOST = "127.0.0.1"  # Localhost
    PORT = 29999        # Port InSim per defecte
    
    try:
        # Crear client InSim
        logger.info(f"Connectant a {HOST}:{PORT}...")
        client = InSimClient(
            host=HOST,
            port=PORT,
            admin_password="",
            app_name="BasicExample"
        )
        
        # Connectar
        client.connect()
        logger.info("Connexió establerta!")
        
        # Inicialitzar InSim
        client.initialize()
        logger.info("InSim inicialitzat!")
        
        # Rebre alguns paquets
        logger.info("Rebent paquets durant 10 segons...")
        handler = PacketHandler()
        
        start_time = time.time()
        while time.time() - start_time < 10:
            packet = client.receive_packet(timeout=1.0)
            if packet:
                info = handler.parse_packet(packet)
                if info:
                    logger.info(f"Paquet rebut - Tipus: {info.type}, Mida: {info.size}")
        
        # Desconnectar
        client.disconnect()
        logger.info("Desconnectat!")
        
    except ConnectionError as e:
        logger.error(f"Error de connexió: {e}")
        logger.info("Assegura't que LFS està executant-se i InSim està habilitat")
        logger.info("Per habilitar InSim: /insim 29999 a LFS")
        return 1
    
    except KeyboardInterrupt:
        logger.info("Interromput per l'usuari")
        return 0
    
    except Exception as e:
        logger.error(f"Error inesperat: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
