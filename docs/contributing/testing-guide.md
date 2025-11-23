# Testing Guide

This guide explains how to write and run tests for LFS-Ayats.

## Types of Tests

### 1. Unit Tests (`tests/unit/`)
Test individual functions in isolation.

### 2. Integration Tests (`tests/integration/`)
Test the interaction between multiple components.

### 3. End-to-End Tests (`tests/e2e/`)
Test the complete system with real LFS.

## Test Structure

```
tests/
├── unit/
│   ├── connection/
│   │   ├── test_insim_client.py
│   │   └── test_packet_handler.py
│   ├── telemetry/
│   │   ├── test_collector.py
│   │   └── test_processor.py
│   └── export/
│       ├── test_csv_exporter.py
│       └── test_json_exporter.py
├── integration/
│   ├── test_full_workflow.py
│   └── test_api_integration.py
├── fixtures/
│   ├── sample_packets.py
│   └── mock_data.json
└── conftest.py  # Shared fixtures
```

## Writing Unit Tests

### Basic Example

```python
import pytest
from src.telemetry import TelemetryProcessor


class TestTelemetryProcessor:
    """Tests for TelemetryProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Fixture that creates a processor."""
        return TelemetryProcessor(max_speed=200.0)
    
    def test_validate_speed_with_valid_value(self, processor):
        """Test validation of valid speed."""
        # Arrange
        speed = 150.0
        
        # Act
        result = processor.validate_speed(speed)
        
        # Assert
        assert result is True
    
    def test_validate_speed_with_negative_value(self, processor):
        """Test validation of negative speed."""
        # Arrange
        speed = -10.0
        
        # Act & Assert
        with pytest.raises(ValueError):
            processor.validate_speed(speed)
```

### Using Fixtures

```python
# conftest.py
import pytest
from src.connection import InSimClient


@pytest.fixture
def mock_client():
    """Mocked InSim client."""
    client = InSimClient(host="127.0.0.1", port=29999)
    # Don't actually connect
    return client


@pytest.fixture
def sample_telemetry_data():
    """Sample telemetry data."""
    return [
        {'speed': 100, 'rpm': 5000, 'gear': 3},
        {'speed': 120, 'rpm': 5500, 'gear': 4},
    ]


# test_file.py
def test_something(mock_client, sample_telemetry_data):
    """Test using fixtures."""
    # Use mock_client and sample_telemetry_data
    pass
```

## Mocking

### Network Connection Mock

```python
from unittest.mock import Mock, patch, MagicMock

def test_connect_success():
    """Test successful connection."""
    with patch('socket.socket') as mock_socket:
        # Configure mock
        mock_socket.return_value.connect.return_value = None
        
        # Create client
        client = InSimClient(host="127.0.0.1", port=29999)
        
        # Act
        result = client.connect()
        
        # Assert
        assert result is True
        mock_socket.return_value.connect.assert_called_once()
```

### Database Mock

```python
def test_save_session(mocker):
    """Test save session."""
    # Mock repository
    mock_repo = mocker.patch('src.database.repository.TelemetryRepository')
    mock_repo.return_value.create_session.return_value = Mock(id=1)
    
    # Act
    session_id = save_session(data)
    
    # Assert
    assert session_id == 1
    mock_repo.return_value.create_session.assert_called_once()
```

## Parametrized Tests

```python
@pytest.mark.parametrize("speed,expected", [
    (0, True),
    (100, True),
    (200, True),
    (-10, False),
    (500, False),
])
def test_validate_speed_parametrized(processor, speed, expected):
    """Test validation with multiple values."""
    if expected:
        assert processor.validate_speed(speed) is True
    else:
        with pytest.raises(ValueError):
            processor.validate_speed(speed)
```

## Asynchronous Tests

```python
import pytest
import asyncio


@pytest.mark.asyncio
async def test_async_telemetry_stream():
    """Test asynchronous telemetry streaming."""
    # Arrange
    collector = AsyncTelemetryCollector()
    
    # Act
    async for data in collector.stream():
        # Assert
        assert 'speed' in data
        break  # Test first element only
```

## Markers (Labels)

```python
# pytest.ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    network: Tests requiring network
    slow: Slow tests (>1s)
    skip_ci: Skip in CI


# Using markers
@pytest.mark.unit
def test_fast_unit():
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_slow_integration():
    pass

@pytest.mark.skip_ci
def test_requires_lfs():
    """This test requires LFS running."""
    pass
```

