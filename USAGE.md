# File Deletion Agent - Usage Guide

## Overview / Visió General

**English**: This is an automated agent for deleting all files from a GitHub repository in a safe and controlled manner.

**Català**: Aquest és un agent automatitzat per esborrar tots els arxius d'un repositori de GitHub de manera segura i controlada.

---

## Quick Start / Inici Ràpid

### 1. Preview what will be deleted / Previsualitzar què s'esborraria

```bash
python3 delete_files_agent.py
```

### 2. Delete all files (with confirmation) / Esborrar tots els arxius (amb confirmació)

```bash
python3 delete_files_agent.py --execute
```

### 3. Delete without confirmation / Esborrar sense confirmació

```bash
python3 delete_files_agent.py --execute --force
```

---

## Features / Característiques

### English

- **Dry Run Mode**: By default, shows what would be deleted without actually deleting
- **User Confirmation**: Requires explicit "yes" before deleting files
- **Git Protection**: Never touches the `.git` directory
- **Detailed Logging**: Shows every file and directory being processed
- **Error Handling**: Continues operation even if individual files can't be deleted
- **Empty Directory Cleanup**: Automatically removes empty directories after file deletion

### Català

- **Mode de Prova**: Per defecte, mostra què s'esborraria sense esborrar realment
- **Confirmació d'Usuari**: Requereix "yes" explícit abans d'esborrar arxius
- **Protecció Git**: Mai toca el directori `.git`
- **Registre Detallat**: Mostra cada arxiu i directori que es processa
- **Gestió d'Errors**: Continua l'operació fins i tot si arxius individuals no es poden esborrar
- **Neteja de Directoris Buits**: Esborra automàticament directoris buits després d'esborrar arxius

---

## Command Line Options / Opcions de Línia de Comandes

| Option / Opció | Description / Descripció (English) | Descripció (Català) |
|---------------|-----------------------------------|---------------------|
| `repo_path` | Path to repository (default: current directory) | Ruta al repositori (per defecte: directori actual) |
| `--execute` | Actually delete files (default is dry run) | Esborra arxius realment (per defecte és mode de prova) |
| `--force` | Skip all confirmation prompts | Salta totes les confirmacions |
| `--help` | Show help message | Mostra el missatge d'ajuda |

---

## Examples / Exemples

### Example 1: Safe Preview / Exemple 1: Previsualització Segura

**English**: First, always run without `--execute` to see what will happen:

**Català**: Primer, executa sempre sense `--execute` per veure què passarà:

```bash
cd /path/to/your/repo
python3 delete_files_agent.py
```

**Output / Sortida**:
```
============================================================
File Deletion Agent
Repository: /path/to/your/repo
Mode: DRY RUN (no files will be deleted)
============================================================

Found 10 file(s) to delete.

[DRY RUN] Would delete: file1.txt
[DRY RUN] Would delete: file2.txt
...
```

### Example 2: Actual Deletion with Confirmation / Exemple 2: Esborrament Real amb Confirmació

**English**: After verifying the preview, run with `--execute`:

**Català**: Després de verificar la previsualització, executa amb `--execute`:

```bash
python3 delete_files_agent.py --execute
```

**Interactive Prompt / Pregunta Interactiva**:
```
WARNING: This will delete ALL files from the repository!
This operation cannot be undone!

Are you absolutely sure you want to proceed? (yes/no): yes
```

### Example 3: Automated Deletion / Exemple 3: Esborrament Automatitzat

**English**: For automation scripts, use `--force` (use with extreme caution):

**Català**: Per a scripts automatitzats, usa `--force` (usa amb molta precaució):

```bash
python3 delete_files_agent.py --execute --force
```

### Example 4: Specific Repository / Exemple 4: Repositori Específic

**English**: Delete files from a specific repository path:

**Català**: Esborra arxius d'una ruta de repositori específica:

```bash
python3 delete_files_agent.py /path/to/specific/repo --execute
```

---

## Workflow / Flux de Treball

### Recommended Workflow / Flux de Treball Recomanat

