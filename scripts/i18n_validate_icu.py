#!/usr/bin/env python3
"""
Validació senzilla de patrons ICU:
- Detecta usos de plural {count, plural, ...}
- Exigeix com a mínim les formes 'one' i 'other'
- Comprova que EN i CA coincideixin en l'ús de plural i placeholders

*No* és un parser complet d'ICU, però detecta la majoria d'errors comuns abans de runtime.

Ús:
  python scripts/i18n_validate_icu.py i18n/en-US.json i18n/ca.json
"""
import sys, json, re
from typing import Dict, Any, Tuple, Set

PLURAL_RE = re.compile(r"\{\s*([a-zA-Z_]\w*)\s*,\s*plural\s*,(.*?)\}", re.DOTALL)
FORM_RE = re.compile(r"(?:^|[^\w])(zero|one|two|few|many|other)\s*\{", re.IGNORECASE)

def flatten(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out

def find_plural_forms(s: str) -> Set[str]:
    m = PLURAL_RE.search(s or "")
    if not m:
        return set()
    body = m.group(2)
    forms = set(f.lower() for f in FORM_RE.findall(body))
    return forms

def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/i18n_validate_icu.py <en.json> <ca.json>")
        sys.exit(2)
    en = json.load(open(sys.argv[1], encoding="utf-8"))
    ca = json.load(open(sys.argv[2], encoding="utf-8"))
    f_en = flatten(en); f_ca = flatten(ca)

    exit_code = 0
    for k in sorted(set(f_en.keys()) & set(f_ca.keys())):
        v_en = f_en[k]; v_ca = f_ca[k]
        if not isinstance(v_en, str) or not isinstance(v_ca, str):
            continue
        p_en = find_plural_forms(v_en)
        p_ca = find_plural_forms(v_ca)
        if p_en or p_ca:
            # Si una llengua usa plural, l'altra també
            if bool(p_en) != bool(p_ca):
                print(f"❌ Ús inconsist. de plural ICU a '{k}': EN={p_en or '—'} CA={p_ca or '—'}")
                exit_code = 1
                continue
            # Exigir 'one' i 'other' com a mínim
            for lang, forms in (("EN", p_en), ("CA", p_ca)):
                if "other" not in forms or "one" not in forms:
                    print(f"❌ Falten formes ICU 'one' i/o 'other' a '{k}' ({lang}): {sorted(forms)}")
                    exit_code = 1

    if exit_code == 0:
        print("✅ ICU bàsic validat (plural i consistència)")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
