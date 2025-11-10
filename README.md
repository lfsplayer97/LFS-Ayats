# LFS-Ayats: Live for Speed InSim Telemetry System

Un sistema modular i complet per a la recollida, processament i visualització de dades de telemetria del simulador Live for Speed mitjançant el protocol InSim.

## 📋 Descripció

Aquest repositori proporciona una implementació professional del protocol InSim de Live for Speed, permetent:

- **Connexió i comunicació** amb el servidor LFS mitjançant sockets TCP/UDP
- **Recollida de telemetria** en temps real (velocitat, RPM, temperatura, posició, etc.)
- **Processament de paquets** InSim amb validació i gestió d'errors
- **Visualització de dades** en temps real amb dashboards interactius
- **Exportació de dades** a formats CSV, JSON i bases de dades
- **REST API** per accés programàtic i integració amb altres eines
- **WebSocket** per streaming de telemetria en temps real
- **Proves automàtiques** per validar inputs/outputs telemètrics

## 🏗️ Estructura del Repositori

```
LFS-Ayats/
├── src/                          # Codi font principal
│   ├── api/                      # API REST (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py              # Aplicació FastAPI
│   │   ├── models.py            # Models Pydantic
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── middleware.py        # CORS i logging
│   │   ├── exceptions.py        # Excepcions personalitzades
│   │   └── routers/             # Endpoints API
│   ├── connection/               # Mòdul de connexió InSim
│   │   ├── __init__.py
│   │   ├── insim_client.py      # Client InSim TCP/UDP
│   │   └── packet_handler.py    # Gestió de paquets InSim
│   ├── telemetry/               # Mòdul de telemetria
│   │   ├── __init__.py
│   │   ├── collector.py         # Recollida de dades telemètriques
│   │   └── processor.py         # Processament i validació de dades
│   ├── database/                # Mòdul de base de dades
│   │   ├── __init__.py
│   │   ├── models.py            # Models SQLAlchemy
│   │   └── repository.py        # Capa d'accés a dades
│   ├── visualization/           # Mòdul de visualització
│   │   ├── __init__.py
│   │   ├── dashboard.py         # Dashboard web en temps real (Dash)
│   │   ├── plots.py             # Gràfics d'anàlisi
│   │   ├── map_view.py          # Visualització de mapes de circuit
│   │   ├── comparator.py        # Comparació de voltes
│   │   └── components/          # Components reutilitzables
│   ├── export/                  # Mòdul d'exportació
│   │   ├── __init__.py
│   │   ├── csv_exporter.py     # Exportació a CSV
│   │   ├── json_exporter.py    # Exportació a JSON
│   │   └── db_exporter.py      # Exportació a base de dades
│   ├── config/                  # Gestió de configuració
│   │   ├── __init__.py
│   │   └── settings.py         # Configuració de l'aplicació
│   └── utils/                   # Utilitats comunes
│       ├── __init__.py
│       └── logger.py           # Sistema de logging
├── tests/                       # Proves automàtiques
│   ├── unit/                   # Tests unitaris
│   ├── integration/            # Tests d'integració
│   └── fixtures/               # Dades de prova
├── examples/                    # Exemples d'ús
│   ├── basic_connection.py     # Connexió bàsica
│   ├── telemetry_monitor.py   # Monitor de telemetria
│   ├── data_logger.py         # Logger de dades
│   └── api_client_example.py  # Client de l'API REST
├── docs/                       # Documentació
│   ├── insim_protocol.md      # Documentació del protocol InSim
│   ├── packet_reference.md    # Referència de paquets
│   ├── api_reference.md       # Referència de l'API
│   ├── api_documentation.md   # Documentació de l'API REST
│   └── development.md         # Guia de desenvolupament
├── scripts/                    # Scripts d'utilitat
│   └── delete-branches.sh     # Gestió de branques
├── .gitignore                 # Fitxers ignorats per Git
├── requirements.txt           # Dependències Python
├── setup.py                   # Instal·lació del paquet
├── pytest.ini                 # Configuració de pytest
└── README.md                  # Aquest fitxer
```

## 🚀 Instal·lació

### Requisits Previs

- Python 3.8 o superior
- Live for Speed (demostració o versió completa)
- pip (gestor de paquets Python)