**English**:
1. **Preview** the deletion with dry run
2. **Execute** the deletion with `--execute`
3. **Review** changes with `git status`
4. **Commit** the changes: `git add -A && git commit -m "Delete all files"`
5. **Push** to GitHub: `git push`

**Català**:
1. **Previsualitza** l'esborrament amb mode de prova
2. **Executa** l'esborrament amb `--execute`
3. **Revisa** els canvis amb `git status`
4. **Commit** els canvis: `git add -A && git commit -m "Esborrar tots els arxius"`
5. **Push** a GitHub: `git push`

### Full Example / Exemple Complet

```bash
# Step 1: Preview / Pas 1: Previsualització
python3 delete_files_agent.py
# Review the output / Revisa la sortida

# Step 2: Execute / Pas 2: Executa
python3 delete_files_agent.py --execute
# Type 'yes' when prompted / Escriu 'yes' quan es demani

# Step 3: Git workflow / Pas 3: Flux de treball Git
git status                                        # Review changes / Revisa canvis
git add -A                                        # Stage all deletions / Prepara tots els esborrats
git commit -m "Delete all files from repository" # Commit / Compromet
git push                                          # Push to GitHub / Puja a GitHub
```

---

## Safety Features / Característiques de Seguretat

### What is Protected / Què està Protegit

**English**:
- The `.git` directory (repository history)
- Git's internal files and structure
- Nothing else - ALL other files will be deleted

**Català**:
- El directori `.git` (historial del repositori)
- Arxius interns i estructura de Git
- Res més - TOTS els altres arxius s'esborraran

### Safety Checks / Comprovacions de Seguretat

**English**:
1. ✅ Dry run by default - never deletes without explicit `--execute`
2. ✅ Confirmation prompt - requires typing "yes"
3. ✅ Git repository check - warns if not in a git repo
4. ✅ Detailed logging - shows every file being deleted
5. ✅ Error recovery - continues even if some files fail

**Català**:
1. ✅ Mode de prova per defecte - mai esborra sense `--execute` explícit
2. ✅ Pregunta de confirmació - requereix escriure "yes"
3. ✅ Comprovació de repositori Git - avisa si no és un repositori git
4. ✅ Registre detallat - mostra cada arxiu que s'esborra
5. ✅ Recuperació d'errors - continua fins i tot si alguns arxius fallen

---

## Troubleshooting / Solució de Problemes

### Issue: Permission Denied / Problema: Permís Denegat

**English**: If you get permission errors, make sure you have write permissions to the files:

**Català**: Si obtens errors de permisos, assegura't que tens permisos d'escriptura als arxius:

```bash
chmod -R u+w .
python3 delete_files_agent.py --execute
```

### Issue: Can't Delete Some Files / Problema: No Es Poden Esborrar Alguns Arxius

**English**: The script will continue and report which files failed. Review the output for errors.

**Català**: El script continuarà i informarà quins arxius han fallat. Revisa la sortida per errors.

### Issue: Accidentally Deleted Files / Problema: Arxius Esborrats Accidentalment

**English**: If you haven't committed yet, you can restore files from git:

**Català**: Si encara no has fet commit, pots restaurar arxius des de git:

```bash
git checkout HEAD -- .
```

---

## Requirements / Requisits

- Python 3.6 or higher / Python 3.6 o superior
- Git repository (recommended) / Repositori Git (recomanat)
- Write permissions / Permisos d'escriptura

---

## Warning / Advertència

⚠️ **English**: This tool deletes ALL files from the repository (except `.git`). This operation is permanent once committed and pushed. Always preview first with dry run mode.

⚠️ **Català**: Aquesta eina esborra TOTS els arxius del repositori (excepte `.git`). Aquesta operació és permanent un cop es fa commit i push. Sempre previsualitza primer amb mode de prova.

---

## Support / Suport

For issues or questions / Per problemes o preguntes:
- Review this documentation first / Revisa primer aquesta documentació
- Check the output messages carefully / Comprova els missatges de sortida amb cura
- Test with dry run mode before executing / Prova amb mode de prova abans d'executar
