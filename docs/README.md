# Documentació de LFS-Ayats

Benvingut a la documentació completa del sistema de telemetria LFS-Ayats per Live for Speed.

## 🚀 Començar Ràpidament

### Per Usuaris Nous

- **[Guia d'Inici Ràpid](quick-start.md)** - Posa el sistema en funcionament en 5-10 minuts
- **[Tutorial 1: Primera Sessió](tutorials/01-first-session.md)** - Recull la teva primera sessió de telemetria

### Per Desenvolupadors

- **[Configuració d'Entorn](contributing/development-setup.md)** - Configura l'entorn de desenvolupament
- **[Guia de Contribució](../CONTRIBUTING.md)** - Com contribuir al projecte

## 📚 Tutorials Interactius

Aprèn pas a pas amb els nostres tutorials detallats:

| Tutorial | Descripció | Temps | Nivell |
|----------|------------|-------|--------|
| **[01 - Primera Sessió](tutorials/01-first-session.md)** | Recull i exporta telemetria bàsica | 30 min | Principiant |
| **[02 - Anàlisi de Voltes](tutorials/02-lap-analysis.md)** | Compara voltes i troba millores | 45 min | Intermedi |
| **[03 - Dashboard Temps Real](tutorials/03-real-time-dashboard.md)** | Crea dashboard web interactiu | 30 min | Intermedi |
| **[04 - Anàlisi Avançada](tutorials/04-advanced-analysis.md)** | Machine learning i prediccions | 60 min | Avançat |
| **[05 - Base de Dades](tutorials/05-database-integration.md)** | Emmagatzema històrics | 45 min | Avançat |

## 🏗️ Documentació Tècnica

### Arquitectura i Disseny

- **[Arquitectura del Sistema](architecture.md)** - Components, patrons de disseny i flux de dades
- **[Protocol InSim](insim_protocol.md)** - Detalls del protocol de comunicació amb LFS
- **[Referència de Paquets](packet_reference.md)** - Estructura de paquets InSim

### APIs i Referències

- **[API REST](api_documentation.md)** - Documentació completa de l'API REST
- **[Inici Ràpid API](api_quickstart.md)** - Guia ràpida per utilitzar l'API
- **[Referència API](api_reference.md)** - Referència completa de classes i mètodes

### Mòduls Específics

- **[Analysis Module](analysis_module.md)** - Advanced analysis features
- **[Mòdul de Visualització](visualization.md)** - Gràfics i dashboards
- **[Gestió d'Errors](error_handling_reconnection.md)** - Reconnexió i gestió d'errors

## 💡 Casos d'Ús Pràctics

Aprèn com utilitzar LFS-Ayats en escenaris reals:

### [🏆 Carreres de Lliga](use-cases/league-racing.md)
Configuració completa per gestionar telemetria en lligues amb múltiples pilots:
- Recollida multi-pilot
- Anàlisi comparativa
- Reports automàtics
- Dashboard públic

### [📈 Entrenament de Pilots](use-cases/driver-coaching.md)
Sistema de coaching basat en dades per millorar rendiment:
- Anàlisi de consistència
- Comparació amb referència
- Identificació d'àrees de millora
- Seguiment de progressió

## 👨‍💻 Guies per Desenvolupadors

### Contribuir al Projecte

- **[Configuració d'Entorn](contributing/development-setup.md)** - Configura l'entorn de desenvolupament
  - Fork i clonar
  - Entorn virtual
  - Instal·lació de dependències
  - Pre-commit hooks
  - Verificació

- **[Estàndards de Codi](contributing/coding-standards.md)** - Convencions i bones pràctiques
  - Nomenclatura (PEP 8)
  - Type hints
  - Docstrings (Google style)
  - Comentaris
  - Patrons recomanats

- **[Guia de Testing](contributing/testing-guide.md)** - Escriure i executar tests
  - Tests unitaris
  - Tests d'integració
  - Mocking
  - Cobertura de codi
  - CI/CD

## ❓ Preguntes Freqüents

**[FAQ Completa](faq.md)** - Respostes a les preguntes més comunes

### Categories

- **Instal·lació i Configuració** - Setup inicial, ports, configuració
- **Connexió** - Problemes de connexió, desconnexions, servidors remots
- **Telemetria** - Recollida de dades, freqüència, filtres
- **Visualització** - Dashboard, gràfics, personalització
- **Base de Dades** - PostgreSQL, SQLite, backups, optimització
- **API REST** - Autenticació, WebSocket, límits
- **Rendiment** - Memòria, latència, optimitzacions
- **Troubleshooting** - Errors comuns i solucions

## 📖 Referències Ràpides

### Comandes Útils

```bash
# Instal·lació
pip install -r requirements.txt
pip install -e .

# Tests
pytest                           # Tots els tests
pytest --cov=src                # Amb cobertura
pytest -m unit                  # Només unitaris

# Qualitat de codi
black src/ tests/               # Formatació
flake8 src/ tests/              # Linting
mypy src/                       # Type checking

# Executar sistema
python examples/basic_connection.py
python examples/telemetry_monitor.py
python examples/dashboard_example.py

# API
uvicorn src.api.main:app --reload
```

### Configuració Ràpida

```yaml
# config.yaml
insim:
  host: "127.0.0.1"
  port: 29999
  interval: 100

telemetry:
  max_history: 10000
  
export:
  output_directory: "./data"
  
api:
  port: 8000
  
dashboard:
  port: 8050
  update_interval: 100
```

### Python Ràpid

```python
from src.connection import InSimClient
from src.telemetry import TelemetryCollector

# Connectar
client = InSimClient(host="127.0.0.1", port=29999)
client.connect()
client.initialize()

# Recollir telemetria
collector = TelemetryCollector(client)
collector.start()

# Obtenir dades
data = collector.get_latest_telemetry()
history = collector.get_telemetry_history(limit=100)

# Aturar
collector.stop()
client.disconnect()
```

## 🔗 Recursos Externs

### Live for Speed

- **[LFS Manual](https://en.lfsmanual.net/)** - Manual oficial
- **[InSim Protocol](https://en.lfsmanual.net/wiki/InSim.txt)** - Especificació completa
- **[LFS Forum](https://www.lfs.net/forum)** - Comunitat oficial
- **[LFS World](https://www.lfs.net/)** - Estadístiques i rànquings

### Python i Eines

- **[Python Documentation](https://docs.python.org/3/)** - Documentació oficial de Python
- **[Plotly](https://plotly.com/python/)** - Gràfics interactius
- **[Dash](https://dash.plotly.com/)** - Framework per dashboards
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework per APIs
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM per Python

### Desenvolupament

- **[PEP 8](https://pep8.org/)** - Guia d'estil Python
- **[Black](https://black.readthedocs.io/)** - Formatador automàtic
- **[Pytest](https://docs.pytest.org/)** - Framework de testing
- **[Git](https://git-scm.com/doc)** - Control de versions

## 📝 Índex de Documentació

### Nivell Principiant

1. [Guia d'Inici Ràpid](quick-start.md)
2. [Tutorial 1: Primera Sessió](tutorials/01-first-session.md)
3. [FAQ: Instal·lació](faq.md#installació-i-configuració)
4. [FAQ: Connexió](faq.md#connexió)

### Nivell Intermedi

1. [Tutorial 2: Anàlisi de Voltes](tutorials/02-lap-analysis.md)
2. [Tutorial 3: Dashboard](tutorials/03-real-time-dashboard.md)
3. [Visualització](visualization.md)
4. [API Quickstart](api_quickstart.md)

### Nivell Avançat

1. [Tutorial 4: Anàlisi Avançada](tutorials/04-advanced-analysis.md)
2. [Tutorial 5: Base de Dades](tutorials/05-database-integration.md)
3. [Arquitectura](architecture.md)
4. [Protocol InSim](insim_protocol.md)

### Per Desenvolupadors

1. [Development Setup](contributing/development-setup.md)
2. [Coding Standards](contributing/coding-standards.md)
3. [Testing Guide](contributing/testing-guide.md)
4. [CONTRIBUTING.md](../CONTRIBUTING.md)

## 🆘 Suport

### Reportar Problemes

Si trobes un bug o tens un problema:

1. Consulta la [FAQ](faq.md)
2. Busca a [Issues existents](https://github.com/lfsplayer97/LFS-Ayats/issues)
3. Obre un [nou issue](https://github.com/lfsplayer97/LFS-Ayats/issues/new)

### Preguntes i Discussions

Per preguntes generals o discussions:

- [GitHub Discussions](https://github.com/lfsplayer97/LFS-Ayats/discussions)
- Fòrum de LFS (secció Addons)

### Contribuir

Vols millorar la documentació o el codi?

1. Llegeix [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Consulta [Development Setup](contributing/development-setup.md)
3. Obre un Pull Request

## 📅 Actualitzacions

La documentació s'actualitza regularment. Última actualització: **2024**

Per veure canvis recents:
- [Changelog](../CHANGELOG.md) (si existeix)
- [Commits recents](https://github.com/lfsplayer97/LFS-Ayats/commits/main)

---

## 🎯 Pròxims Passos Recomanats

**Si ets nou**:
1. ✅ Llegeix la [Guia d'Inici Ràpid](quick-start.md)
2. ✅ Completa el [Tutorial 1](tutorials/01-first-session.md)
3. ✅ Explora la [FAQ](faq.md)

**Si vols aprofundir**:
1. ✅ Completa tots els [Tutorials](tutorials/)
2. ✅ Revisa un [Cas d'Ús](use-cases/)
3. ✅ Explora l'[Arquitectura](architecture.md)

**Si vols contribuir**:
1. ✅ Configura [Entorn de Desenvolupament](contributing/development-setup.md)
2. ✅ Llegeix [Estàndards de Codi](contributing/coding-standards.md)
3. ✅ Escriu tests ([Testing Guide](contributing/testing-guide.md))

---

**Gaudeix utilitzant LFS-Ayats!** 🏎️ 💨

Per qualsevol dubte, no dubtis en contactar a través de [GitHub](https://github.com/lfsplayer97/LFS-Ayats).
