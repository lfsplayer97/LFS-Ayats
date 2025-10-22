# LFS-Ayats

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

Prototype telemetry radar for Live for Speed (LFS).

## Resum executiu

- **Objectiu:** Visualitzar en temps real un radar ASCII que replica el
  comportament del prototip original mentre es rep telemetria de LFS.
- **Fonts de telemetria:** Control per InSim (TCP) i dades OutSim (UDP) per
  sincronitzar la posició dels vehicles i l’estat del servidor.
- **Abast del projecte:** Prototype enfocat a proves locals que pot estendre’s
  amb funcionalitats addicionals de les especificacions InSim/OutSim.

## Requisits

- Python 3.10 o superior.
- Dependència opcional: [`simpleaudio`](https://simpleaudio.readthedocs.io/) per reproduir
  els avisos sonors. Si no està disponible, el controlador d’àudio passa a un mode
  silenciós i només registra els esdeveniments.
- Dependències de desenvolupament opcionals per a analitzadors estàtics: consulteu
  `requirements-dev.txt`.

## Configuració essencial

Totes les opcions de temps d’execució es defineixen a
[`config.json`](config.json). Els blocs següents resumeixen els paràmetres
principals:

| Secció / Clau | Funció |
| --- | --- |
| `insim.host`, `insim.port` | Destinació del servidor InSim i interval (`insim.interval_ms`) per als paquets de control. |
| `insim.admin_password` | Contrasenya opcional per autenticar la sessió InSim. |
| `outsim.port`, `outsim.update_hz` | Port UDP on LFS emet OutSim i freqüència esperada d’actualització. |
| `outsim.allowed_sources` | Llista d’adreces IP o xarxes CIDR autoritzades a enviar paquets OutSim. Si s’omet, s’accepten totes les fonts. |
| `outsim.max_packets_per_second` | Límit opcional de paquets OutSim per segon. Els paquets que superen el llindar es descarten i s’enregistra un avís. |
| `telemetry_ws.enabled` | Activa el servidor WebSocket local que retransmet la combinació d’OutSim i InSim. |
| `telemetry_ws.host`, `telemetry_ws.port` | Host i port on s’escolta el servidor WebSocket (per defecte `127.0.0.1:30333`). |
| `telemetry_ws.update_hz` | Cadència d’actualització del flux WebSocket (recomanat entre 10 i 20 Hz per superposicions). |
| `sp_radar_enabled`, `sp_beeps_enabled` | Activen radar i avisos sonors en sessions d’un sol jugador. |
| `mp_radar_enabled`, `mp_beeps_enabled` | Equivalents per a partides multijugador quan `ISS_MULTI` està actiu. |
| `beep.mode` | Estratègia del subsistema d’avisos sonors (`standard`, `calm`, `aggressive`). |
| `beep.volume` | Volum normalitzat del to (0.0–1.0). |
| `beep.base_frequency_hz` | Freqüència base del to; es multiplica en funció de la velocitat instantània. |
| `beep.intervals_ms` | Patró cíclic amb els intervals (en mil·lisegons) entre beeps successius. |

Els canvis al fitxer es detecten i s’apliquen sense reiniciar, permetent ajustar
la configuració segons la teva instal·lació de LFS.

> Nota: el subsistema d’avisos sonors intenta carregar `simpleaudio` en temps
> d’execució. Quan no està disponible, continua funcionant en mode silenciós i
> registra els batecs que s’haurien reproduït.

## Quick start

1. Activa OutSim i InSim a LFS, apuntant OutSim al port definit a `config.json`.
2. Revisa i adapta els valors de `config.json` perquè coincideixin amb la teva
   configuració local.
3. Executa el radar des de l’arrel del projecte amb **`python main.py`**.
4. Mantén la terminal oberta: el client esperarà telemetria OutSim i mostrarà
   el radar ASCII contínuament fins que premis `Ctrl+C`.

Si la clau `telemetry_ws.enabled` està activa, també s’aixeca un servidor a
`ws://<host>:<port>` que publica instantànies JSON (~15 Hz per defecte) amb la
trama OutSim més recent, la informació `IS_MCI` de tots els vehicles i el
vehicle actualment enfocat. Aquest flux permet a superposicions externes
obtenir telemetria sense llegir directament els sockets d’LFS.

## Superposició HTML

El directori [`overlay/`](overlay/) conté una superposició HTML transparent amb
radar de 360°, barra de progrés de volta i indicador de delta que es nodreix del
flux WebSocket anterior. Els passos bàsics per provar-la són:

1. Assegura’t que `telemetry_ws.enabled` estigui actiu i anota el port (per
   defecte `30333`).
2. Des d’una terminal separada, serveix el directori `overlay/` amb qualsevol
   servidor estàtic. Un exemple ràpid amb Python és:

   ```bash
   cd overlay
   python -m http.server 8000
   ```

3. Obre `http://127.0.0.1:8000/index.html` al navegador i introdueix el port
   del WebSocket (o afegeix `?port=30333` a la URL per connectar automàticament).
4. Fes servir els interruptors de la capçalera per amagar o mostrar el radar, la
   barra de volta o el widget de delta segons les necessitats de la transmissió.

La superposició escala i redibuixa el canvas a la cadència del flux. Quan el
socket es tanca o hi ha un tall de telemetria, es mostra un missatge de fallback
perquè el realitzador sàpiga que cal reconnectar.

### Envolupant-la en una finestra sempre visible (opcional)

Per obtenir una finestra flotant sense chrome que mantingui la superposició per
sobre del joc, s’inclou [`overlay/electron-main.js`](overlay/electron-main.js).

1. Inicia un projecte mínim d’Electron si no en tens cap:

   ```bash
   npm init -y
   npm install --save-dev electron
   ```

2. Afegeix un script a `package.json`, per exemple:

   ```json
   "scripts": {
     "overlay": "electron overlay/electron-main.js"
   }
   ```

3. Executa’l amb `npm run overlay`. La finestra és sempre visible, admet
   transparència i pots reposicionar-la damunt de la captura del joc.

El fitxer `preload.js` exposa informació mínima del runtime (`window.electronOverlay`)
per evitar que el contingut de la pàgina requereixi integració Node.js.

## Documentació

- [LFS Programming - LFS Manual](docs/LFS%20Programming%20-%20LFS%20Manual.pdf)
- [Script Guide - LFS Manual](docs/Script%20Guide%20-%20LFS%20Manual.pdf)
- [Commands - LFS Manual](docs/Commands%20-%20LFS%20Manual.pdf)
- [Category_Options - LFS Manual](docs/Category_Options%20-%20LFS%20Manual.pdf)
- [Display - LFS Manual](docs/Display%20-%20LFS%20Manual.pdf)
- [Options_Controls - LFS Manual](docs/Options_Controls%20-%20LFS%20Manual.pdf)
- [Views - LFS Manual](docs/Views%20-%20LFS%20Manual.pdf)
- [Documentació interactiva](docs/site/index.html)

## Integració contínua

- Substituïu `OWNER/REPO` a la insignia anterior pel nom real del projecte a
  GitHub per activar l’enllaç automàtic a la pipeline.
- La pipeline `CI` s’executa en `push` i en `pull_request` i inclou una matriu
  d’entorns amb `ubuntu-latest` i Python `3.10`/`3.11`.
- Cada feina instal·la el paquet en mode editable, reutilitza la memòria cau de
  `pip` (tant des de `actions/setup-python` com amb una memòria cau dedicada del
  directori retornat per `python -m pip cache dir`) i després executa les
  comprovacions següents:
  - `black --check`
  - `isort --check-only`
  - `flake8`
  - `pylint`
  - `mypy`
  - `bandit`
  - `pytest`
- Una feina addicional genera un informe consolidat amb la sortida de totes les
  eines anteriors i l’adjunta com a artefacte (`static-analysis-report.txt`) per
  facilitar la revisió sense haver de consultar els logs de cada feina.

## Notes per a desenvolupadors

### Arquitectura

- `main.py` orquestra el bucle principal i gestiona la recàrrega de configuració.
- Els clients InSim i OutSim encapsulen la comunicació TCP/UDP.

### Fitxers clau

- [`src/insim_client.py`](src/insim_client.py): client mínim per a InSim.
- [`src/outsim_client.py`](src/outsim_client.py): receptor i parser de trames OutSim.
- [`src/radar.py`](src/radar.py): renderitza el radar ASCII.

### Extensió

- Afegiu camps addicionals a `radar.py` segons les necessitats del prototip.
- Utilitzeu els manuals d’InSim/OutSim per incorporar nous paquets o esdeveniments.

### Qualitat de codi

Instal·leu les dependències de desenvolupament amb:

```bash
python -m pip install -r requirements-dev.txt
```

Les eines de qualitat estan configurades perquè apuntin al paquet principal
(`src`) i comparteixen llindars comuns:

- **Flake8**: longitud de línia màxima de 100 caràcters.
- **Pylint**: puntuació mínima (`fail-under`) de 9.0 amb algunes regles
  desactivades (`missing-docstring`, `too-few-public-methods`, `fixme`).
- **Mypy**: comprovacions estrictes amb prohibició de funcions sense anotacions
  i opcions relaxades a `tests`.
- **Bandit**: severitat mínima `LOW` i confiança `HIGH`, permetent l’ús d’`assert`
  (regla `B101`) justificat al prototip.

Per executar totes les comprovacions d’una vegada, utilitzeu el `Makefile`:

```bash
make lint
```

També podeu invocar les eines individualment: `make lint-flake8`,
`make lint-pylint`, `make lint-mypy` o `make lint-bandit`.

### Tests automatitzats

Els tests utilitzen `pytest` i pressuposen que el paquet s'ha instal·lat en mode
editable perquè els imports `src.*` funcionin sense hacks de camí. Des de
l'arrel del projecte:

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt  # inclou pytest i les eines de qualitat
pytest
```

El fitxer [`tests/conftest.py`](tests/conftest.py) conté fixtures compartides,
com ara `insim_client_factory`, per crear instàncies d'`InSimClient` de manera
consistent entre proves.

### Flux amb pre-commit

Instal·leu [pre-commit](https://pre-commit.com) i registreu els hooks definits a
`.pre-commit-config.yaml`:

```bash
python -m pip install pre-commit
pre-commit install
```

Per executar totes les comprovacions manualment abans de fer `commit` utilitzeu:

```bash
pre-commit run --all-files
```

## Convencions d'estil

- Les eines de formatatge (`black` i `isort`) comparteixen una longitud de línia de 100
  caràcters i configuració compatible (`profile = black`).
- La base de codi utilitza anotacions de tipus i es verifica amb `mypy`.
- Les regles de `flake8`, `pylint` i `bandit` definides al projecte són part del procés de
  revisió i s'espera que passin abans d'enviar canvis.

## Crèdits

- Desenvolupament del prototip: equip LFS-Ayats.
- Documentació original de LFS: Scavier / Live for Speed.
