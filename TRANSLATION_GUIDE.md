# Translation Guide: Completing Catalan to English Translation

This guide provides detailed instructions for completing the translation of remaining Catalan content to English in the LFS-Ayats repository.

## Status Overview

### ✅ Completed (100%)
- [x] README.md (530 lines)
- [x] CONTRIBUTING.md (300 lines)
- [x] docs/development.md (430 lines)
- [x] examples/basic_connection.py (83 lines)
- [x] examples/data_logger.py (103 lines)

### ⚠️ Partially Completed (30-50%)
- [ ] src/connection/insim_client.py (~200 lines of Catalan remaining)
- [ ] src/connection/packet_handler.py (~100 lines of Catalan remaining)

### 📝 Not Started (0%)
- [ ] examples/telemetry_monitor.py
- [ ] examples/analysis_examples.py
- [ ] src/telemetry/collector.py
- [ ] src/telemetry/processor.py
- [ ] src/telemetry/__init__.py
- [ ] src/export/db_exporter.py
- [ ] src/config/settings.py
- [ ] src/analysis/sectors.py
- [ ] src/analysis/alerts.py
- [ ] src/analysis/anomaly.py
- [ ] src/__init__.py

## Common Catalan to English Translations

### Module/File Level
| Catalan | English |
|---------|---------|
| Gestió i processament | Handling and processing |
| Gestió de | Management of |
| Referència: | Reference: |
| Exemple de | Example of |

### Docstring Terms
| Catalan | English |
|---------|---------|
| Aquesta classe | This class |
| s'encarrega de | handles / is responsible for |
| Inicialitza | Initialize / Initializes |
| Registra | Register / Registers |
| Canvia | Change / Changes |
| Estableix | Establish / Establishes |
| Dispara | Trigger / Triggers |
| Executa | Execute / Executes |
| Envia | Send / Sends |
| Tanca | Close / Closes |
| Parseja | Parse / Parses |
| Gestiona | Handle / Handles / Manage / Manages |

### Common Words
| Catalan | English |
|---------|---------|
| connexió | connection |
| Connexió | Connection |
| telemetria | telemetry |
| Telemetria | Telemetry |
| processament | processing |
| Processament | Processing |
| recollida | collection |
| Recollida | Collection |
| màxim | maximum |
| Màxim | Maximum |
| automàtica | automatic |
| automàtic | automatic |
| Habilitar | Enable |
| deshabilitada | disabled |
| exitosa | successful |
| èxit | success |
| Error de | Error in / Connection error |
| d'intents | attempts |
| assolit | reached |
| fitxer | file |
| dades | data |
| paquets | packets |
| servidor | server |

### Comments
| Catalan | English |
|---------|---------|
| # Crear | # Create |
| # Connectar | # Connect |
| # Configuració | # Configuration |
| # Inicialitzar | # Initialize |
| # Rebre | # Receive |
| # Desconnectar | # Disconnect |
| # Afegir | # Add |
| # Actualitzar | # Update |
| # Comprovar | # Check |

### Logging Messages
| Catalan | English |
|---------|---------|
| Connectant a | Connecting to |
| establerta | established |
| inicialitzat | initialized |
| Rebent | Receiving |
| Desconnectat | Disconnected |
| Paquet rebut | Packet received |
| Tipus: | Type: |
| Mida: | Size: |
| Assegura't que | Make sure / Ensure that |
| està executant-se | is running |
| està habilitat | is enabled |
| Per habilitar | To enable |
| Interromput per | Interrupted by |
| l'usuari | user / the user |
| inesperat | unexpected |
| finalitzat | finished / completed |
| exportades | exported |

### Function Parameters
| Catalan | English |
|---------|---------|
| Nombre màxim d'intents | Maximum number of attempts |
| Retard inicial entre intents | Initial delay between attempts |
| Temps d'espera màxim | Maximum timeout |
| Interval entre | Interval between |
| Adreça IP | IP address |
| Contrasenya d'administrador | Admin password |

## Step-by-Step Translation Process

### 1. Identify Files with Catalan Content

```bash
# Find all Python files with Catalan content
cd /home/runner/work/LFS-Ayats/LFS-Ayats
grep -r "connexió\|telemetria\|processament\|recollida" --include="*.py" src/ examples/
```

### 2. Translation Priority Order

**Priority 1: User-Facing Files**
1. examples/telemetry_monitor.py
2. examples/analysis_examples.py

**Priority 2: Core Connection Module**
3. src/connection/insim_client.py (complete remaining)
4. src/connection/packet_handler.py (complete remaining)

**Priority 3: Telemetry Module**
5. src/telemetry/collector.py
6. src/telemetry/processor.py

