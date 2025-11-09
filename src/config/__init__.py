"""
Configuration Module
Gestió de configuració de l'aplicació
"""

__version__ = "0.1.0"

from .settings import Settings, load_config, save_config

__all__ = ["Settings", "load_config", "save_config"]
