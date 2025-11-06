# LFS Ayats

**[🏴󠁥󠁳󠁣󠁴󠁿 Català](docs/ca/README.md)** | **[🇺🇸 English](docs/en/README.md)**

## Quick Start / Inici Ràpid

Choose your language / Escull el teu idioma:

- **Català**: [Documentació completa en català](docs/ca/README.md)
- **English**: [Full documentation in English](docs/en/README.md)

## Version Management / Gestió de Versions

This project follows [Semantic Versioning](https://semver.org/). The single source of truth for the version is `pyproject.toml`.

Aquest projecte segueix [Versionat Semàntic](https://semver.org/). La font única de veritat per a la versió és `pyproject.toml`.

To synchronize versions across all configuration files / Per sincronitzar versions en tots els fitxers de configuració:

```bash
make version-sync
```

To check if versions are synchronized / Per comprovar si les versions estan sincronitzades:

```bash
make version-check
```

### Configuration / Configuració

Before running the application, copy the example configuration:

```bash
cp config.example.json config.json
```

Abans d'executar l'aplicació, copia la configuració d'exemple:

```bash
cp config.example.json config.json
```

> **Security Note / Nota de seguretat:** `config.json` is not tracked in git to protect 
> local settings. Always use `config.example.json` as a reference.
> 
> `config.json` no es guarda al repositori per protegir la configuració local. 
> Utilitza sempre `config.example.json` com a referència.

## Demo

Open `demo.html` in your browser to test the i18n system.
Obre `demo.html` al navegador per provar el sistema d'internacionalització.

## Examples / Exemples

- **Radar Variants**: Experimental radar implementations → [`examples/radar/`](examples/radar/)
- **Variants del Radar**: Implementacions experimentals del radar → [`examples/radar/`](examples/radar/)

---

**LFS Ayats** - Telemetry system for Live for Speed racing simulator  
**LFS Ayats** - Sistema de telemetria per al simulador de curses Live for Speed
