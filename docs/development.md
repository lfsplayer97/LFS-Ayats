# Guia de Desenvolupament

Aquesta guia proporciona informació per desenvolupadors que volen contribuir o utilitzar LFS-Ayats.

## Configuració de l'Entorn de Desenvolupament

### Requisits

- Python 3.8 o superior
- Git
- Live for Speed (opcional per proves reals)

### Instal·lació

```bash
# Clonar repositori
git clone https://github.com/lfsplayer97/LFS-Ayats.git
cd LFS-Ayats

# Crear entorn virtual
python -m venv venv

# Activar entorn virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instal·lar dependències de desenvolupament
pip install -r requirements.txt
pip install -e .
```

## Estructura del Projecte

```
LFS-Ayats/
├── src/                    # Codi font
│   ├── connection/        # Connexió InSim
│   ├── telemetry/         # Telemetria
│   ├── visualization/     # Visualització
│   ├── export/            # Exportació
│   ├── config/            # Configuració
│   └── utils/             # Utilitats
├── tests/                 # Tests
│   ├── unit/             # Tests unitaris
│   └── integration/      # Tests d'integració
├── examples/             # Exemples
├── docs/                 # Documentació
└── scripts/              # Scripts d'utilitat
```

## Convencions de Codi

### Estil Python (PEP 8)

Utilitzem Black per formatació automàtica:

```bash
# Formatar codi
black src/ tests/

# Comprovar estil
flake8 src/ tests/

# Type checking
mypy src/
```

### Docstrings

Utilitzem docstrings estil Google:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Breu descripció de la funció.

    Descripció més detallada si cal.

    Args:
        param1: Descripció del paràmetre 1
        param2: Descripció del paràmetre 2

    Returns:
        Descripció del valor de retorn

    Raises:
        ValueError: Quan param2 és negatiu

    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### Nomenclatura

- **Classes**: `PascalCase` (ex: `InSimClient`)
- **Funcions/mètodes**: `snake_case` (ex: `send_packet`)
- **Constants**: `UPPER_SNAKE_CASE` (ex: `MAX_SPEED`)
- **Variables privades**: `_leading_underscore` (ex: `_internal_var`)

## Tests

### Executar Tests

```bash
# Tots els tests
pytest

# Tests amb cobertura
pytest --cov=src --cov-report=html

# Tests específics
pytest tests/unit/connection/
pytest tests/integration/

# Tests marcats
pytest -m unit
pytest -m integration
```

### Escriure Tests

```python
import pytest
from src.connection import InSimClient


class TestInSimClient:
    """Test cases for InSimClient"""

    def test_init(self):
        """Test client initialization"""
        client = InSimClient(host="127.0.0.1", port=29999)
        assert client.host == "127.0.0.1"
        assert client.port == 29999

    @pytest.fixture
    def client(self):
        """Fixture for InSimClient"""
        return InSimClient()

    def test_connect(self, client, mocker):
        """Test connection with mocking"""
        mock_socket = mocker.patch('socket.socket')
        client.connect()
        assert client.connected
```

### Fixtures de Test

```python
# tests/fixtures/packets.py

def create_test_mci_packet():
    """Create a test MCI packet"""
    import struct
    return struct.pack("=4B", 8, 38, 0, 1)  # Simplified
```

## Desenvolupament de Nous Mòduls

### 1. Planificació

- Definir la responsabilitat del mòdul
- Identificar dependències
- Dissenyar interfície pública
- Considerar testabilitat

### 2. Implementació

```python
# src/new_module/__init__.py
"""
New Module
Descripció del mòdul.
"""

__version__ = "0.1.0"

from .main_class import MainClass

__all__ = ["MainClass"]
```

### 3. Documentació

- Docstrings completes
- Exemples d'ús
- Referències a documentació InSim
- Actualitzar README.md si cal

### 4. Tests

- Tests unitaris per totes les funcions públiques
- Tests d'integració si interactua amb altres mòduls
- Cobertura > 80%

## Integració amb InSim

### Afegir Suport per Nou Tipus de Paquet

1. **Actualitzar PacketType enum**:

```python
# src/connection/insim_client.py
class PacketType(IntEnum):
    # ... paquets existents ...
    ISP_NEW = 99  # Nou tipus
```

2. **Afegir parser al PacketHandler**:

