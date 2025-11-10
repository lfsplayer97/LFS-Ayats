# Guia d'Inici Ràpid

Aquesta guia t'ajudarà a posar en funcionament el sistema LFS-Ayats en 5-10 minuts.

## Prerequisits

- **Python 3.8 o superior** - [Descarregar Python](https://www.python.org/downloads/)
- **Live for Speed** instal·lat (versió demo o completa) - [Descarregar LFS](https://www.lfs.net/)
- **Git** (opcional, per clonar el repositori) - [Descarregar Git](https://git-scm.com/)

## Pas 1: Instal·lació

### Opció A: Clonar des de GitHub (recomanat)

```bash
git clone https://github.com/lfsplayer97/LFS-Ayats.git
cd LFS-Ayats
```

### Opció B: Descarregar ZIP

1. Descarrega el [repositori com ZIP](https://github.com/lfsplayer97/LFS-Ayats/archive/refs/heads/main.zip)
2. Extreu el contingut a una carpeta
3. Obre un terminal a la carpeta extreta

### Instal·lar Dependències

```bash
# Crear entorn virtual (recomanat)
python -m venv venv

# Activar entorn virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instal·lar dependències
pip install -r requirements.txt

# Instal·lar el paquet en mode desenvolupament
pip install -e .
```

**Temps estimat**: 2-3 minuts (depenent de la velocitat d'Internet)

## Pas 2: Configuració

Copia el fitxer de configuració d'exemple:

```bash
cp config.example.yaml config.yaml
```

**Configuració per defecte** (ja preparada per funcionar):
- Host: `127.0.0.1` (localhost)
- Port: `29999` (port InSim estàndard)
- No requereix contrasenya d'administrador per defecte

Si vols personalitzar la configuració, edita `config.yaml`:

```yaml
insim:
  host: "127.0.0.1"
  port: 29999
  admin_password: ""  # Deixar buit si no cal
  app_name: "LFS-Ayats"
  interval: 100  # ms entre actualitzacions
```

## Pas 3: Executar Live for Speed

1. **Obre Live for Speed**
2. **Activa InSim**:
   - Ves a **Options > Misc**
   - A la secció **InSim**, marca la casella
   - Introdueix el port: `29999`
   - Fes clic a **OK**

   ![InSim Configuration](images/insim-config.png)

3. **Inicia una sessió de conducció**:
   - Escull un circuit (per exemple, Blackwood GP - BL1)
   - Escull un cotxe (per exemple, XF GTI)
   - Fes clic a **Drive**

**Important**: InSim només funciona durant sessions de conducció actives, no al menú principal.

## Pas 4: Connectar i Recollir Dades

Executa l'exemple de connexió bàsica:

```bash
python examples/basic_connection.py
```

**Sortida esperada**:
```
INFO - === Exemple Bàsic de Connexió InSim ===
INFO - Connectant a 127.0.0.1:29999...
INFO - Connexió establerta!
INFO - InSim inicialitzat!
INFO - Rebent paquets durant 10 segons...
INFO - Paquet rebut: IS_VER
INFO - Paquet rebut: IS_ISM
```

Condueix pel circuit durant aquest temps per veure paquets de telemetria!

## Pas 5: Visualitzar Dades en Temps Real

### Opció A: Monitor de Telemetria (consola)

```bash
python examples/telemetry_monitor.py
```

Veuràs dades actualitzades en temps real a la consola:
```
=== Telemetria en Temps Real ===
Jugador: YourName
Velocitat: 145.2 km/h
RPM: 6500
Marxa: 4
Posició: X=1234.5 Y=567.8 Z=12.3
```

### Opció B: Dashboard Web Interactiu

```bash
python examples/dashboard_example.py
```

Obre el navegador a: **http://localhost:8050**

Funcions del dashboard:
- 📊 Gràfics de velocitat en temps real
- 🔄 Actualització cada 100ms
- 🎨 Interfície interactiva amb Plotly
- 📈 Historial de dades

![Dashboard Example](images/dashboard.png)

## Pas 6: Exportar Dades

Recull dades i exporta-les a CSV:

```bash
python examples/data_logger.py
```

Les dades es guardaran a:
- `data/telemetry_YYYYMMDD_HHMMSS.csv`
- `data/telemetry_YYYYMMDD_HHMMSS.json`

**Format CSV**:
```csv
timestamp,player_id,speed,rpm,gear,pos_x,pos_y,pos_z
2024-01-15 10:30:45.123,1,145.2,6500,4,1234.5,567.8,12.3
```

## Verificar que Tot Funciona

✅ **Checklist d'èxit**:
- [ ] Dependències instal·lades sense errors
- [ ] LFS executa i InSim està activat
- [ ] Connexió bàsica establerta correctament
- [ ] Es reben paquets de telemetria
- [ ] Dashboard web mostra dades
- [ ] Dades exportades correctament

## Pròxims Passos

### Tutorials Avançats

1. **[Primera Sessió de Telemetria](tutorials/01-first-session.md)** - Aprèn a recollir i analitzar dades d'una sessió completa
2. **[Anàlisi de Voltes](tutorials/02-lap-analysis.md)** - Compara voltes i troba àrees de millora
3. **[Dashboard en Temps Real](tutorials/03-real-time-dashboard.md)** - Personalitza el dashboard
4. **[Anàlisi Avançada](tutorials/04-advanced-analysis.md)** - Detecció d'anomalies i prediccions
5. **[Integració amb Base de Dades](tutorials/05-database-integration.md)** - Emmagatzema sessions històriques

### Aprendre Més

- **[Documentació d'Arquitectura](architecture.md)** - Com funciona el sistema internament
- **[Protocol InSim](insim_protocol.md)** - Detalls del protocol de comunicació
- **[API REST](api_documentation.md)** - Integració amb altres aplicacions
- **[FAQ](faq.md)** - Preguntes freqüents i solució de problemes

### Contribuir

Vols millorar el projecte? Consulta:
- **[Guia de Contribució](../CONTRIBUTING.md)**
- **[Configuració d'Entorn de Desenvolupament](contributing/development-setup.md)**
- **[Estàndards de Codi](contributing/coding-standards.md)**

## Solució de Problemes Ràpids

### Error: "Connection refused"

**Causa**: LFS no està executant o InSim no està activat

**Solució**:
1. Verifica que LFS està en execució
2. Comprova que InSim està activat a Options > Misc
3. Confirma que el port és 29999
4. Assegura't que estàs en una sessió de conducció activa

### Error: "Module not found"

**Causa**: Dependències no instal·lades o entorn virtual no activat

**Solució**:
```bash
# Activa l'entorn virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstal·la dependències
pip install -r requirements.txt
pip install -e .
```

### No es reben dades de telemetria

**Causa**: El cotxe està aturat o la configuració de l'interval és incorrecta

**Solució**:
1. Condueix activament pel circuit
2. Verifica que `interval` a `config.yaml` és > 0
3. Comprova que el sistema està subscrit als paquets correctes

### Més problemes?

Consulta la **[guia completa de troubleshooting](faq.md#troubleshooting)** o obre un [issue a GitHub](https://github.com/lfsplayer97/LFS-Ayats/issues).

## Recursos Addicionals

### Documentació Oficial de LFS

- [Manual de Live for Speed](https://en.lfsmanual.net/)
- [Protocol InSim](https://en.lfsmanual.net/wiki/InSim.txt)
- [Fòrum de LFS](https://www.lfs.net/forum)

### Comunitat

- [GitHub Issues](https://github.com/lfsplayer97/LFS-Ayats/issues) - Reporta problemes o suggereix millores
- [GitHub Discussions](https://github.com/lfsplayer97/LFS-Ayats/discussions) - Preguntes i discussions

---

**Temps total estimat**: 5-10 minuts

Ara estàs preparat per començar a utilitzar LFS-Ayats! 🏎️ 💨

Per qualsevol dubte, consulta la [documentació completa](README.md) o contacta amb la comunitat.
