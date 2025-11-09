# Guia de Contribució

Gràcies pel teu interès en contribuir a LFS-Ayats! Aquest document proporciona directrius per contribuir al projecte.

## Codi de Conducta

- Sigues respectuós i professional
- Accepta crítiques constructives
- Centra't en el millor per la comunitat
- Mostra empatia cap altres membres

## Com Contribuir

### Reportar Bugs

Si trobes un bug, si us plau obre un issue amb:

1. **Títol descriptiu**
2. **Descripció detallada** del problema
3. **Passos per reproduir** el bug
4. **Comportament esperat** vs comportament actual
5. **Entorn**: Versió de Python, OS, versió de LFS
6. **Logs o captures** si escau

### Suggerir Millores

Per suggerir noves funcionalitats:

1. **Comprova** que no existeixi ja un issue similar
2. **Descriu** la funcionalitat desitjada
3. **Explica** el cas d'ús i beneficis
4. **Proposa** una implementació si és possible

### Pull Requests

#### Preparació

1. **Fork** el repositori
2. **Crea una branca** des de `main`:
   ```bash
   git checkout -b feature/nom-funcionalitat
   # o
   git checkout -b fix/nom-bug
   ```

#### Desenvolupament

1. **Segueix** les convencions de codi (PEP 8)
2. **Escriu tests** per la teva funcionalitat
3. **Actualitza documentació** si cal
4. **Assegura't** que tots els tests passen:
   ```bash
   pytest --cov=src
   ```

#### Format i Qualitat

```bash
# Formatar codi
black src/ tests/

# Comprovar estil
flake8 src/ tests/

# Type checking
mypy src/
```

#### Commit

Utilitza missatges de commit descriptius:

```
feat: Afegir suport per paquet IS_NEW

- Implementar parser per IS_NEW
- Afegir tests unitaris
- Actualitzar documentació

Refs: #123
```

Prefixos recomanats:
- `feat:` Nova funcionalitat
- `fix:` Correcció de bug
- `docs:` Canvis en documentació
- `test:` Afegir o modificar tests
- `refactor:` Refactorització de codi
- `style:` Canvis de format (no afecten funcionalitat)
- `perf:` Millores de rendiment

#### Crear Pull Request

1. **Push** la teva branca al teu fork
2. **Obre** un Pull Request a `main`
3. **Descriu** els canvis realitzats
4. **Referencia** issues relacionats
5. **Espera** el review

### Review de Codi

Els PRs seran revisats per:

- **Qualitat del codi**: Seguiment de convencions
- **Tests**: Cobertura adequada
- **Documentació**: Clara i completa
- **Funcionalitat**: Funciona com s'espera
- **Impacte**: No trenca funcionalitat existent

## Estàndards de Codi

### Python (PEP 8)

```python
# Bones pràctiques

# 1. Imports organitzats
import os
import sys
from typing import List, Optional

from src.connection import InSimClient
from src.telemetry import TelemetryCollector

# 2. Constants en majúscules
MAX_SPEED = 150.0
DEFAULT_PORT = 29999

# 3. Funcions amb type hints
def process_telemetry(data: List[CarTelemetry]) -> ProcessedTelemetry:
    """
    Processa telemetria.
    
    Args:
        data: Llista de telemetria
        
    Returns:
        Dades processades
    """
    pass

# 4. Classes amb docstrings
class TelemetryProcessor:
    """
    Processador de telemetria.
    
    Attributes:
        max_speed: Velocitat màxima permesa
    """
    
    def __init__(self, max_speed: float = 150.0):
        self.max_speed = max_speed
```

### Documentació

Tots els mòduls, classes i funcions públiques han de tenir docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Descripció breu.

    Descripció detallada si necessària. Pot incloure múltiples
    paràgrafs per explicar el comportament.

    Args:
        param1: Descripció del primer paràmetre
        param2: Descripció del segon paràmetre

    Returns:
        Descripció del valor retornat

    Raises:
        ValueError: Quan param2 és negatiu
        ConnectionError: Si no es pot connectar

    Example:
        >>> function_name("test", 42)
        True
        
    Referència: https://en.lfsmanual.net/wiki/InSim.txt#section
    """
    pass
```

### Tests

Escriu tests per:

- Totes les funcions públiques
- Casos límit i errors
- Integració entre mòduls

```python
import pytest
from src.module import MyClass


class TestMyClass:
    """Test cases for MyClass"""

    @pytest.fixture
    def instance(self):
        """Fixture for MyClass instance"""
        return MyClass()

    def test_basic_functionality(self, instance):
        """Test basic functionality"""
        result = instance.method()
        assert result is not None

    def test_error_handling(self, instance):
        """Test error handling"""
        with pytest.raises(ValueError):
            instance.method_with_error()

    @pytest.mark.integration
    def test_integration(self, instance):
        """Test integration with other modules"""
        # Test d'integració
        pass
```

## Estructura de Projecte

Quan afegeixis nova funcionalitat, segueix aquesta estructura:

```
src/
└── new_module/
    ├── __init__.py          # Exporta API pública
    ├── main_class.py        # Classe principal
    ├── helpers.py           # Funcions auxiliars
    └── constants.py         # Constants del mòdul

tests/
└── unit/
    └── new_module/
        ├── __init__.py
        ├── test_main_class.py
        └── test_helpers.py

docs/
└── new_module.md            # Documentació del mòdul

examples/
└── new_module_example.py    # Exemple d'ús
```

## Aspectes Específics d'InSim

### Implementar Nou Tipus de Paquet

1. **Consulta InSim.txt**: https://en.lfsmanual.net/wiki/InSim.txt
2. **Afegeix el tipus** a `PacketType` enum
3. **Implementa el parser** a `PacketHandler`
4. **Escriu tests** amb paquets de prova
5. **Documenta** l'estructura i ús

### Telemetria

- Considera rendiment (alta freqüència de dades)
- Valida dades rebudes
- Gestiona errors de xarxa
- Documenta unitats de mesura

### Referències

Inclou sempre referències a la documentació oficial:

```python
"""
Implementació del paquet IS_MCI.

Referència: https://en.lfsmanual.net/wiki/InSim.txt#IS_MCI
"""
```

## Llicència

En contribuir, acceptes que les teves contribucions es llicenciïn sota la llicència MIT del projecte.

## Preguntes?

Si tens preguntes:

1. Consulta la [documentació](docs/)
2. Busca a [issues existents](https://github.com/lfsplayer97/LFS-Ayats/issues)
3. Obre un nou issue amb etiqueta "question"

## Reconeixements

Les contribucions seran reconegudes:

- Al README.md
- A les release notes
- Al fitxer AUTHORS (si existeix)

Gràcies per ajudar a millorar LFS-Ayats! 🏎️