```python
# src/connection/packet_handler.py
def parse_new_packet(self, data: bytes) -> Optional[Dict[str, Any]]:
    """
    Parseja un paquet IS_NEW.
    
    Referència: https://en.lfsmanual.net/wiki/InSim.txt#IS_NEW
    """
    try:
        # Implementar parsing segons estructura
        unpacked = struct.unpack("=format", data)
        return {
            'field1': unpacked[0],
            'field2': unpacked[1],
        }
    except struct.error as e:
        logger.error(f"Error parsejant IS_NEW: {e}")
        return None
```

3. **Afegir tests**:

```python
# tests/unit/connection/test_packet_handler.py
def test_parse_new_packet(self):
    """Test parsing IS_NEW packet"""
    handler = PacketHandler()
    packet = struct.pack("=format", value1, value2)
    
    info = handler.parse_new_packet(packet)
    
    assert info is not None
    assert info['field1'] == value1
```

## Debugging

### Logging

```python
from src.utils import setup_logger

# Crear logger
logger = setup_logger("debug_session", level="DEBUG", log_file="debug.log")

# Utilitzar
logger.debug("Missatge de debug")
logger.info("Informació")
logger.warning("Advertència")
logger.error("Error")
```

### Inspeccionar Paquets

```python
import struct

def inspect_packet(data: bytes):
    """Mostra contingut d'un paquet"""
    print(f"Mida: {len(data)} bytes")
    print(f"Hex: {data.hex()}")
    
    if len(data) >= 4:
        size, pkt_type, req_id, sub = struct.unpack("=4B", data[:4])
        print(f"Size: {size}, Type: {pkt_type}, ReqI: {req_id}, Sub: {sub}")
```

### Simular Servidor LFS

Per desenvolupament sense LFS:

```python
# scripts/mock_server.py
import socket
import struct

def mock_lfs_server(port=29999):
    """Mock LFS server per tests"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', port))
    sock.listen(1)
    
    print(f"Mock server listening on port {port}")
    
    conn, addr = sock.accept()
    print(f"Connection from {addr}")
    
    # Rebre IS_ISI
    data = conn.recv(1024)
    print(f"Received: {len(data)} bytes")
    
    # Enviar IS_VER
    ver_packet = struct.pack(
        "=4B8s6sH",
        5, 2, 0, 0,
        b'0.6V\x00\x00\x00\x00',
        b'S2\x00\x00\x00\x00',
        9
    )
    conn.sendall(ver_packet)
    print("Sent IS_VER")
    
    # Mantenir connexió...
```

## Workflow de Desenvolupament

### 1. Crear Branca

```bash
git checkout -b feature/nova-funcionalitat
```

### 2. Desenvolupar

- Escriure codi
- Afegir tests
- Actualitzar documentació

### 3. Validar

```bash
# Formatar
black src/ tests/

# Lint
flake8 src/ tests/

# Tests
pytest --cov=src

# Type check
mypy src/
```

### 4. Commit

```bash
git add .
git commit -m "feat: Afegir nova funcionalitat

- Descripció detallada
- Referències a issues si escau
"
```

### 5. Pull Request

- Push de la branca
- Crear PR amb descripció clara
- Assegurar que els tests passen
- Review de codi

## Bones Pràctiques

### Gestió d'Errors

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Error específic: {e}")
    # Gestionar error
except Exception as e:
    logger.error(f"Error inesperat: {e}", exc_info=True)
    raise  # Re-llançar si no es pot gestionar
```

### Context Managers

```python
# Preferir context managers per recursos
with InSimClient() as client:
    client.initialize()
    # Utilitzar client...
# Connexió tancada automàticament
```

### Type Hints

```python
from typing import List, Optional, Dict, Any

def process_data(
    data: List[CarTelemetry],
    filter_speed: Optional[float] = None
) -> Dict[str, Any]:
    """Sempre utilitzar type hints"""
    pass
```

### Documentació de Codi

- Docstrings per totes les classes i funcions públiques
- Comentaris per lògica complexa
- Referències a InSim.txt quan apliqui
- Exemples d'ús

## Recursos

### Documentació
- [InSim Protocol](insim_protocol.md)
- [Packet Reference](packet_reference.md)
- [API Reference](api_reference.md)

### Eines
- **Black**: Formatació de codi
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing
- **Coverage**: Cobertura de tests

### Comunitat
- [LFS Forum](https://www.lfs.net/forum)
- [GitHub Issues](https://github.com/lfsplayer97/LFS-Ayats/issues)
