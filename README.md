# File Deletion Agent

Aquesta és una eina automatitzada per esborrar tots els arxius d'un repositori de GitHub.

## Descripció

Aquest agent Python proporciona una manera segura i controlada d'esborrar tots els arxius d'un repositori. Inclou diverses mesures de seguretat:

- **Mode de prova (dry run)** per defecte: mostra què s'esborraria sense esborrar res
- **Confirmació d'usuari**: demana confirmació abans d'esborrar arxius realment
- **Exclusions automàtiques**: no toca mai el directori `.git`
- **Registre detallat**: mostra tots els arxius que s'esborren

## Ús

### Mode de prova (recomanat primer)

```bash
python delete_files_agent.py
```

Això mostrarà tots els arxius que s'esborrerien sense esborrar-los realment.

### Esborrar arxius realment

```bash
python delete_files_agent.py --execute
```

Això demanarà confirmació i després esborrarà tots els arxius del repositori.

### Esborrar sense confirmació (perillós!)

```bash
python delete_files_agent.py --execute --force
```

## Opcions

- `repo_path`: Ruta al repositori (per defecte: directori actual)
- `--execute`: Executar realment l'esborrament (per defecte és mode de prova)
- `--force`: Saltar la confirmació (usar amb precaució!)

## Exemples

### Veure què s'esborraria:
```bash
python delete_files_agent.py /ruta/al/repositori
```

### Esborrar arxius amb confirmació:
```bash
python delete_files_agent.py /ruta/al/repositori --execute
```

### Esborrar tot sense confirmació:
```bash
python delete_files_agent.py . --execute --force
```

## Flux de treball recomanat

1. **Executar en mode de prova** per veure què s'esborraria:
   ```bash
   python delete_files_agent.py
   ```

2. **Executar l'esborrament real** si estàs satisfet:
   ```bash
   python delete_files_agent.py --execute
   ```

3. **Revisar els canvis** amb git:
   ```bash
   git status
   ```

4. **Commit i push** els canvis:
   ```bash
   git add -A
   git commit -m "Esborrar tots els arxius del repositori"
   git push
   ```

## Advertències

⚠️ **ADVERTÈNCIA**: Aquesta eina esborra TOTS els arxius del repositori!

⚠️ **Aquesta operació no es pot desfer** fàcilment. Assegura't que:
- Has fet una còpia de seguretat si necessites els arxius
- Realment vols esborrar tots els arxius
- Estàs en el repositori correcte

## Què NO esborra

L'agent **NO** esborra:
- El directori `.git` (per mantenir l'historial de git)
- Arxius `.gitignore` (opcional, es pot configurar)

## Característiques de seguretat

1. **Mode de prova per defecte**: Mai esborra res sense `--execute`
2. **Confirmació explícita**: Cal escriure "yes" per confirmar
3. **Protecció del directori .git**: Mai toca l'historial de git
4. **Registre complet**: Mostra cada arxiu que s'esborra
5. **Gestió d'errors**: Continua si un arxiu no es pot esborrar

## Requisits

- Python 3.6 o superior
- Sistema operatiu: Linux, macOS, o Windows
- Permisos d'escriptura al repositori

## Llicència

Aquest script es proporciona "tal qual" sense cap garantia. Usar sota la pròpia responsabilitat.
