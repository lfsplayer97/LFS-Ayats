# Configuració d'Entorn de Desenvolupament

Guia completa per configurar l'entorn de desenvolupament de LFS-Ayats.

## Prerequisits

- **Python 3.8+** instal·lat
- **Git** instal·lat
- **Editor de codi** (VS Code recomanat)
- **Live for Speed** (opcional per testing real)

## Pas 1: Fork i Clonar

### 1.1 Fork del Repositori

1. Ves a https://github.com/lfsplayer97/LFS-Ayats
2. Fes clic a "Fork" a la part superior dreta
3. Escull el teu compte de GitHub

### 1.2 Clonar el Fork

```bash
git clone https://github.com/TU_USUARIO/LFS-Ayats.git
cd LFS-Ayats

# Afegir upstream per sincronitzar
git remote add upstream https://github.com/lfsplayer97/LFS-Ayats.git
```

## Pas 2: Entorn Virtual

### Linux/Mac

```bash
# Crear entorn virtual
python3 -m venv venv

# Activar
source venv/bin/activate

# Verificar
which python  # Ha de mostrar ruta dins de venv/
```

### Windows

```powershell
# Crear entorn virtual
python -m venv venv

# Activar
venv\Scripts\activate

# Verificar
where python  # Ha de mostrar ruta dins de venv\
```

## Pas 3: Instal·lar Dependències

```bash
# Dependències de producció i desenvolupament
pip install -r requirements.txt

# Instal·lar paquet en mode editable
pip install -e .

# Verificar instal·lació
pip list | grep lfs-ayats
```

## Pas 4: Configuració d'Editor

### VS Code (Recomanat)

Instal·la extensions:
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
code --install-extension ms-python.flake8
```

Configuració (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false
}
```

### PyCharm

1. Obre el projecte
2. File > Settings > Project > Python Interpreter
3. Afegeix intèrpret: `venv/bin/python`
4. Configura Black com a formatter
5. Activa Flake8 per linting

## Pas 5: Pre-commit Hooks

```bash
# Instal·lar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Executar manualment
pre-commit run --all-files
```

Configuració (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

## Pas 6: Executar Tests

```bash
# Tots els tests
pytest

# Amb cobertura
pytest --cov=src --cov-report=html

# Tests específics
pytest tests/unit/
pytest tests/integration/

# Tests ràpids (sense integració)
pytest -m "not integration"
```

## Pas 7: Configuració Local

```bash
# Copiar configuració d'exemple
cp config.example.yaml config.yaml

# Editar per les teves necessitats
nano config.yaml  # o vim, code, etc.
```

## Pas 8: Verificar Configuració

Executa l'script de verificació per assegurar que tot està configurat correctament:

```bash
# Des del directori arrel del projecte
python scripts/verify_setup.py
```

Aquest script verifica:
- ✓ Versió de Python (3.8+)
- ✓ Entorn virtual actiu
- ✓ Dependències principals instal·lades
- ✓ Paquet instal·lat en mode editable
- ✓ Estructura del projecte completa
- ✓ Fitxer de configuració existent
- ✓ Tests es poden executar

**Sortida esperada:**
```
============================================================
  LFS-Ayats Setup Verification
============================================================

✓ [PASS] Python version: 3.12.3
✓ [PASS] Virtual environment detected
✓ [PASS] Core dependencies installed
✓ [PASS] Package installed in editable mode
✓ [PASS] Project structure is complete
✓ [PASS] Configuration file exists
✓ [PASS] Tests can be executed

============================================================
  Summary
============================================================

Checks passed: 7/7
✓ All checks passed! Your environment is properly configured.
```

Si alguna verificació falla, l'script mostrarà els passos per corregir-ho.

## Workflow de Desenvolupament

### 1. Crear Branca

```bash
# Sincronitzar amb upstream
git fetch upstream
git merge upstream/main

# Crear branca per feature
git checkout -b feature/nova-funcionalitat

# O per bug fix
git checkout -b fix/corregir-bug
```

### 2. Fer Canvis

```bash
# Editar fitxers...

# Formatar codi
black src/ tests/

# Verificar estil
flake8 src/ tests/

# Type checking
mypy src/
```

### 3. Executar Tests

```bash
# Tests unitaris
pytest tests/unit/

# Tests complets
pytest --cov=src
```

### 4. Commit

```bash
# Afegir fitxers
git add .

# Commit amb missatge descriptiu
git commit -m "feat: afegir nova funcionalitat X"

# Pre-commit hooks s'executaran automàticament
```

### 5. Push i Pull Request

```bash
# Push a fork
git push origin feature/nova-funcionalitat

# Crear PR des de GitHub web interface
```

## Solució de Problemes

### Error: "pip: command not found"

```bash
# Instal·lar pip
python -m ensurepip --upgrade
```

### Error: "ModuleNotFoundError: No module named 'src'"

```bash
# Reinstal·lar en mode editable
pip install -e .
```

### Tests fallen amb ImportError

```bash
# Verificar PYTHONPATH
echo $PYTHONPATH

# Afegir si necessari
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Pre-commit hooks fallen

```bash
# Reinstal·lar hooks
pre-commit uninstall
pre-commit install

# Actualitzar hooks
pre-commit autoupdate
```

## Recursos Addicionals

- [Estàndards de Codi](coding-standards.md)
- [Guia de Testing](testing-guide.md)
- [Documentació Principal](../README.md)
- [Arquitectura](../architecture.md)

## Consells

1. **Actualitza regularment**: `git fetch upstream && git merge upstream/main`
2. **Executa tests sovint**: Abans de commit i push
3. **Llegeix el codi existent**: Per mantenir consistència
4. **Documenta canvis**: Actualitza docs si cal
5. **Pregunta**: Obre issue si tens dubtes

---

Ara estàs preparat per contribuir! 🚀
