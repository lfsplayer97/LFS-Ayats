## Resum
<!-- Explica què canvia aquest PR i per què. -->

## Impacte i18n
- [ ] Afecta **docs** (`/docs/en`, `/docs/ca`)
- [ ] Afecta **UI/CLI** (`/i18n/*.json`)
- [ ] Només codi sense impacte a usuari

## Checklist i18n (obligatori)
- [ ] **Res de strings hardcoded** en codi nou (externalitzats a `/i18n`)
- [ ] Claus noves a `en-US.json` i `ca.json` (mateixa **estructura**)
- [ ] **Placeholders** idèntics entre EN/CA
- [ ] **ICU** validat (`scripts/i18n_validate_icu.py`)
- [ ] Pseudo-localització sense trencaments (`scripts/pseudo_localize.py`)
- [ ] MD lints OK (`markdownlint`) i enllaços OK
- [ ] `alex` sense alertes crítiques; `vale` sense errors
- [ ] Captures actualitzades i **alt text** afegit si aplica
- [ ] S’ha comprovat **overflow** d’UI amb textos llargs

## Notes per a revisió
<!-- Context addicional, decisions terminològiques, captures. -->
