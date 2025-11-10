# Estàndards de Codi

Convencions i estàndards de codi per contribuir a LFS-Ayats.

## Estil General: PEP 8

Seguim [PEP 8](https://pep8.org/) amb algunes adaptacions.

## Nomenclatura

### Classes
```python
# PascalCase
class InSimClient:
    pass

class TelemetryCollector:
    pass
```

### Funcions i Mètodes
```python
# snake_case
def connect_to_server():
    pass

def get_latest_telemetry():
    pass
```

### Constants
```python
# UPPER_SNAKE_CASE
MAX_SPEED = 500.0
DEFAULT_PORT = 29999
PACKET_SIZE = 1024
```

### Variables Privades
```python
# _leading_underscore
class MyClass:
    def __init__(self):
        self._internal_state = {}
        self.__very_private = None
```

## Formatació

### Line Length
- **Màxim 88 caràcters** (convenció de Black)
- Excepcions per URLs llargues o strings

### Imports
```python
# 1. Standard library
import os
import sys
from typing import List, Dict, Optional

# 2. Third party
import numpy as np
import pandas as pd
from fastapi import FastAPI

# 3. Local/aplicació
from src.connection import InSimClient
from src.telemetry import TelemetryCollector
```

### Espais en Blanc
```python
# Correcte
def function(a, b, c=None):
    result = a + b
    return result

# Incorrecte
def function( a,b,c = None ):
    result=a+b
    return result
```

## Type Hints

**Obligatori** per totes les funcions públiques:

```python
from typing import List, Dict, Optional, Union

def process_telemetry(
    data: List[Dict[str, float]], 
    filter_speed: Optional[float] = None
) -> Dict[str, any]:
    """Processa dades telemètriques."""
    pass

class TelemetryProcessor:
    def __init__(self, max_speed: float = 150.0) -> None:
        self.max_speed: float = max_speed
    
    def validate(self, speed: float) -> bool:
        return 0 <= speed <= self.max_speed
```

## Docstrings: Google Style

### Funcions
```python
def calculate_lap_time(lap_data: List[Dict], method: str = "sum") -> float:
    """
    Calcula el temps total d'una volta.
    
    Aquesta funció analitza les dades telemètriques d'una volta i calcula
    el temps total utilitzant el mètode especificat.
    
    Args:
        lap_data: Llista de diccionaris amb dades de telemetria.
            Cada diccionari ha de contenir almenys 'timestamp'.
        method: Mètode de càlcul ('sum', 'interval', 'official').
            Per defecte 'sum'.
    
    Returns:
        Temps de volta en segons. Retorna float('inf') si no hi ha dades.
    
    Raises:
        ValueError: Si method no és vàlid.
        KeyError: Si falta camp 'timestamp' a les dades.
    
    Example:
        >>> lap_data = [{'timestamp': '2024-01-01 10:00:00'}, ...]
        >>> calculate_lap_time(lap_data)
        95.342
        
    Note:
        El mètode 'official' utilitza el temps del paquet IS_LAP quan disponible.
    
    Reference:
        https://en.lfsmanual.net/wiki/InSim.txt#IS_LAP
    """
    if method not in ('sum', 'interval', 'official'):
        raise ValueError(f"Invalid method: {method}")
    
    # Implementació...
    pass
```

### Classes
```python
class TelemetryCollector:
    """
    Recull telemetria en temps real de LFS.
    
    Aquesta classe gestiona la recollida contínua de dades telemètriques
    des d'un servidor LFS via protocol InSim. Utilitza un thread separat
    per evitar bloquejar l'aplicació principal.
    
    Attributes:
        client: Client InSim connectat al servidor.
        max_history: Nombre màxim de mostres a mantenir en memòria.
        callbacks: Diccionari de callbacks per esdeveniments.
        telemetry_history: Històric de telemetria per jugador.
    
    Example:
        >>> client = InSimClient(host="127.0.0.1", port=29999)
        >>> collector = TelemetryCollector(client)
        >>> collector.start()
        >>> # ... conduir en LFS ...
        >>> data = collector.get_latest_telemetry()
        >>> collector.stop()
    """
    
    def __init__(self, client: InSimClient, max_history: int = 10000):
        """
        Inicialitza el col·lector.
        
        Args:
            client: Client InSim ja connectat.
            max_history: Màxim nombre de mostres a guardar.
        """
        self.client = client
        self.max_history = max_history
```

### Mòduls
```python
"""
Mòdul de connexió InSim.

Aquest mòdul proporciona classes per gestionar la comunicació amb
Live for Speed mitjançant el protocol InSim.

Classes:
    InSimClient: Client TCP/UDP per connexió InSim.
    PacketHandler: Parsejador de paquets InSim.

Reference:
    https://en.lfsmanual.net/wiki/InSim.txt
"""
```

## Comentaris

### Quan Comentar

✅ **Comentar**:
- Algoritmes complexos
- Workarounds per bugs coneguts
- Referències a issues o documentació
- TODO/FIXME/NOTE

❌ **No comentar**:
- Codi evident
- Paràfrasis del codi
- Codi comentat (eliminar-lo)

### Exemples

```python
# ✅ Bon comentari
# Workaround per bug en InSim 0.6V on IS_MCI pot contenir dades corruptes
# Vegeu: https://github.com/lfsplayer97/LFS-Ayats/issues/42
if packet_type == PacketType.IS_MCI:
    data = self._sanitize_mci_data(data)

# TODO(username): Implementar suport per IS_NLP
# FIXME: Aquest càlcul no és precís per circuits amb desnivell
# NOTE: Aquest mètode és costós, considerar caching

# ❌ Mal comentari
# Suma a i b
result = a + b

# Retorna True si la velocitat és vàlida
return 0 <= speed <= 500
```

## Gestió d'Errors

### Excepcions Específiques

```python
# Correcte
try:
    speed = float(data['speed'])
except KeyError:
    logger.error("Missing 'speed' field in telemetry data")
    raise
except ValueError:
    logger.error(f"Invalid speed value: {data.get('speed')}")
    raise

# Incorrecte
try:
    speed = float(data['speed'])
except Exception:  # Massa genèric
    pass  # No capturar sense gestionar
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

# Nivells apropiats
logger.debug("Raw packet: %s", raw_data)  # Detalls tècnics
logger.info("Connected to server")        # Esdeveniments normals
logger.warning("High memory usage: %d MB", mem_usage)  # Situacions anòmales
logger.error("Failed to parse packet", exc_info=True)  # Errors recuperables
logger.critical("Database corruption detected")  # Errors crítics
```

## Testing

### Nomenclatura de Tests

```python
def test_<funcionalitat>_<condició>_<resultat_esperat>():
    pass

# Exemples
def test_connect_with_valid_credentials_succeeds():
    pass

def test_validate_speed_with_negative_value_raises_error():
    pass

def test_get_telemetry_when_empty_returns_none():
    pass
```

### Estructura AAA

```python
def test_calculate_lap_time():
    # Arrange
    lap_data = [
        {'timestamp': '2024-01-01 10:00:00.000'},
        {'timestamp': '2024-01-01 10:01:35.342'}
    ]
    
    # Act
    result = calculate_lap_time(lap_data)
    
    # Assert
    assert result == 95.342
    assert isinstance(result, float)
```

## Bones Pràctiques

### 1. DRY (Don't Repeat Yourself)

```python
# ❌ Incorrecte
def get_session_stats(session_id):
    session = db.query(Session).filter_by(id=session_id).first()
    # ...

def delete_session(session_id):
    session = db.query(Session).filter_by(id=session_id).first()
    # ...

# ✅ Correcte
def _get_session(session_id):
    """Helper per obtenir sessió."""
    return db.query(Session).filter_by(id=session_id).first()

def get_session_stats(session_id):
    session = _get_session(session_id)
    # ...

def delete_session(session_id):
    session = _get_session(session_id)
    # ...
```

### 2. Single Responsibility

```python
# ❌ Massa responsabilitats
def process_and_save_telemetry(data):
    # Valida dades
    validated = validate(data)
    # Calcula derivades
    processed = calculate_derivatives(validated)
    # Guarda a DB
    save_to_database(processed)
    # Notifica subscriptors
    notify_subscribers(processed)
    return processed

# ✅ Una responsabilitat per funció
def process_telemetry(data):
    validated = validate(data)
    return calculate_derivatives(validated)

def save_telemetry(data):
    save_to_database(data)

def notify_telemetry_update(data):
    notify_subscribers(data)
```

### 3. Immutabilitat Quan Possible

```python
# ✅ Preferir retornar nou objecte
def add_timestamp(data: Dict) -> Dict:
    return {**data, 'timestamp': datetime.now()}

# En lloc de modificar in-place
def add_timestamp(data: Dict) -> None:
    data['timestamp'] = datetime.now()
```

### 4. List/Dict Comprehensions

```python
# ✅ Clar i concís
speeds = [sample['speed'] for sample in telemetry if sample['speed'] > 0]

# ❌ Menys pythonic
speeds = []
for sample in telemetry:
    if sample['speed'] > 0:
        speeds.append(sample['speed'])
```

### 5. Context Managers

```python
# ✅ Amb context manager
with open('data.json', 'r') as f:
    data = json.load(f)

# ❌ Sense context manager
f = open('data.json', 'r')
data = json.load(f)
f.close()
```

## Checklist Pre-commit

- [ ] Codi formatat amb Black
- [ ] Flake8 passa sense errors
- [ ] Type hints afegits
- [ ] Docstrings complets
- [ ] Tests escrits i passen
- [ ] No hi ha codi comentat
- [ ] Imports organitzats
- [ ] Logs apropiats
- [ ] Documentació actualitzada

## Eines Recomanades

```bash
# Formatació automàtica
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Sort imports
isort src/ tests/

# Complexity
radon cc src/ -a

# Security
bandit -r src/
```

## Referències

- [PEP 8](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Black Documentation](https://black.readthedocs.io/)
- [Type Hints PEP 484](https://peps.python.org/pep-0484/)

---

Seguint aquests estàndards mantenim un codi net i consistent! ✨
