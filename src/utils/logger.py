"""
Logger
Sistema de logging per a LFS-Ayats.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "lfs_ayats",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Configura el sistema de logging.

    Args:
        name: Nom del logger
        level: Nivell de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Fitxer de log (None per no usar fitxer)
        console: Mostrar logs a la consola
        log_format: Format dels logs

    Returns:
        logging.Logger: Logger configurat

    Exemple:
        >>> logger = setup_logger("lfs_ayats", "DEBUG", "app.log")
        >>> logger.info("Aplicació iniciada")
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Evitar duplicats
    if logger.handlers:
        logger.handlers.clear()

    # Format per defecte
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)

    # Handler de consola
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Handler de fitxer
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "lfs_ayats") -> logging.Logger:
    """
    Obté un logger existent.

    Args:
        name: Nom del logger

    Returns:
        logging.Logger: Logger
    """
    return logging.getLogger(name)


def create_session_logger(base_name: str = "lfs_ayats") -> logging.Logger:
    """
    Crea un logger per a una sessió amb timestamp.

    Args:
        base_name: Nom base del logger

    Returns:
        logging.Logger: Logger de sessió
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/{base_name}_{timestamp}.log"
    
    return setup_logger(
        name=f"{base_name}_{timestamp}",
        level="DEBUG",
        log_file=log_file,
        console=True
    )
