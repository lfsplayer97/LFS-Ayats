# i18n

Catàlegs d’idioma i scripts per a control de qualitat.

## Scripts
- `scripts/i18n_check_keys.py i18n/en-US.json i18n/ca.json` — compara claus i placeholders.
- `scripts/i18n_validate_icu.py i18n/en-US.json i18n/ca.json` — valida pluralització ICU bàsica.
- `scripts/pseudo_localize.py i18n/en-US.json i18n/en-US__pseudo.json` — genera catàleg pseudo.

## Flux recomanat
1. Afegeix/edita claus a `en-US.json`.
2. Executa `i18n_check_keys.py` i `i18n_validate_icu.py`.
3. Tradueix `ca.json`.
4. Torna a executar els scripts.
5. Prova pseudo-local i comprova truncaments d’UI.
