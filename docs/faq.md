# Preguntes Freqüents (FAQ)

Respostes a les preguntes més comunes sobre LFS-Ayats.

## 📑 Índex

- [Instal·lació i Configuració](#installació-i-configuració)
- [Connexió](#connexió)
- [Telemetria](#telemetria)
- [Visualització](#visualització)
- [Base de Dades](#base-de-dades)
- [API REST](#api-rest)
- [Rendiment](#rendiment)
- [Troubleshooting](#troubleshooting)

---

## Instal·lació i Configuració

### P: Quines versions de Python són compatibles?

**R:** LFS-Ayats requereix Python 3.8 o superior. S'ha provat amb Python 3.8, 3.9, 3.10, 3.11 i 3.12.

```bash
python --version  # Ha de mostrar 3.8+
```

### P: Com configurar el port InSim a LFS?

**R:** A Live for Speed:
1. Ves a **Options > Misc**
2. A la secció **InSim**, marca la casella
3. Introdueix el port: `29999` (o el que vulguis)
4. (Opcional) Introdueix contrasenya d'admin
5. Fes clic a **OK**

### P: On es guarden les dades per defecte?

**R:** Les dades es guarden a la carpeta `./data/` per defecte. Pots canviar-ho a `config.yaml`:

```yaml
export:
  output_directory: "./my_data"
```

### P: Puc utilitzar el sistema sense Live for Speed?

**R:** No directament. Necessites LFS en execució per rebre telemetria. Tanmateix, pots:
- Analitzar dades prèviament exportades
- Utilitzar el mode de simulació (si implementat)
- Reproduir sessions gravades

### P: Com actualitzar a l'última versió?

**R:**
```bash
cd LFS-Ayats
git pull origin main
pip install -r requirements.txt --upgrade
pip install -e .
```

---

## Connexió

### P: Error "Connection refused"

**R:** Verifica que:

1. **LFS està en execució**
   ```bash
   # Comprova si LFS està obert
   ps aux | grep LFS  # Linux/Mac
   tasklist | findstr LFS  # Windows
   ```

2. **InSim està activat** a Options > Misc

3. **Port correcte** (per defecte 29999)
   ```python
   client = InSimClient(host="127.0.0.1", port=29999)
   ```

4. **Firewall no bloqueja** la connexió
   ```bash
   # Linux: Permet port 29999
   sudo ufw allow 29999/tcp
   
   # Windows: Afegeix excepció al Windows Firewall
   ```

### P: Es desconnecta constantment

**R:** Comprova:

1. **Estabilitat de xarxa**: Ping a localhost
   ```bash
   ping 127.0.0.1
   ```

2. **Sistema no està en suspensió**: Desactiva sleep mode

3. **Heartbeat activat** a config:
   ```yaml
   insim:
     heartbeat_interval: 30  # segons
   ```

4. **Logs d'error**: Revisa `logs/` per errors específics

### P: Com connectar a un servidor remot?

**R:** Especifica l'adreça IP del servidor:

```python
client = InSimClient(
    host="192.168.1.100",  # IP del servidor LFS
    port=29999,
    admin_password="mypassword"  # Requerit per servidors remots
)
```

**Nota**: El servidor LFS ha de tenir InSim configurat per acceptar connexions externes.

### P: Quin és el límit de connexions simultànies?

**R:** LFS suporta fins a 8 connexions InSim simultànies per defecte. Cada instància de LFS-Ayats compta com una connexió.

---

## Telemetria

### P: No rebo dades telemètriques

**R:** Assegura't que:

1. **Estàs en una sessió activa** (no al menú)
   - Has de ser a la pista conduint

2. **Interval configurat correctament** (> 0):
   ```yaml
   insim:
     interval: 100  # milliseconds
   ```

3. **Vehicle en moviment**: InSim no envia dades si el cotxe està aturat

4. **Subscripció a paquets correcta**:
   ```python
   collector = TelemetryCollector(client)
   collector.start()  # No oblidis iniciar!
   ```

### P: Les dades semblen incorrectes

**R:** Verifica:

1. **Versions d'InSim compatibles**: LFS 0.6V o superior

2. **Unitats de mesura** a config:
   ```yaml
   telemetry:
     speed_unit: "kmh"  # o "mph", "ms"
     temperature_unit: "celsius"
   ```

3. **Calibració**: Compara amb indicadors in-game

4. **Logs de validació**:
   ```python
   processor = TelemetryProcessor()
   valid = processor.validate_speed(speed)
   ```

### P: Quina és la freqüència màxima de telemetria?

**R:** 
- **Mínim interval**: 10ms (100 Hz)
- **Recomanat**: 50-100ms (10-20 Hz)
- **Per defecte**: 100ms (10 Hz)

Intervals massa curts poden sobrecarregar el sistema.

### P: Com filtrar telemetria per jugador específic?

**R:**
```python
# Filtrar per player_id
telemetry = collector.get_latest_telemetry(player_id=1)

# Filtrar per nom
history = collector.get_telemetry_history()
player_data = [t for t in history if t['player_name'] == 'MyName']
```

### P: Es poden recollir dades de múltiples cotxes simultàniament?

**R:** Sí! El paquet `IS_MCI` (Multi Car Info) proporciona dades de fins a 8 cotxes simultàniament. LFS-Ayats processa automàticament tots els vehicles a la pista.

---

## Visualització

### P: El dashboard no es carrega

**R:** Comprova:

1. **Port disponible** (per defecte 8050):
   ```bash
   # Linux/Mac
   lsof -i :8050
   
   # Windows
   netstat -ano | findstr :8050
   ```

2. **Dependències instal·lades**:
   ```bash
   pip install dash plotly
   ```

3. **Obre navegador correcte**:
   - URL: `http://localhost:8050`
   - No `https://`

4. **Logs del servidor**:
   ```python
   dashboard.run(debug=True)  # Mostra errors detallats
   ```

### P: Els gràfics no s'actualitzen

**R:**

1. **Interval configurat**:
   ```python
   dcc.Interval(interval=100)  # milliseconds
   ```

2. **Callbacks registrats correctament**:
   ```python
   @app.callback(...)
   def update_graph(n):
       # Codi d'actualització
   ```

3. **Dades disponibles**: Verifica que `get_latest_telemetry()` retorna dades

### P: Com personalitzar colors del dashboard?

**R:**
```python
app.layout = html.Div([
    # ...
], style={
    'backgroundColor': '#1e1e1e',  # Fons fosc
    'color': '#ffffff'              # Text blanc
})

# O utilitza temes predefinits
import dash_bootstrap_components as dbc
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
```

### P: Puc exportar gràfics com a imatges?

**R:** Sí!

```python
fig = create_speed_vs_distance_plot(telemetry)

# PNG
fig.write_image("graph.png", width=1200, height=600)

# SVG (escalable)
fig.write_image("graph.svg")

# HTML interactiu
fig.write_html("graph.html")
```

**Nota**: Necessita `kaleido` instal·lat: `pip install kaleido`

---

## Base de Dades

### P: Quin motor de base de dades utilitzar?

**R:**

**SQLite** (Recomanat per començar):
- ✅ Sense configuració
- ✅ Fitxer únic
- ✅ Perfecte per ús local
- ❌ Límit en concurrència

**PostgreSQL** (Recomanat per producció):
- ✅ Millor rendiment
- ✅ Suporta múltiples clients
- ✅ Funcions avançades
- ❌ Requereix servidor

### P: Com migrar de SQLite a PostgreSQL?

**R:**

1. **Exportar dades de SQLite**:
   ```bash
   sqlite3 telemetry.db .dump > dump.sql
   ```

2. **Configurar PostgreSQL**:
   ```python
   engine = create_engine('postgresql://user:pass@localhost/lfs_telemetry')
   ```

3. **Executar migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Importar dades**:
   ```bash
   psql -U user -d lfs_telemetry < dump.sql
   ```

### P: Com fer backup de la base de dades?

**R:**

**SQLite**:
```bash
# Còpia simple
cp data/telemetry.db backups/telemetry_$(date +%Y%m%d).db

# Amb compressió
tar -czf telemetry_backup.tar.gz data/telemetry.db
```

**PostgreSQL**:
```bash
# Backup complet
pg_dump lfs_telemetry > backup_$(date +%Y%m%d).sql

# Backup comprimit
pg_dump lfs_telemetry | gzip > backup.sql.gz

# Restore
psql lfs_telemetry < backup.sql
```

### P: La base de dades creix molt ràpid

**R:** Optimitzacions:

1. **Limitar històric**:
   ```python
   # Mantenir només últimes 1000 voltes
   repo.delete_old_sessions(keep_last=1000)
   ```

2. **Agregar dades antigues**:
   ```python
   # Mostrejar dades antigues (guardar 1 de cada 10 punts)
   repo.downsample_old_telemetry(older_than_days=30, factor=10)
   ```

3. **Vacuum (SQLite)**:
   ```bash
   sqlite3 telemetry.db "VACUUM;"
   ```

4. **Particionament (PostgreSQL)**:
   ```sql
   -- Partir taula per dates
   CREATE TABLE telemetry_2024_01 PARTITION OF telemetry
   FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
   ```

---

## API REST

### P: Com accedir a la documentació de l'API?

**R:** Amb el servidor en execució:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### P: Error 401 Unauthorized

**R:** L'API requereix autenticació per alguns endpoints:

```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get(
    "http://localhost:8000/api/v1/sessions",
    headers=headers
)
```

Obté token amb:
```python
response = requests.post(
    "http://localhost:8000/api/v1/auth/token",
    data={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]
```

### P: Com utilitzar WebSocket per telemetria en temps real?

**R:**

**Python**:
```python
import asyncio
import websockets

async def stream_telemetry():
    uri = "ws://localhost:8000/api/v1/telemetry/live"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(f"Received: {data}")

asyncio.run(stream_telemetry())
```

**JavaScript**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/telemetry/live');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Telemetry:', data);
};
```

### P: Límit de peticions per minut?

**R:** Per defecte:
- **GET requests**: 60/minut
- **POST requests**: 30/minut
- **WebSocket**: Sense límit

Configurable a `config.yaml`:
```yaml
api:
  rate_limit:
    get: 100
    post: 50
```

---

## Rendiment

### P: El sistema consumeix molta memòria

**R:** Optimitzacions:

1. **Limitar buffer**:
   ```python
   collector = TelemetryCollector(client, max_history=5000)
   ```

2. **Netejar històric periòdicament**:
   ```python
   collector.clear_history()
   ```

3. **Utilitzar base de dades** en lloc de memòria

4. **Reducir freqüència**:
   ```yaml
   insim:
     interval: 200  # menys freqüent = menys memòria
   ```

### P: Latència alta en el dashboard

**R:**

1. **Augmentar interval d'actualització**:
   ```python
   dcc.Interval(interval=500)  # 500ms en lloc de 100ms
   ```

2. **Reduir dades mostrades**:
   ```python
   history = collector.get_telemetry_history(limit=100)
   ```

3. **Simplificar gràfics**: Menys punts, menys traces

4. **Utilitzar cache**:
   ```python
   @lru_cache(maxsize=128)
   def get_processed_data():
       # ...
   ```

### P: Com monitoritzar rendiment del sistema?

**R:**

```python
import psutil
import time

def monitor_performance():
    process = psutil.Process()
    
    print(f"CPU: {process.cpu_percent()}%")
    print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    print(f"Threads: {process.num_threads()}")

# Executar periòdicament
while True:
    monitor_performance()
    time.sleep(60)
```

---

## Troubleshooting

### P: "ModuleNotFoundError: No module named 'src'"

**R:** Instal·la el paquet en mode desenvolupament:

```bash
pip install -e .
```

O afegeix al PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows
```

### P: Tests fallen amb errors de connexió

**R:** Els tests unitaris utilitzen mocking. Assegura't que:

```bash
# Executar només tests que no requereixen connexió
pytest -m "not network"

# Ignorar tests d'integració
pytest tests/unit/
```

### P: Dashboard mostra pàgina en blanc

**R:**

1. **Comprova consola del navegador** (F12) per errors JavaScript

2. **Verifica que Dash s'ha inicialitzat**:
   ```python
   app = dash.Dash(__name__)
   # Afegir layout i callbacks abans de run_server()
   ```

3. **Prova amb debug activat**:
   ```python
   app.run_server(debug=True)
   ```

### P: Error "SSL: CERTIFICATE_VERIFY_FAILED"

**R:** Problema amb certificats HTTPS. Solucions:

```python
# Opció 1: Actualitzar certificats
pip install --upgrade certifi

# Opció 2: Desactivar verificació (NO recomanat per producció)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

### P: Com habilitar logging detallat?

**R:**

```python
from src.utils import setup_logger

# Nivells: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger = setup_logger("my_module", level="DEBUG")
```

O a `config.yaml`:
```yaml
logging:
  level: DEBUG
  file: "logs/lfs_ayats.log"
```

### P: Encara tinc problemes...

**R:** Obre un issue a GitHub amb:

1. **Descripció detallada** del problema
2. **Codi per reproduir** l'error
3. **Logs complets** (amb `level="DEBUG"`)
4. **Entorn**:
   - Versió de Python
   - Sistema operatiu
   - Versions de dependències (`pip list`)
5. **Passos realitzats** per intentar solucionar-ho

---

## Recursos Addicionals

- 📖 [Documentació Completa](README.md)
- 🚀 [Guia d'Inici Ràpid](quick-start.md)
- 🎓 [Tutorials](tutorials/)
- 🏗️ [Arquitectura](architecture.md)
- 🐛 [Reportar Issues](https://github.com/lfsplayer97/LFS-Ayats/issues)

---

Si tens més preguntes, no dubtis en obrir un [issue](https://github.com/lfsplayer97/LFS-Ayats/issues) o iniciar una [discussió](https://github.com/lfsplayer97/LFS-Ayats/discussions)! 🤝
