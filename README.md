# LFS-Ayats

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
- No calen dependències externes; s’utilitza exclusivament la llibreria estàndard.
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
| `sp_radar_enabled`, `sp_beeps_enabled` | Activen radar i avisos sonors en sessions d’un sol jugador. |
| `mp_radar_enabled`, `mp_beeps_enabled` | Equivalents per a partides multijugador quan `ISS_MULTI` està actiu. |
| `beep_mode` | Estratègia del subsistema d’avisos (actualment marcador). |

Els canvis al fitxer es detecten i s’apliquen sense reiniciar, permetent ajustar
la configuració segons la teva instal·lació de LFS.

## Quick start

1. Activa OutSim i InSim a LFS, apuntant OutSim al port definit a `config.json`.
2. Revisa i adapta els valors de `config.json` perquè coincideixin amb la teva
   configuració local.
3. Executa el radar des de l’arrel del projecte amb **`python main.py`**.
4. Mantén la terminal oberta: el client esperarà telemetria OutSim i mostrarà
   el radar ASCII contínuament fins que premis `Ctrl+C`.

## Documentació

- [LFS Programming - LFS Manual](docs/LFS%20Programming%20-%20LFS%20Manual.pdf)
- [Script Guide - LFS Manual](docs/Script%20Guide%20-%20LFS%20Manual.pdf)
- [Commands - LFS Manual](docs/Commands%20-%20LFS%20Manual.pdf)
- [Category_Options - LFS Manual](docs/Category_Options%20-%20LFS%20Manual.pdf)
- [Display - LFS Manual](docs/Display%20-%20LFS%20Manual.pdf)
- [Options_Controls - LFS Manual](docs/Options_Controls%20-%20LFS%20Manual.pdf)
- [Views - LFS Manual](docs/Views%20-%20LFS%20Manual.pdf)
- [Documentació interactiva](docs/site/index.html)

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
python -m pip install -r requirements-dev.txt  # opcional, per a eines addicionals
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
