# Guia de Testing

Aquesta guia explica com escriure i executar tests per LFS-Ayats.

## Tipus de Tests

### 1. Tests Unitaris (`tests/unit/`)
Testen funcions individuals de forma aïllada.

### 2. Tests d'Integració (`tests/integration/`)
Testen la interacció entre múltiples components.

### 3. Tests End-to-End (`tests/e2e/`)
Testen el sistema complet amb LFS real.

## Estructura de Tests

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
└── conftest.py  # Fixtures compartides
```

## Escriure Tests Unitaris

### Exemple Bàsic

```python
import pytest
from src.telemetry import TelemetryProcessor


class TestTelemetryProcessor:
    """Tests per TelemetryProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Fixture que crea un processor."""
        return TelemetryProcessor(max_speed=200.0)
    
    def test_validate_speed_with_valid_value(self, processor):
        """Test validació de velocitat vàlida."""
        # Arrange
        speed = 150.0
        
        # Act
        result = processor.validate_speed(speed)
        
        # Assert
        assert result is True
    
    def test_validate_speed_with_negative_value(self, processor):
        """Test validació de velocitat negativa."""
        # Arrange
        speed = -10.0
        
        # Act & Assert
        with pytest.raises(ValueError):
            processor.validate_speed(speed)
```

### Utilitzar Fixtures

```python
# conftest.py
import pytest
from src.connection import InSimClient


@pytest.fixture
def mock_client():
    """Client InSim mockat."""
    client = InSimClient(host="127.0.0.1", port=29999)
    # No connectar realment
    return client


@pytest.fixture
def sample_telemetry_data():
    """Dades de telemetria d'exemple."""
    return [
        {'speed': 100, 'rpm': 5000, 'gear': 3},
        {'speed': 120, 'rpm': 5500, 'gear': 4},
    ]


# test_file.py
def test_something(mock_client, sample_telemetry_data):
    """Test utilitzant fixtures."""
    # Utilitza mock_client i sample_telemetry_data
    pass
```

## Mocking

### Mock de Connexió de Xarxa

```python
from unittest.mock import Mock, patch, MagicMock

def test_connect_success():
    """Test connexió exitosa."""
    with patch('socket.socket') as mock_socket:
        # Configurar mock
        mock_socket.return_value.connect.return_value = None
        
        # Crear client
        client = InSimClient(host="127.0.0.1", port=29999)
        
        # Act
        result = client.connect()
        
        # Assert
        assert result is True
        mock_socket.return_value.connect.assert_called_once()
```

### Mock de Base de Dades

```python
def test_save_session(mocker):
    """Test guardar sessió."""
    # Mock de repository
    mock_repo = mocker.patch('src.database.repository.TelemetryRepository')
    mock_repo.return_value.create_session.return_value = Mock(id=1)
    
    # Act
    session_id = save_session(data)
    
    # Assert
    assert session_id == 1
    mock_repo.return_value.create_session.assert_called_once()
```

## Tests Parametritzats

```python
@pytest.mark.parametrize("speed,expected", [
    (0, True),
    (100, True),
    (200, True),
    (-10, False),
    (500, False),
])
def test_validate_speed_parametrized(processor, speed, expected):
    """Test validació amb múltiples valors."""
    if expected:
        assert processor.validate_speed(speed) is True
    else:
        with pytest.raises(ValueError):
            processor.validate_speed(speed)
```

## Tests Asíncrons

```python
import pytest
import asyncio


@pytest.mark.asyncio
async def test_async_telemetry_stream():
    """Test streaming asíncron de telemetria."""
    # Arrange
    collector = AsyncTelemetryCollector()
    
    # Act
    async for data in collector.stream():
        # Assert
        assert 'speed' in data
        break  # Test primer element només
```

## Markers (Etiquetes)

```python
# pytest.ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    network: Tests que requereixen xarxa
    slow: Tests lents (>1s)
    skip_ci: Skip en CI


# Utilitzar markers
@pytest.mark.unit
def test_fast_unit():
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_slow_integration():
    pass

@pytest.mark.skip_ci
def test_requires_lfs():
    """Aquest test requereix LFS executant."""
    pass
