"""
LFS-Ayats Package
Modular telemetry system for Live for Speed
"""

__version__ = "0.1.0"
__author__ = "lfsplayer97"

# Exportar mòduls principals
from . import connection
from . import telemetry
from . import export
from . import config
from . import utils

__all__ = [
    "connection",
    "telemetry",
    "export",
    "config",
    "utils",
]