Run by marker:
```bash
pytest -m unit          # Only unit tests
pytest -m "not slow"    # Exclude slow tests
pytest -m "integration and not network"
```

## Code Coverage

### Configuration

```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

### Run with Coverage

```bash
# Generate report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Terminal report
pytest --cov=src --cov-report=term-missing
```

### Coverage Goals

- **Minimum acceptable**: 70%
- **Target**: 80%
- **Ideal**: 90%+

Critical modules (connection, telemetry): 85%+

## Integration Tests

```python
import pytest
from src.connection import InSimClient
from src.telemetry import TelemetryCollector


@pytest.mark.integration
class TestTelemetryWorkflow:
    """Integration tests for complete workflow."""
    
    def test_full_telemetry_collection(self, mock_lfs_server):
        """Test complete telemetry collection."""
        # Arrange
        client = InSimClient(host="127.0.0.1", port=29999)
        collector = TelemetryCollector(client)
        
        # Act
        client.connect()
        client.initialize()
        collector.start()
        
        # Simulate data reception
        mock_lfs_server.send_telemetry_packet()
        
        # Assert
        data = collector.get_latest_telemetry()
        assert data is not None
        assert 'speed' in data
        
        # Cleanup
        collector.stop()
        client.disconnect()
```

## Advanced Fixtures

```python
# conftest.py
import pytest
from contextlib import contextmanager


@pytest.fixture(scope="session")
def database_engine():
    """DB engine for all tests."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(database_engine):
    """DB session for each test."""
    Session = sessionmaker(bind=database_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporary directory for data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    yield data_dir
    # Automatic cleanup by pytest
```

## Running Tests

### Basic Commands

```bash
# All tests
pytest

# Specific directory
pytest tests/unit/

# Specific file
pytest tests/unit/test_collector.py

# Specific test
pytest tests/unit/test_collector.py::TestCollector::test_start

# Verbose
pytest -v

# Show print statements
pytest -s

# Stop at first error
pytest -x

# Run last failed tests
pytest --lf

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Useful Options

```bash
# Debugger on error
pytest --pdb

# Show test duration
pytest --durations=10

# Only recently modified tests
pytest --testmon

# With warnings
pytest -W all

# HTML report
pytest --html=report.html
```

## Debugging Tests

### PDB (Python Debugger)

```python
def test_something():
    data = process_data()
    
    import pdb; pdb.set_trace()  # Breakpoint
    
    assert data is not None
```

PDB Commands:
- `n` - Next line
- `s` - Step into
- `c` - Continue
- `l` - List code
- `p variable` - Print variable
- `q` - Quit

### VS Code Debugging

`.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "${file}",
                "-v",
                "-s"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

## Best Practices

### 1. Independent Tests

```python
# ✅ Correct - each test is independent
def test_a():
    data = create_data()
    assert process(data) == expected

def test_b():
    data = create_data()  # New creation
    assert validate(data) is True

# ❌ Incorrect - tests depend on each other
shared_data = None

def test_create():
    global shared_data
    shared_data = create_data()

def test_process():
    assert process(shared_data) == expected  # Depends on test_create
```

### 2. Fast Tests

```python
# ✅ Fast - uses mocks
def test_save_session(mock_db):
    session = save_session(data, mock_db)
    assert session.id is not None

# ❌ Slow - uses real DB
def test_save_session_slow():
    db = create_database()  # Slow
    session = save_session(data, db)
    assert session.id is not None
```

### 3. Clear Assertions

```python
# ✅ Clear message
assert len(results) == 5, f"Expected 5 results, got {len(results)}"

# ✅ Use specific functions
assert result is True  # Instead of assert result == True
assert 'key' in dictionary
assert value is None

# ✅ pytest helpers
from pytest import approx
assert 0.1 + 0.2 == approx(0.3)
```

### 4. Setup and Teardown

```python
class TestCollector:
    def setup_method(self):
        """Run before each test."""
        self.collector = TelemetryCollector()
    
    def teardown_method(self):
        """Run after each test."""
        self.collector.stop()
        self.collector = None
    
    def test_start(self):
        self.collector.start()
        assert self.collector.is_running()
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

Now you can write professional tests! ✅
