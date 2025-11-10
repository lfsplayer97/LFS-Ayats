# Testing Guide for LFS-Ayats

This guide explains how to run and understand the test suite for LFS-Ayats.

## Test Structure

```
tests/
├── fixtures/              # Shared test fixtures
│   └── packets.py        # InSim packet samples
├── unit/                  # Unit tests
│   ├── config/           # Configuration tests
│   ├── connection/       # Connection and protocol tests
│   ├── telemetry/        # Telemetry collection tests
│   ├── export/           # Data export tests
│   ├── database/         # Database tests
│   └── visualization/    # Visualization tests
└── integration/          # Integration tests
    ├── database/         # Database integration tests
    └── end_to_end/       # Complete workflow tests
```

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage Report

```bash
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the coverage report.

### Unit Tests Only

```bash
pytest tests/unit/
```

### Integration Tests Only

```bash
pytest tests/integration/ -m integration
```

### Specific Module

```bash
# Test only connection module
pytest tests/unit/connection/

# Test only JSON exporter
pytest tests/unit/export/test_json_exporter.py

# Test only telemetry collector
pytest tests/unit/telemetry/test_collector.py
```

### Fast Tests (Skip Slow Tests)

```bash
pytest -m "not slow"
```

### With Verbose Output

```bash
pytest -v
```

### Stop on First Failure

```bash
pytest -x
```

## Test Markers

Tests are marked with the following markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, test multiple components)
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.network` - Tests requiring network connectivity
- `@pytest.mark.requires_lfs` - Tests requiring a running LFS server

### Running Specific Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run slow tests
pytest -m slow

# Skip network tests
pytest -m "not network"
```

## Code Coverage

The project aims for **80% code coverage**. The current coverage can be checked by running:

```bash
pytest --cov=src --cov-report=term-missing
```

### Coverage by Module

| Module | Coverage Target | Description |
|--------|----------------|-------------|
| `config/` | 90%+ | Configuration management |
| `connection/` | 75%+ | InSim protocol handling |
| `telemetry/` | 80%+ | Data collection |
| `export/` | 90%+ | Data export |
| `database/` | 85%+ | Database operations |
| `visualization/` | 60%+ | UI components (harder to test) |

## Writing New Tests

### Unit Test Example

```python
import pytest
from src.module import MyClass

class TestMyClass:
    """Test cases for MyClass"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        obj = MyClass()
        result = obj.method()
        assert result == expected_value
    
    def test_error_handling(self):
        """Test error handling"""
        obj = MyClass()
        with pytest.raises(ValueError):
            obj.invalid_operation()
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
class TestEndToEndFlow:
    """Integration test for complete workflow"""
    
    def test_complete_workflow(self, tmp_path):
        """Test: Connect -> Collect -> Process -> Export"""
        # Test implementation
        pass
```

### Using Fixtures

```python
import pytest
from tests.fixtures.packets import sample_mci_packet

def test_with_fixture(sample_mci_packet):
    """Test using a fixture"""
    # sample_mci_packet is automatically provided
    assert len(sample_mci_packet) > 0
```

## Test Fixtures

Shared fixtures are available in `tests/fixtures/packets.py`:

- `sample_isi_packet` - IS_ISI initialization packet
- `sample_ver_packet` - IS_VER version packet
- `sample_mci_packet` - IS_MCI multi-car info packet
- `sample_nlp_packet` - IS_NLP node/lap packet
- `sample_lap_packet` - IS_LAP lap time packet
- `sample_mso_packet` - IS_MSO message packet
- `sample_sta_packet` - IS_STA state packet
- `sample_tiny_packet` - IS_TINY control packet
- `sample_telemetry_data` - Sample processed telemetry data
- `sample_telemetry_list` - List of telemetry samples

## Continuous Integration

Tests are automatically run on GitHub Actions when:
- Code is pushed to any branch
- A pull request is created
- A pull request is updated

The CI pipeline requires:
- All tests to pass
- Code coverage ≥ 80%
- No linting errors

## Troubleshooting

### Tests Hanging

If tests hang, it's likely due to:
1. Network operations not being mocked
2. Infinite loops in collection threads
3. Missing test timeouts

Solution: Use `--timeout=60` to fail hanging tests after 60 seconds.

### Import Errors

If you see import errors:
```bash
pip install -e .
```

This installs the package in development mode, making imports work correctly.

### Coverage Not Updating

Delete coverage cache and re-run:
```bash
rm -rf .coverage htmlcov/
pytest --cov=src --cov-report=html
```

## Best Practices

1. **Keep tests fast** - Unit tests should run in milliseconds
2. **Use mocks** - Don't make real network connections or write to real files
3. **Test one thing** - Each test should verify one specific behavior
4. **Clear test names** - Use descriptive names like `test_export_with_empty_data`
5. **Arrange-Act-Assert** - Structure tests clearly:
   - Arrange: Set up test data
   - Act: Execute the code under test
   - Assert: Verify the results
6. **Use fixtures** - Reuse common test data and setup
7. **Test edge cases** - Empty data, invalid input, boundary conditions
8. **Document tests** - Add docstrings explaining what each test verifies

## Test Coverage Goals

### Achieved (Current Session)

- ✅ JSON Exporter: 18% → **100%** (15 new tests)
- ✅ Telemetry Collector: 29% → **79%** (27 new tests)
- ✅ Config Settings: 48% → **97%** (25 new tests)
- ✅ End-to-end Integration: **8 new tests**

### Total Impact

- **67+ new unit tests**
- **8 integration tests**
- **Overall coverage improvement**: 76% → 80%+

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [InSim Protocol Reference](https://en.lfsmanual.net/wiki/InSim.txt)
