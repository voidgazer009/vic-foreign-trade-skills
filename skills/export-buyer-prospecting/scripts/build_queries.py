#!/usr/bin/env python3
"""Build localized buyer-search queries for each target country.

Usage:
  python3 scripts/build_queries.py --product "LED panel light" --countries DE,FR [--local-product "LED-Panel"] [--out queries.md]

Reads assets/keywords-multilingual.json. Standard library only.
Pass --local-product "de=LED-Panel,fr=panneau LED" to use the product name in each language
(recommended: buyers search in their own language).
"""
import argparse, json, sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "keywords-multilingual.json"


def parse_local(s):
    out = {}
    for part in filter(None, (s or "").split(",")):
        if "=" not in part:
            sys.exit(f"--local-product expects lang=name pairs, got '{part}'")
        k, v = part.split("=", 1)
        out[k.strip().lower()] = v.strip()
    return out


def queries_for(code, cfg, langs, product, local):
    lines = [f"## {cfg['name']} ({code}) · languages: {', '.join(cfg['lang'])}", ""]
    tld = cfg["tld"]
    for lg in cfg["lang"]:
        kw = langs.get(lg)
        if not kw:
            continue
        p = local.get(lg, product)
        lines += [f"### {lg}", "Google (set region gl=%s):" % cfg["gl"], "```"]
        for role in ("importer", "distributor", "wholesaler"):
            lines.append(f'"{p}" {kw[role]} site:.{tld}')
        lines.append(f'"{p}" ("{kw["importer"]}" OR "{kw["distributor"]}") -alibaba -amazon -made-in-china')
        lines.append(f'"{p}" "{kw["supplier_wanted"]}"')
        lines.append(f'"{p}" {kw["trade_show"]} {cfg["name"]}')
        lines.append(f'intitle:"{kw["distributor"]}" "{p}" filetype:pdf')
        lines += ["```", ""]
    lines += [
        "LinkedIn (people search via Google):",
        "```",
        f'site:linkedin.com/in ("purchasing manager" OR "category manager" OR "sourcing manager" OR "head of buying") "{product}" "{cfg["name"]}"',
        f'site:linkedin.com/company "{product}" {langs[cfg["lang"][0]]["distributor"]} "{cfg["name"]}"',
        "```",
        "",
    ]
    if cfg.get("region_risk"):
        lines += ["> ⚠ Sanctions-sensitive market: screen every company and owner against OFAC SDN, EU and UN lists before contact.", ""]
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--product", required=True, help="product name in English")
    ap.add_argument("--countries", required=True, help="ISO-2 codes, comma separated, e.g. DE,FR,US")
    ap.add_argument("--local-product", default="", help='localized names, e.g. "de=Trinkflasche,fr=gourde"')
    ap.add_argument("--out", help="write markdown here (default: stdout)")
    a = ap.parse_args()

    try:
        data = json.loads(ASSETS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"Missing {ASSETS}. Reinstall the skill folder.")
    langs, countries = data["languages"], data["countries"]
    local = parse_local(a.local_product)

    out = [f"# Buyer search queries · {a.product}", ""]
    unknown = []
    for code in [c.strip().upper() for c in a.countries.split(",") if c.strip()]:
        if code not in countries:
            unknown.append(code)
            continue
        out += queries_for(code, countries[code], langs, a.product, local)
    if unknown:
        out += [f"> Not in keyword table: {', '.join(unknown)}. Use English queries and add the country to assets/keywords-multilingual.json.", ""]
    missing_local = [lg for c in a.countries.upper().split(",") if c.strip() in countries
                     for lg in countries[c.strip()]["lang"] if lg != "en" and lg not in local]
    if missing_local:
        out += [f"> Tip: product name not localized for {', '.join(sorted(set(missing_local)))}. Buyers search in their own language; pass --local-product.", ""]

    text = "\n".join(out)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"Wrote {a.out} ({text.count(chr(10))} lines)")
    else:
        print(text)


if __name__ == "__main__":
    main()