### Instal·lació de Dependències

```bash
# Clonar el repositori
git clone https://github.com/lfsplayer97/LFS-Ayats.git
cd LFS-Ayats

# Crear entorn virtual (recomanat)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instal·lar dependències
pip install -r requirements.txt

# Instal·lar el paquet en mode desenvolupament
pip install -e .
```

## 📖 Ús Bàsic

### Connexió a LFS

```python
from src.connection import InSimClient
from src.telemetry import TelemetryCollector

# Crear client InSim
client = InSimClient(
    host='127.0.0.1',
    port=29999,
    admin_password='',
    app_name='LFS-Ayats'
)

# Connectar
client.connect()

# Crear col·lector de telemetria
collector = TelemetryCollector(client)

# Iniciar recollida de dades
collector.start()
```

### Exportació de Dades

```python
from src.export import CSVExporter, JSONExporter

# Exportar a CSV
csv_exporter = CSVExporter('telemetry_data.csv')
csv_exporter.export(telemetry_data)

# Exportar a JSON
json_exporter = JSONExporter('telemetry_data.json')
json_exporter.export(telemetry_data)
```

### REST API

El sistema inclou una API REST completa construïda amb FastAPI per accés programàtic:

```bash
# Iniciar el servidor API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Documentació Automàtica:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

**Exemple d'ús del client:**

```python
import requests

# Llistar sessions
response = requests.get("http://localhost:8000/api/v1/sessions")
sessions = response.json()

# Obtenir telemetria d'una volta
response = requests.get("http://localhost:8000/api/v1/1/telemetry")
telemetry = response.json()

# WebSocket per telemetria en temps real
import websockets
import asyncio

async def receive_telemetry():
    uri = "ws://localhost:8000/api/v1/telemetry/live"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(f"Telemetry: {data}")

asyncio.run(receive_telemetry())
```

**Endpoints disponibles:**
- `/api/v1/health` - Health check
- `/api/v1/sessions` - Gestió de sessions
- `/api/v1/{lap_id}` - Informació de voltes
- `/api/v1/telemetry/live` - WebSocket streaming
- `/api/v1/stats/best-laps` - Millors voltes
- `/api/v1/export/csv/{lap_id}` - Exportació CSV
- i molts més...

Vegeu [docs/api_documentation.md](docs/api_documentation.md) per documentació completa de l'API.

### Visualització en Temps Real

```python
from src.visualization import TelemetryDashboard

# Crear dashboard web en temps real
dashboard = TelemetryDashboard(
    host='127.0.0.1',
    port=29999,
    update_interval=100  # actualització cada 100ms
)

# Executar el servidor del dashboard
dashboard.run(debug=True, port=8050)
# Obre el navegador a http://localhost:8050
```

### Anàlisi i Comparació de Voltes

```python
from src.visualization import (
    LapComparator,
    create_speed_vs_distance_plot,
    create_track_map,
    create_heatmap_plot
)

# Comparar voltes
comparator = LapComparator()
comparator.add_lap("Lap 1", lap1_telemetry)
comparator.add_lap("Lap 2", lap2_telemetry)

# Crear gràfics de comparació
fig = comparator.create_comparison_plot()
fig.write_html("lap_comparison.html")

# Crear mapa de circuit amb velocitats
track_fig = create_track_map(telemetry, show_speed_colors=True)
track_fig.write_html("track_map.html")

# Crear mapa de calor
heatmap_fig = create_heatmap_plot(telemetry)
heatmap_fig.write_html("speed_heatmap.html")
```

Per més informació sobre visualització, consulta [docs/visualization.md](docs/visualization.md)

## 🧪 Proves Automàtiques

El projecte inclou proves automàtiques completes per garantir la qualitat del codi:

```bash
# Executar totes les proves
pytest

# Executar proves amb cobertura
pytest --cov=src --cov-report=html

