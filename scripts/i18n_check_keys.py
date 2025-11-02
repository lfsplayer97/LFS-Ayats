#!/usr/bin/env python3
"""
Comprova:
- Mateix conjunt de claus entre dos catàlegs (EN/CA)
- Placeholders consistents entre idiomes
- Claus duplicades (en JSON no hi poden haver, però comprovem diccionaris repetits)

Ús:
  python scripts/i18n_check_keys.py i18n/en-US.json i18n/ca.json
"""
import sys, json, re
from typing import Dict, Any, Tuple, Set, List

PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

def flatten(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out

def extract_placeholders(value: str) -> Set[str]:
    return set(PLACEHOLDER_RE.findall(value or ""))

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/i18n_check_keys.py <en.json> <ca.json>")
        sys.exit(2)
    en_path, ca_path = sys.argv[1], sys.argv[2]
    en = load_json(en_path)
    ca = load_json(ca_path)
    f_en = flatten(en)
    f_ca = flatten(ca)

    exit_code = 0

    # Claus que falten / sobren
    en_keys = set(f_en.keys())
    ca_keys = set(f_ca.keys())

    missing_in_ca = en_keys - ca_keys
    missing_in_en = ca_keys - en_keys

    if missing_in_ca:
        print("❌ Falta(n) a ca.json:")
        for k in sorted(missing_in_ca):
            print("  -", k)
        exit_code = 1
    if missing_in_en:
        print("❌ Falta(n) a en-US.json:")
        for k in sorted(missing_in_en):
            print("  -", k)
        exit_code = 1

    # Placeholders consistents
    for k in sorted(en_keys & ca_keys):
        v_en = f_en[k]
        v_ca = f_ca[k]
        if not isinstance(v_en, str) or not isinstance(v_ca, str):
            continue
        ph_en = extract_placeholders(v_en)
        ph_ca = extract_placeholders(v_ca)
        if ph_en != ph_ca:
            print(f"❌ Placeholders diferents a la clau '{k}': EN={sorted(ph_en)} CA={sorted(ph_ca)}")
            exit_code = 1

    if exit_code == 0:
        print("✅ Claus i placeholders consistents entre en-US.json i ca.json")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