```

Executar per marker:
```bash
pytest -m unit          # Només unit tests
pytest -m "not slow"    # Excloure tests lents
pytest -m "integration and not network"
```

## Cobertura de Codi

### Configuració

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

### Executar amb Cobertura

```bash
# Generar report
pytest --cov=src --cov-report=html

# Veure report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Report en terminal
pytest --cov=src --cov-report=term-missing
```

### Objectius de Cobertura

- **Mínim acceptable**: 70%
- **Objectiu**: 80%
- **Ideal**: 90%+

Mòduls crítics (connexió, telemetria): 85%+

## Tests d'Integració

```python
import pytest
from src.connection import InSimClient
from src.telemetry import TelemetryCollector


@pytest.mark.integration
class TestTelemetryWorkflow:
    """Tests d'integració del workflow complet."""
    
    def test_full_telemetry_collection(self, mock_lfs_server):
        """Test recollida completa de telemetria."""
        # Arrange
        client = InSimClient(host="127.0.0.1", port=29999)
        collector = TelemetryCollector(client)
        
        # Act
        client.connect()
        client.initialize()
        collector.start()
        
        # Simular recepció de dades
        mock_lfs_server.send_telemetry_packet()
        
        # Assert
        data = collector.get_latest_telemetry()
        assert data is not None
        assert 'speed' in data
        
        # Cleanup
        collector.stop()
        client.disconnect()
```

## Fixtures Avançades

```python
# conftest.py
import pytest
from contextlib import contextmanager


@pytest.fixture(scope="session")
def database_engine():
    """Engine de DB per tots els tests."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(database_engine):
    """Sessió de DB per cada test."""
    Session = sessionmaker(bind=database_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def temp_data_dir(tmp_path):
    """Directori temporal per dades."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    yield data_dir
    # Cleanup automàtic per pytest
```

## Executar Tests

### Comandes Bàsiques

```bash
# Tots els tests
pytest

# Directori específic
pytest tests/unit/

# Fitxer específic
pytest tests/unit/test_collector.py

# Test específic
pytest tests/unit/test_collector.py::TestCollector::test_start

# Verbose
pytest -v

# Mostrar print statements
pytest -s

# Aturar al primer error
pytest -x

# Executar últims tests fallits
pytest --lf

# Executar tests en paral·lel (requereix pytest-xdist)
pytest -n auto
```

### Opcions Útils

```bash
# Debugger en error
pytest --pdb

# Mostrar durada de tests
pytest --durations=10

# Només tests modificats recentment
pytest --testmon

# Amb warnings
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

Comandes PDB:
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

## Bones Pràctiques

### 1. Tests Independents

```python
# ✅ Correcte - cada test és independent
def test_a():
    data = create_data()
    assert process(data) == expected

def test_b():
    data = create_data()  # Nova creació
    assert validate(data) is True

# ❌ Incorrecte - tests depenen entre si
shared_data = None

def test_create():
    global shared_data
    shared_data = create_data()

def test_process():
    assert process(shared_data) == expected  # Depèn de test_create
```

### 2. Tests Ràpids

```python
# ✅ Ràpid - utilitza mocks
def test_save_session(mock_db):
    session = save_session(data, mock_db)
    assert session.id is not None

# ❌ Lent - utilitza DB real
def test_save_session_slow():
    db = create_database()  # Lent
    session = save_session(data, db)
    assert session.id is not None
```

### 3. Assertions Clares

```python
# ✅ Missatge clar
assert len(results) == 5, f"Expected 5 results, got {len(results)}"

# ✅ Utilitzar funcions específiques
assert result is True  # En lloc de assert result == True
assert 'key' in dictionary
assert value is None

# ✅ pytest helpers
from pytest import approx
assert 0.1 + 0.2 == approx(0.3)
```

### 4. Setup i Teardown

```python
class TestCollector:
    def setup_method(self):
        """Executat abans de cada test."""
        self.collector = TelemetryCollector()
    
    def teardown_method(self):
        """Executat després de cada test."""
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

## Referències

- [Pytest Documentation](https://docs.pytest.org/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

Ara pots escriure tests professionals! ✅