# Executar proves específiques
pytest tests/unit/connection/
pytest tests/integration/
```

## 📚 Protocol InSim

InSim (Internet Simulator) és el protocol de comunicació de Live for Speed que permet a aplicacions externes interactuar amb el simulador.

### Paquets InSim Principals

| Paquet | Descripció | Ús |
|--------|------------|-----|
| `IS_ISI` | InSim Init | Inicialitzar connexió InSim |
| `IS_VER` | Version | Versió del protocol InSim |
| `IS_TINY` | Tiny | Paquets de control petit |
| `IS_SMALL` | Small | Paquets de dades petit |
| `IS_MCI` | Multi Car Info | Informació de múltiples cotxes |
| `IS_NLP` | Node and Lap | Informació de nodes i voltes |
| `IS_MSO` | Message Out | Missatges del servidor |
| `IS_III` | InSim Info | Informació del servidor |
| `IS_STA` | State | Estat del servidor |
| `IS_NCN` | New Connection | Nova connexió de jugador |
| `IS_CNL` | Connection Leave | Jugador desconnecta |
| `IS_CPR` | Connection Player Rename | Canvi de nom de jugador |
| `IS_NPL` | New Player | Nou jugador a la pista |
| `IS_PLP` | Player Leave | Jugador deixa la pista |
| `IS_PIT` | Pit Stop | Parada als boxes |
| `IS_PSF` | Pit Stop Finish | Fi de parada als boxes |
| `IS_LAP` | Lap Time | Temps de volta |
| `IS_SPX` | Split Time | Temps de sector |
| `IS_PEN` | Penalty | Penalització |
| `IS_TOC` | Take Over Car | Canvi de control de cotxe |
| `IS_FLG` | Flag | Bandera |
| `IS_RES` | Result | Resultats |
| `IS_REO` | Reorder | Reordenació de cotxes |
| `IS_BTN` | Button | Botons d'interfície |
| `IS_BFN` | Button Function | Funcions de botons |
| `IS_AXI` | Autocross Info | Informació d'Autocross |
| `IS_RIP` | Replay Info | Informació de replay |

### Telemetria Disponible

La telemetria que es pot recollir inclou:

- **Dades del vehicle**: velocitat, RPM, marxa, angle de direcció
- **Dades del motor**: temperatura, consum de combustible, força
- **Dades de posició**: coordenades X/Y/Z, orientació, alçada
- **Dades de volta**: temps de volta, millor temps, sectors
- **Dades de la pista**: tipus de superfície, distància recorreguda
- **Dades del jugador**: nom, equip, cotxe, configuració
- **Esdeveniments**: sortida, arribada, parades als boxes, penalitzacions

## 📖 Referències

### Documentació Oficial

- **LFS Manual**: https://en.lfsmanual.net/wiki/Main_Page
- **InSim Protocol**: https://en.lfsmanual.net/wiki/InSim.txt
- **Outgauge Protocol**: https://en.lfsmanual.net/wiki/OutGauge
- **Outsim Protocol**: https://en.lfsmanual.net/wiki/OutSim

### Recursos Addicionals

- **LFS Forum**: https://www.lfs.net/forum
- **LFS World**: https://www.lfs.net/
- **Packet Reference**: Consultar `docs/packet_reference.md`
- **API Reference**: Consultar `docs/api_reference.md`

## 🤝 Contribució

Les contribucions són benvingudes! Si vols contribuir:

1. Fork el repositori
2. Crea una branca per la teva feature (`git checkout -b feature/nova-funcionalitat`)
3. Commit els teus canvis (`git commit -m 'Afegir nova funcionalitat'`)
4. Push a la branca (`git push origin feature/nova-funcionalitat`)
5. Obre un Pull Request

### Bones Pràctiques

- Seguir les convencions de codi PEP 8
- Escriure proves per a totes les noves funcionalitats
- Documentar el codi amb docstrings
- Actualitzar la documentació si cal
- Mantenir la modularitat i separació de responsabilitats

## 📄 Llicència

Aquest projecte està sota llicència MIT. Veure el fitxer `LICENSE` per més detalls.

## ✨ Autors

- **lfsplayer97** - Desenvolupador principal

## 🙏 Agraïments

- Scawen Roberts i l'equip de Live for Speed pel simulator i el protocol InSim
- La comunitat LFS per la documentació i suport
- Contributors i beta testers

## 📞 Contacte

Per qüestions, suggeriments o problemes, si us plau obre un issue al repositori de GitHub.

---

**Nota**: Aquest projecte està en desenvolupament actiu. Consulta la documentació i els exemples per més informació sobre l'ús i les funcionalitats disponibles.
