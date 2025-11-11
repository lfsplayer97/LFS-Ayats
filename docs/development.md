# Development Guide

This guide provides information for developers who want to contribute to or use LFS-Ayats.

## Development Environment Setup

### Requirements

- Python 3.8 or higher
- Git
- Live for Speed (optional for real testing)

### Installation

```bash
# Clone repository
git clone https://github.com/lfsplayer97/LFS-Ayats.git
cd LFS-Ayats

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -e .
```

## Project Structure

```
LFS-Ayats/
├── src/                    # Source code
│   ├── connection/        # InSim connection
│   ├── telemetry/         # Telemetry
│   ├── visualization/     # Visualization
│   ├── export/            # Export
│   ├── config/            # Configuration
│   └── utils/             # Utilities
├── tests/                 # Tests
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── examples/             # Examples
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

## Code Conventions

### Python Style (PEP 8)

We use Black for automatic formatting:

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

### Docstrings

We use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief function description.

    More detailed description if needed.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative

    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### Naming

- **Classes**: `PascalCase` (e.g., `InSimClient`)
- **Functions/methods**: `snake_case` (e.g., `send_packet`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_SPEED`)
- **Private variables**: `_leading_underscore` (e.g., `_internal_var`)

## Tests

### Running Tests

```bash
# All tests
pytest

# Tests with coverage
pytest --cov=src --cov-report=html

# Specific tests
pytest tests/unit/connection/
pytest tests/integration/

# Marked tests
pytest -m unit
pytest -m integration
```

### Writing Tests

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

### Test Fixtures

```python
# tests/fixtures/packets.py

def create_test_mci_packet():
    """Create a test MCI packet"""
    import struct
    return struct.pack("=4B", 8, 38, 0, 1)  # Simplified
```

## Developing New Modules

### 1. Planning

- Define module responsibility
- Identify dependencies
- Design public interface
- Consider testability

### 2. Implementation

```python
# src/new_module/__init__.py
"""
New Module
Module description.
"""

__version__ = "0.1.0"

from .main_class import MainClass

__all__ = ["MainClass"]
```

### 3. Documentation

- Complete docstrings
- Usage examples
- References to InSim documentation
- Update README.md if needed

### 4. Tests

- Unit tests for all public functions
- Integration tests if it interacts with other modules
- Coverage > 80%

## InSim Integration

### Adding Support for New Packet Type

1. **Update PacketType enum**:

```python
# src/connection/insim_client.py
class PacketType(IntEnum):
    # ... existing packets ...
    ISP_NEW = 99  # New type
```

2. **Add parser to PacketHandler**:

```python
# src/connection/packet_handler.py
def parse_new_packet(self, data: bytes) -> Optional[Dict[str, Any]]:
    """
    Parse an IS_NEW packet.
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_NEW
    """
    try:
        # Implement parsing according to structure
        unpacked = struct.unpack("=format", data)
        return {
            'field1': unpacked[0],
            'field2': unpacked[1],
        }
    except struct.error as e:
        logger.error(f"Error parsing IS_NEW: {e}")
        return None
```

3. **Add tests**:

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

# Create logger
logger = setup_logger("debug_session", level="DEBUG", log_file="debug.log")

# Use it
logger.debug("Debug message")
logger.info("Information")
logger.warning("Warning")
logger.error("Error")
```

### Inspecting Packets

```python
import struct

def inspect_packet(data: bytes):
    """Display packet contents"""
    print(f"Size: {len(data)} bytes")
    print(f"Hex: {data.hex()}")
    
    if len(data) >= 4:
        size, pkt_type, req_id, sub = struct.unpack("=4B", data[:4])
        print(f"Size: {size}, Type: {pkt_type}, ReqI: {req_id}, Sub: {sub}")
```

### Simulating LFS Server

For development without LFS:

```python
# scripts/mock_server.py
import socket
import struct

def mock_lfs_server(port=29999):
    """Mock LFS server for testing"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', port))
    sock.listen(1)
    
    print(f"Mock server listening on port {port}")
    
    conn, addr = sock.accept()
    print(f"Connection from {addr}")
    
    # Receive IS_ISI
    data = conn.recv(1024)
    print(f"Received: {len(data)} bytes")
    
    # Send IS_VER
    ver_packet = struct.pack(
        "=4B8s6sH",
        5, 2, 0, 0,
        b'0.6V\x00\x00\x00\x00',
        b'S2\x00\x00\x00\x00',
        9
    )
    conn.sendall(ver_packet)
    print("Sent IS_VER")
    
    # Keep connection...
```

## Development Workflow

### 1. Create Branch

```bash
git checkout -b feature/new-feature
```

### 2. Develop

- Write code
- Add tests
- Update documentation

### 3. Validate

```bash
# Format
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
git commit -m "feat: Add new feature

- Detailed description
- References to issues if applicable
"
```

### 5. Pull Request

- Push the branch
- Create PR with clear description
- Ensure tests pass
- Code review

## Best Practices

### Error Handling

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    # Handle error
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise  # Re-raise if cannot handle
```

### Context Managers

```python
# Prefer context managers for resources
with InSimClient() as client:
    client.initialize()
    # Use client...
# Connection closed automatically
```

### Type Hints

```python
from typing import List, Optional, Dict, Any

def process_data(
    data: List[CarTelemetry],
    filter_speed: Optional[float] = None
) -> Dict[str, Any]:
    """Always use type hints"""
    pass
```

### Code Documentation

- Docstrings for all public classes and functions
- Comments for complex logic
- References to InSim.txt when applicable
- Usage examples

## Resources

### Documentation
- [InSim Protocol](insim_protocol.md)
- [Packet Reference](packet_reference.md)
- [API Reference](api_reference.md)

### Tools
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing
- **Coverage**: Test coverage

### Community
- [LFS Forum](https://www.lfs.net/forum)
- [GitHub Issues](https://github.com/lfsplayer97/LFS-Ayats/issues)
