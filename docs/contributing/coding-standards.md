# Coding Standards

Conventions and coding standards for contributing to LFS-Ayats.

## General Style: PEP 8

We follow [PEP 8](https://pep8.org/) with some adaptations.

## Naming Conventions

### Classes
```python
# PascalCase
class InSimClient:
    pass

class TelemetryCollector:
    pass
```

### Functions and Methods
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

### Private Variables
```python
# _leading_underscore
class MyClass:
    def __init__(self):
        self._internal_state = {}
        self.__very_private = None
```

## Formatting

### Line Length
- **Maximum 88 characters** (Black convention)
- Exceptions for long URLs or strings

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

# 3. Local/application
from src.connection import InSimClient
from src.telemetry import TelemetryCollector
```

### Whitespace
```python
# Correct
def function(a, b, c=None):
    result = a + b
    return result

# Incorrect
def function( a,b,c = None ):
    result=a+b
    return result
```

## Type Hints

**Required** for all public functions:

```python
from typing import List, Dict, Optional, Union

def process_telemetry(
    data: List[Dict[str, float]], 
    filter_speed: Optional[float] = None
) -> Dict[str, any]:
    """Process telemetry data."""
    pass

class TelemetryProcessor:
    def __init__(self, max_speed: float = 150.0) -> None:
        self.max_speed: float = max_speed
    
    def validate(self, speed: float) -> bool:
        return 0 <= speed <= self.max_speed
```

## Docstrings: Google Style

### Functions
```python
def calculate_lap_time(lap_data: List[Dict], method: str = "sum") -> float:
    """
    Calculate the total lap time.
    
    This function analyzes telemetry data from a lap and calculates
    the total time using the specified method.
    
    Args:
        lap_data: List of dictionaries with telemetry data.
            Each dictionary must contain at least 'timestamp'.
        method: Calculation method ('sum', 'interval', 'official').
            Defaults to 'sum'.
    
    Returns:
        Lap time in seconds. Returns float('inf') if no data available.
    
    Raises:
        ValueError: If method is not valid.
        KeyError: If 'timestamp' field is missing in the data.
    
    Example:
        >>> lap_data = [{'timestamp': '2024-01-01 10:00:00'}, ...]
        >>> calculate_lap_time(lap_data)
        95.342
        
    Note:
        The 'official' method uses the time from IS_LAP packet when available.
    
    Reference:
        https://en.lfsmanual.net/wiki/InSim.txt#IS_LAP
    """
    if method not in ('sum', 'interval', 'official'):
        raise ValueError(f"Invalid method: {method}")
    
    # Implementation...
    pass
```

### Classes
```python
class TelemetryCollector:
    """
    Collect telemetry in real-time from LFS.
    
    This class manages continuous telemetry data collection
    from an LFS server via InSim protocol. It uses a separate thread
    to avoid blocking the main application.
    
    Attributes:
        client: InSim client connected to the server.
        max_history: Maximum number of samples to keep in memory.
        callbacks: Dictionary of callbacks for events.
        telemetry_history: Telemetry history per player.
    
    Example:
        >>> client = InSimClient(host="127.0.0.1", port=29999)
        >>> collector = TelemetryCollector(client)
        >>> collector.start()
        >>> # ... drive in LFS ...
        >>> data = collector.get_latest_telemetry()
        >>> collector.stop()
    """
    
    def __init__(self, client: InSimClient, max_history: int = 10000):
        """
        Initialize the collector.
        
        Args:
            client: InSim client already connected.
            max_history: Maximum number of samples to store.
        """
        self.client = client
        self.max_history = max_history
```

### Modules
```python
"""
InSim connection module.

This module provides classes to manage communication with
Live for Speed via the InSim protocol.

Classes:
    InSimClient: TCP/UDP client for InSim connection.
    PacketHandler: InSim packet parser.

Reference:
    https://en.lfsmanual.net/wiki/InSim.txt
"""
```

## Comments

### When to Comment

✅ **Comment**:
- Complex algorithms
- Workarounds for known bugs
- References to issues or documentation
- TODO/FIXME/NOTE

❌ **Don't comment**:
- Obvious code
- Paraphrasing the code
- Commented-out code (delete it)

### Examples

```python
# ✅ Good comment
# Workaround for bug in InSim 0.6V where IS_MCI may contain corrupt data
# See: https://github.com/lfsplayer97/LFS-Ayats/issues/42
if packet_type == PacketType.IS_MCI:
    data = self._sanitize_mci_data(data)

# TODO(username): Implement support for IS_NLP
# FIXME: This calculation is not accurate for tracks with elevation changes
# NOTE: This method is expensive, consider caching

# ❌ Bad comment
# Add a and b
result = a + b

# Returns True if speed is valid
return 0 <= speed <= 500
```

## Error Handling

### Specific Exceptions

```python
# Correct
try:
    speed = float(data['speed'])
except KeyError:
    logger.error("Missing 'speed' field in telemetry data")
    raise
except ValueError:
    logger.error(f"Invalid speed value: {data.get('speed')}")
    raise

# Incorrect
try:
    speed = float(data['speed'])
except Exception:  # Too generic
    pass  # Don't catch without handling
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

# Appropriate levels
logger.debug("Raw packet: %s", raw_data)  # Technical details
logger.info("Connected to server")        # Normal events
logger.warning("High memory usage: %d MB", mem_usage)  # Abnormal situations
logger.error("Failed to parse packet", exc_info=True)  # Recoverable errors
logger.critical("Database corruption detected")  # Critical errors
```

## Testing

### Test Naming

```python
def test_<functionality>_<condition>_<expected_result>():
    pass

# Examples
def test_connect_with_valid_credentials_succeeds():
    pass

def test_validate_speed_with_negative_value_raises_error():
    pass

def test_get_telemetry_when_empty_returns_none():
    pass
```

### AAA Structure

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

## Best Practices

### 1. DRY (Don't Repeat Yourself)

```python
# ❌ Incorrect
def get_session_stats(session_id):
    session = db.query(Session).filter_by(id=session_id).first()
    # ...

def delete_session(session_id):
    session = db.query(Session).filter_by(id=session_id).first()
    # ...

# ✅ Correct
def _get_session(session_id):
    """Helper to get session."""
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
# ❌ Too many responsibilities
def process_and_save_telemetry(data):
    # Validate data
    validated = validate(data)
    # Calculate derivatives
    processed = calculate_derivatives(validated)
    # Save to DB
    save_to_database(processed)
    # Notify subscribers
    notify_subscribers(processed)
    return processed

# ✅ One responsibility per function
def process_telemetry(data):
    validated = validate(data)
    return calculate_derivatives(validated)

def save_telemetry(data):
    save_to_database(data)

def notify_telemetry_update(data):
    notify_subscribers(data)
```

### 3. Immutability When Possible

```python
# ✅ Prefer returning new object
def add_timestamp(data: Dict) -> Dict:
    return {**data, 'timestamp': datetime.now()}

# Instead of modifying in-place
def add_timestamp(data: Dict) -> None:
    data['timestamp'] = datetime.now()
```

### 4. List/Dict Comprehensions

```python
# ✅ Clear and concise
speeds = [sample['speed'] for sample in telemetry if sample['speed'] > 0]

# ❌ Less pythonic
speeds = []
for sample in telemetry:
    if sample['speed'] > 0:
        speeds.append(sample['speed'])
```

### 5. Context Managers

```python
# ✅ With context manager
with open('data.json', 'r') as f:
    data = json.load(f)

# ❌ Without context manager
f = open('data.json', 'r')
data = json.load(f)
f.close()
```

## Pre-commit Checklist

- [ ] Code formatted with Black
- [ ] Flake8 passes without errors
- [ ] Type hints added
- [ ] Complete docstrings
- [ ] Tests written and passing
- [ ] No commented-out code
- [ ] Imports organized
- [ ] Appropriate logs
- [ ] Documentation updated

## Recommended Tools

```bash
# Automatic formatting
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

## References

- [PEP 8](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Black Documentation](https://black.readthedocs.io/)
- [Type Hints PEP 484](https://peps.python.org/pep-0484/)

---

Following these standards keeps our code clean and consistent! ✨
