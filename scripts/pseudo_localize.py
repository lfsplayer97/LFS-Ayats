#!/usr/bin/env python3
"""
Genera un catàleg pseudo-localitzat per provar truncaments d'UI.

Converteix text ASCII a una versió amb diacrítics i envolta amb marcadors, allargant lleugerament la longitud.

Ús:
  python scripts/pseudo_localize.py i18n/en-US.json i18n/en-US__pseudo.json
"""
import sys, json, re
from typing import Dict, Any

MAP = str.maketrans({
    "A":"Å","a":"á","B":"ß","b":"ƀ","C":"Ć","c":"č","D":"Đ","d":"ď",
    "E":"Ė","e":"ē","F":"Ḟ","f":"ƒ","G":"Ğ","g":"ğ","H":"Ħ","h":"ħ",
    "I":"Í","i":"ï","J":"Ĵ","j":"ĵ","K":"Ķ","k":"ķ","L":"Ŀ","l":"ľ",
    "M":"Μ","m":"ṁ","N":"Ń","n":"ñ","O":"Ø","o":"õ","P":"Ṗ","p":"ƥ",
    "Q":"Ɋ","q":"ʠ","R":"Ř","r":"ř","S":"Š","s":"š","T":"Ť","t":"ť",
    "U":"Ü","u":"ü","V":"Ṽ","v":"ṿ","W":"Ŵ","w":"ŵ","X":"Ẍ","x":"ẍ",
    "Y":"Ý","y":"ÿ","Z":"Ž","z":"ž"
})

def transform(s: str) -> str:
    # Evita tocar placeholders {name}
    parts = re.split(r"(\{[^}]+\})", s)
    out = []
    for p in parts:
        if p.startswith("{") and p.endswith("}"):
            out.append(p)
        else:
            p2 = p.translate(MAP)
            # allarga una mica
            p2 = re.sub(r"([A-Za-z])", r"\1·", p2)
            out.append(p2)
    return "⟦" + "".join(out) + "⟧"

def walk(obj):
    if isinstance(obj, dict):
        return {k: walk(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [walk(x) for x in obj]
    elif isinstance(obj, str):
        return transform(obj)
    else:
        return obj

def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/pseudo_localize.py <in.json> <out.json>")
        sys.exit(2)
    src, dst = sys.argv[1], sys.argv[2]
    data = json.load(open(src, encoding="utf-8"))
    pseudo = walk(data)
    json.dump(pseudo, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ Pseudo-local creat: {dst}")

if __name__ == "__main__":
    main()
