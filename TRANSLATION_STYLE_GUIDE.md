# TRANSLATION_STYLE_GUIDE

> **Idiomes**: `en-US` (predeterminat) i `ca`.  
> **Públic**: usuaris finals, admins i desenvolupadors.  
> **Objectiu**: consistència terminològica i de to; evitar regressions d’UI i d’ajuda de CLI.

## 1. Variant, to i persona
- **Anglès**: `en-US`. **Català**: `ca`.
- **To**: professional, clar, orientat a l’acció i precís tècnicament.
- **Persona**: segona persona (“you”) i **veu activa**.

## 2. Formats i convencions
- **Dates**: ISO 8601 `YYYY-MM-DD` (ex.: `2025-11-02`). Quan mostris data i hora, usa TZ clara o UTC (ex.: `2025-11-02T18:05Z`).
- **Nombres**:
  - EN: decimals amb **punt** (`3.14`), separador de milers **coma** (`12,345`).
  - CA: decimals amb **coma** (`3,14`), milers amb **espai fi** (`12 345`).
- **Unitats**: preferim **km/h** i **°C**. Quan la font sigui *mph* o *°F*, mostra conversió:
  - EN: `Converted {value} mph → {kmh} km/h.`
  - CA: `S’ha convertit {value} mph → {kmh} km/h.`
- **Moneda**: codi ISO davant si cal desambiguar (p. ex. `USD 12.50`).
- **Codi i flags**: no es tradueixen. No tradueixis **noms de paràmetres**, **claus JSON**, **rutes**, **APIs** ni **sortida de terminal**.

## 3. Referències d’UI i text
- Elements d’UI (botons/menús): en **cometes** i literal, ex.: *Click “Save”* / *Fes clic a “Save”* si el literal és en anglès.
- **No concatenar** cadenes. Usa **plantilles** amb placeholders **anomenats**: `{fileName}`, `{count}`.

## 4. Pluralització i ICU
- Usa **ICU MessageFormat** per a plurals i variants.
  - EN: `"{count, plural, one {# lap} other {# laps}}"`
  - CA: `"{count, plural, one {# volta} other {# voltes}}"`
- **Obligatori**: les dues llengües han de tenir **els mateixos placeholders** i, si hi ha plural, com a mínim les formes **`one`** i **`other`**.

## 5. Títols, puntuació i estil
- **EN**: Title Case als títols de docs; **CA**: estil de frase (només la primera paraula i noms propis en majúscula).
- Puntuació simple i clara; evita exclamacions innecessàries.
- Text inclusiu: evita argot, jerga excloent o expressions ambigua.

## 6. Exemple de patrons
- **Salutació amb nom**  
  - EN: `Hi, {name}!`  
  - CA: `Hola, {name}!`
- **Error genèric**  
  - EN: `Something went wrong. Try again.`  
  - CA: `Alguna cosa no ha anat bé. Torna-ho a provar.`
- **Temps per volta**  
  - EN: `Split time: {time}`  
  - CA: `Split: {time}` (mantén el terme tècnic si és l’ús establert)
- **Conversió d’unitats**  
  - EN: `Converted {value} mph → {kmh} km/h.`  
  - CA: `S’ha convertit {value} mph → {kmh} km/h.`

## 7. No traduïbles
- Identificadors, claus, rutes, noms de protocols (InSim/OutSim/OutGauge), **noms de producte**, flags i ordres CLI, fragments de codi i sortides.

## 8. Captures i accessibilitat
- Proporciona **capturas** en EN i CA quan hi hagi text incrustat.
- Afegeix **alt text** descriptiu, i comprova **contrast** i **overflow** amb textos llargs (pseudo-localització).

## 9. Comprovacions abans de fer merge
- Clau present a **ambdós** catàlegs (`en-US.json`, `ca.json`).
- **Placeholders** idèntics i **ICU validat**.
- Docs sense enllaços trencats; MD lint OK; alex/vale OK.
- UI sense truncaments amb pseudo-localització.
