"""
Settings
Configuració de l'aplicació LFS-Ayats.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from src.utils import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionSettings:
    """Configuració de connexió InSim"""
    host: str = "127.0.0.1"
    port: int = 29999
    admin_password: str = ""
    app_name: str = "LFS-Ayats"
    udp: bool = False
    timeout: float = 5.0


@dataclass
class TelemetrySettings:
    """Configuració de telemetria"""
    interval: int = 100  # ms
    max_history: int = 10000  # mostres
    auto_export: bool = False
    export_interval: int = 60  # segons


@dataclass
class ExportSettings:
    """Configuració d'exportació"""
    format: str = "csv"  # csv, json, both
    output_dir: str = "data"
    filename_template: str = "telemetry_{timestamp}"
    auto_compression: bool = False


@dataclass
class VisualizationSettings:
    """Configuració de visualització"""
    refresh_rate: int = 10  # Hz
    show_realtime: bool = True
    plot_history: int = 100  # mostres


@dataclass
class LoggingSettings:
    """Configuració de logging"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    console: bool = True


@dataclass
class Settings:
    """
    Configuració principal de l'aplicació.
    
    Exemple:
        >>> settings = Settings()
        >>> settings.connection.host = "192.168.1.100"
        >>> save_config(settings, "config.yaml")
    """
    connection: ConnectionSettings = None
    telemetry: TelemetrySettings = None
    export: ExportSettings = None
    visualization: VisualizationSettings = None
    logging: LoggingSettings = None

    def __post_init__(self):
        """Inicialitza subconfiguracions si són None"""
        if self.connection is None:
            self.connection = ConnectionSettings()
        if self.telemetry is None:
            self.telemetry = TelemetrySettings()
        if self.export is None:
            self.export = ExportSettings()
        if self.visualization is None:
            self.visualization = VisualizationSettings()
        if self.logging is None:
            self.logging = LoggingSettings()

    def to_dict(self) -> Dict[str, Any]:
        """Converteix la configuració a diccionari"""
        return {
            'connection': asdict(self.connection),
            'telemetry': asdict(self.telemetry),
            'export': asdict(self.export),
            'visualization': asdict(self.visualization),
            'logging': asdict(self.logging),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Crea una configuració des d'un diccionari"""
        return cls(
            connection=ConnectionSettings(**data.get('connection', {})),
            telemetry=TelemetrySettings(**data.get('telemetry', {})),
            export=ExportSettings(**data.get('export', {})),
            visualization=VisualizationSettings(**data.get('visualization', {})),
            logging=LoggingSettings(**data.get('logging', {})),
        )


def load_config(filename: str = "config.yaml") -> Settings:
    """
    Carrega la configuració des d'un fitxer YAML.

    Args:
        filename: Nom del fitxer de configuració

    Returns:
        Settings: Objecte de configuració

    Raises:
        FileNotFoundError: Si el fitxer no existeix
    """
    config_path = Path(filename)
    
    if not config_path.exists():
        logger.warning(f"Fitxer de configuració no trobat: {filename}")
        logger.info("Utilitzant configuració per defecte")
        return Settings()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        settings = Settings.from_dict(data)
        logger.info(f"Configuració carregada des de {filename}")
        return settings

    except yaml.YAMLError as e:
        logger.error(f"Error llegint YAML: {e}")
        raise
    except Exception as e:
        logger.error(f"Error carregant configuració: {e}")
        raise


def save_config(settings: Settings, filename: str = "config.yaml") -> bool:
    """
    Desa la configuració a un fitxer YAML.

    Args:
        settings: Objecte de configuració
        filename: Nom del fitxer de sortida

    Returns:
        bool: True si s'ha desat correctament
    """
    try:
        config_path = Path(filename)
        
        # Crear directori si no existeix
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(settings.to_dict(), f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Configuració desada a {filename}")
        return True

    except Exception as e:
        logger.error(f"Error desant configuració: {e}")
        return False


def create_default_config(filename: str = "config.yaml") -> Settings:
    """
    Crea un fitxer de configuració per defecte.

    Args:
        filename: Nom del fitxer de sortida

    Returns:
        Settings: Configuració per defecte
    """
    settings = Settings()
    save_config(settings, filename)
    logger.info(f"Configuració per defecte creada: {filename}")
    return settings