**Priority 4: Other Modules**
7. src/export/db_exporter.py
8. src/config/settings.py
9. src/analysis/* files
10. src/__init__.py, src/telemetry/__init__.py

### 3. Translation Guidelines

**DO:**
- ✅ Translate all docstrings (module, class, function)
- ✅ Translate all inline comments
- ✅ Translate all user-facing strings (logger messages, error messages)
- ✅ Maintain technical accuracy
- ✅ Preserve code functionality
- ✅ Keep technical terms in English (InSim, TCP/UDP, packet names)
- ✅ Preserve markdown formatting in docstrings
- ✅ Keep references to official documentation

**DON'T:**
- ❌ Change variable names
- ❌ Change function names
- ❌ Modify code logic
- ❌ Remove or alter code structure
- ❌ Change technical terminology (e.g., "InSim" stays "InSim")
- ❌ Modify packet type names (e.g., IS_MCI, IS_VER)
- ❌ Change file names or directory structure

### 4. Example Translation

**Before (Catalan):**
```python
def process_telemetry(data: List[CarTelemetry]) -> ProcessedTelemetry:
    """
    Processa dades de telemetria.
    
    Aquesta funció s'encarrega de validar i processar les dades
    de telemetria rebudes del servidor LFS.
    
    Args:
        data: Llista de dades telemètriques
        
    Returns:
        Dades processades
        
    Raises:
        ValueError: Si les dades no són vàlides
    """
    # Validar dades
    if not data:
        raise ValueError("Dades buides")
    
    # Processar cada element
    logger.info("Processant telemetria...")
    return processed_data
```

**After (English):**
```python
def process_telemetry(data: List[CarTelemetry]) -> ProcessedTelemetry:
    """
    Process telemetry data.
    
    This function handles validation and processing of telemetry data
    received from the LFS server.
    
    Args:
        data: List of telemetry data
        
    Returns:
        Processed data
        
    Raises:
        ValueError: If data is invalid
    """
    # Validate data
    if not data:
        raise ValueError("Empty data")
    
    # Process each element
    logger.info("Processing telemetry...")
    return processed_data
```

### 5. Testing After Translation

After translating each file:

```bash
# Run tests for the specific module
pytest tests/unit/connection/ -v
pytest tests/unit/telemetry/ -v

# Run all tests
pytest

# Run linters
black src/ tests/ examples/
flake8 src/ tests/ examples/
mypy src/
```

### 6. Verification Checklist

For each translated file:
- [ ] All docstrings translated
- [ ] All comments translated
- [ ] All logger messages translated
- [ ] All error messages translated
- [ ] Technical terms preserved (InSim, packet types, etc.)
- [ ] Code functionality unchanged
- [ ] Tests pass
- [ ] Linters pass
- [ ] Professional English grammar and style

## Automated Translation Hints

### Using grep to find Catalan patterns:

```bash
# Find files with common Catalan words
grep -r "connexió\|telemetria\|processament" --include="*.py" src/

# Find Catalan docstrings
grep -r "Aquesta\|s'encarrega\|Inicialitza" --include="*.py" src/

# Find Catalan comments
grep -r "# Crear\|# Configuració\|# Inicialitzar" --include="*.py" src/

# Find Catalan logger messages
grep -r "logger.*Connectant\|logger.*establerta" --include="*.py" src/ examples/
```

### Using sed for batch replacements (use with caution):

```bash
# Example: Replace common comment patterns
sed -i 's/# Configuració/# Configuration/g' file.py
sed -i 's/# Crear /# Create /g' file.py

# Always verify changes with git diff after batch replacements
git diff file.py
```

## Common Translation Patterns

### Pattern 1: Class Docstrings
```python
# Before:
"""
Client per connectar-se i comunicar-se amb el servidor LFS.
"""

# After:
"""
Client to connect and communicate with the LFS server.
"""
```

### Pattern 2: Method Docstrings
```python
# Before:
def connect(self) -> bool:
    """
    Estableix la connexió amb el servidor.
    
    Returns:
        bool: True si la connexió és exitosa
    """

# After:
def connect(self) -> bool:
    """
    Establish connection with the server.
    
    Returns:
        bool: True if connection is successful
    """
```

### Pattern 3: Logger Messages
```python
# Before:
logger.info("Connectant a {host}:{port}...")
logger.error(f"Error de connexió: {e}")
logger.info("Connexió establerta!")

# After:
logger.info(f"Connecting to {host}:{port}...")
logger.error(f"Connection error: {e}")
logger.info("Connection established!")
```

### Pattern 4: Error Messages
```python
# Before:
raise ValueError("Dades no vàlides")
raise ConnectionError("Error de connexió al servidor")

# After:
raise ValueError("Invalid data")
raise ConnectionError("Connection error to server")
```

## File-Specific Notes

### src/connection/insim_client.py
- Contains ~200 lines of Catalan in detailed docstrings
- Focus on class docstring, method docstrings, and inline comments
- Many technical InSim protocol details - preserve accuracy
- Reference: https://en.lfsmanual.net/wiki/InSim.txt

### src/connection/packet_handler.py
- Contains ~100 lines of Catalan
- Focus on packet parsing method docstrings
- Maintain packet structure documentation accuracy

### examples/telemetry_monitor.py
- User-facing example file
- Translate all comments and logger messages
- Keep code simple and well-documented in English

### examples/analysis_examples.py
- Advanced analysis examples
- Translate technical explanations clearly
- Maintain accuracy of analysis terminology

## Quality Standards

### Professional English
- Use proper grammar and spelling
- Be concise and clear
- Use active voice when possible
- Maintain consistent terminology

### Technical Accuracy
- Verify InSim protocol references
- Keep packet structure documentation accurate
- Maintain unit consistency (km/h, RPM, etc.)
- Preserve technical term meanings

### Code Quality
- Follow PEP 8 style guide
- Use Google-style docstrings
- Keep comments helpful and relevant
- Avoid redundant comments

## Getting Help

If unsure about a translation:
1. Check official LFS documentation: https://en.lfsmanual.net/wiki/InSim.txt
2. Review already-translated similar sections
3. Consult the common translations table above
4. Ask in GitHub issue or discussion

## Final Verification

Before marking translation complete:

```bash
# 1. Run all tests
pytest

# 2. Check for remaining Catalan content
grep -r "connexió\|telemetria\|processament\|recollida\|dades\|Configuració" \
  --include="*.py" --include="*.md" src/ examples/ docs/

# 3. Run linters
black --check src/ tests/ examples/
flake8 src/ tests/ examples/
mypy src/

# 4. Verify documentation builds (if applicable)
# 5. Review git diff for accuracy
git diff --stat
```

## Conclusion

This translation work ensures LFS-Ayats is accessible to the international open-source community and maintains professional standards for technical documentation. Thank you for contributing to this effort!
