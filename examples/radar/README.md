# LFS Radar Variants / Variants del Radar LFS

**[🏴󠁥󠁳󠁣󠁴󠁿 Català](#català)** | **[🇺🇸 English](#english)**

---

## English

### Overview

This directory contains **experimental and development versions** of the LFS radar system. These files were created during the development process to test different approaches, debug issues, and explore various implementation strategies.

**⚠️ Important**: For production use, refer to the main radar module at `src/radar.py` and the entry point `main.py`.

### Files Description

#### `lfs_radar_ultimate.py` ⭐ (258 lines)
**Purpose**: The most feature-rich experimental version with enhanced terminal UI

**Features**:
- Colored terminal output with ANSI codes
- Smooth screen updates without flickering
- Maximum speed tracking
- Total distance calculation
- Advanced visualization with background colors
- Status messages and error handling

**Use when**: You want to see the full potential of radar features in a standalone script

---

#### `lfs_radar_working.py` ✅ (222 lines)
**Purpose**: Stable working version without syntax errors

**Features**:
- Clean, functional implementation
- Reliable packet processing
- Terminal color support
- Basic radar visualization
- Good error handling

**Use when**: You need a reliable standalone radar that just works

---

#### `lfs_radar_back_to_basics.py` 🔄 (209 lines)
**Purpose**: Back-to-basics approach focusing on core functionality

**Features**:
- Simplified implementation
- Focus on essential radar features
- Less complexity, easier to understand
- Good starting point for modifications

**Use when**: You want to understand the basic radar implementation or start a custom version

---

#### `lfs_radar_robust.py` 🛡️ (171 lines)
**Purpose**: Version with enhanced error protection and validation

**Features**:
- Extensive input validation
- Safe type conversion helpers (`is_valid_float`, `safe_int_convert`)
- Protection against invalid data
- Graceful degradation on errors

**Use when**: You're debugging packet format issues or need maximum stability

---

#### `lfs_radar_clean.py` 🧹 (146 lines)
**Purpose**: Minimal, clean implementation for improved visualization

**Features**:
- Minimalist approach
- Clear code structure
- Basic but effective radar display
- Reduced complexity

**Use when**: You prefer simple, readable code or want to learn the basics

---

#### `lfs_radar_debug.py` 🕵️ (141 lines)
**Purpose**: Debug tool to analyze OutSim packet structure

**Features**:
- Detailed packet analysis
- Tests multiple data offsets
- Helps identify correct packet format
- Useful for protocol debugging

**Use when**: You're troubleshooting OutSim protocol issues or verifying packet structure

---

### Which One Should I Use?

- **For production**: Use `src/radar.py` with `main.py` (the official module)
- **To experiment**: Start with `lfs_radar_working.py` or `lfs_radar_ultimate.py`
- **To learn**: Use `lfs_radar_clean.py` or `lfs_radar_back_to_basics.py`
- **To debug**: Use `lfs_radar_debug.py`
- **For stability**: Use `lfs_radar_robust.py`

### How to Run

All variants require:
1. Live for Speed running
2. OutSim enabled in LFS (cockpit view)
3. Correct port configuration in `config.json`

```bash
# From repository root
python examples/radar/lfs_radar_working.py
```

### Evolution Path

```
lfs_radar_debug.py (protocol research)
    ↓
lfs_radar_clean.py (basic implementation)
    ↓
lfs_radar_robust.py (error handling)
    ↓
lfs_radar_back_to_basics.py (simplified)
    ↓
lfs_radar_working.py (stable version)
    ↓
lfs_radar_ultimate.py (feature-complete)
    ↓
src/radar.py (production module)
```

---

## Català

### Visió General

Aquest directori conté **versions experimentals i de desenvolupament** del sistema de radar LFS. Aquests fitxers es van crear durant el procés de desenvolupament per provar diferents enfocaments, depurar problemes i explorar diverses estratègies d'implementació.

**⚠️ Important**: Per a ús en producció, consulta el mòdul principal del radar a `src/radar.py` i el punt d'entrada `main.py`.

### Descripció dels Fitxers

#### `lfs_radar_ultimate.py` ⭐ (258 línies)
**Finalitat**: La versió experimental més completa amb interfície de terminal millorada

**Característiques**:
- Sortida de terminal amb colors ANSI
- Actualitzacions de pantalla suaus sense parpelleig
- Seguiment de velocitat màxima
- Càlcul de distància total
- Visualització avançada amb colors de fons
- Missatges d'estat i gestió d'errors

**Usa-la quan**: Vulguis veure el potencial complet de les funcions del radar en un script autònom

---

#### `lfs_radar_working.py` ✅ (222 línies)
**Finalitat**: Versió estable funcionant sense errors de sintaxi

**Característiques**:
- Implementació neta i funcional
- Processament fiable de paquets
- Suport per colors de terminal
- Visualització bàsica del radar
- Bona gestió d'errors

**Usa-la quan**: Necessitis un radar autònom fiable que simplement funcioni

---

#### `lfs_radar_back_to_basics.py` 🔄 (209 línies)
**Finalitat**: Enfocament de tornada als bàsics centrat en la funcionalitat principal

**Característiques**:
- Implementació simplificada
- Focus en funcions essencials del radar
- Menys complexitat, més fàcil d'entendre
- Bon punt de partida per modificacions

**Usa-la quan**: Vulguis entendre la implementació bàsica del radar o començar una versió personalitzada

---

#### `lfs_radar_robust.py` 🛡️ (171 línies)
**Finalitat**: Versió amb protecció millorada contra errors i validació

**Característiques**:
- Validació extensiva d'entrada
- Funcions auxiliars de conversió segura (`is_valid_float`, `safe_int_convert`)
- Protecció contra dades invàlides
- Degradació elegant davant d'errors

**Usa-la quan**: Estiguis depurant problemes de format de paquets o necessitis màxima estabilitat

---

#### `lfs_radar_clean.py` 🧹 (146 línies)
**Finalitat**: Implementació mínima i neta per a visualització millorada

**Característiques**:
- Enfocament minimalista
- Estructura de codi clara
- Visualització del radar bàsica però efectiva
- Complexitat reduïda

**Usa-la quan**: Prefereixis codi simple i llegible o vulguis aprendre els bàsics

---

#### `lfs_radar_debug.py` 🕵️ (141 línies)
**Finalitat**: Eina de depuració per analitzar l'estructura de paquets OutSim

**Característiques**:
- Anàlisi detallada de paquets
- Prova múltiples desplaçaments de dades
- Ajuda a identificar el format correcte del paquet
- Útil per depurar el protocol

**Usa-la quan**: Estiguis solucionant problemes del protocol OutSim o verificant l'estructura dels paquets

---

### Quin Hauria d'Utilitzar?

- **Per producció**: Usa `src/radar.py` amb `main.py` (el mòdul oficial)
- **Per experimentar**: Comença amb `lfs_radar_working.py` o `lfs_radar_ultimate.py`
- **Per aprendre**: Usa `lfs_radar_clean.py` o `lfs_radar_back_to_basics.py`
- **Per depurar**: Usa `lfs_radar_debug.py`
- **Per estabilitat**: Usa `lfs_radar_robust.py`

### Com Executar

Totes les variants requereixen:
1. Live for Speed en execució
2. OutSim habilitat a LFS (vista cockpit)
3. Configuració correcta del port a `config.json`

```bash
# Des de l'arrel del repositori
python examples/radar/lfs_radar_working.py
```

### Camí d'Evolució

```
lfs_radar_debug.py (recerca del protocol)
    ↓
lfs_radar_clean.py (implementació bàsica)
    ↓
lfs_radar_robust.py (gestió d'errors)
    ↓
lfs_radar_back_to_basics.py (simplificat)
    ↓
lfs_radar_working.py (versió estable)
    ↓
lfs_radar_ultimate.py (complet de funcions)
    ↓
src/radar.py (mòdul de producció)
```
