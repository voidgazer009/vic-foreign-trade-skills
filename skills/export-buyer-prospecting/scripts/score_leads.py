#!/usr/bin/env python3
"""Score and tier an export lead list against an ideal-customer profile.

Usage:
  python3 scripts/score_leads.py leads.csv --icp icp.json [--out scored.csv]

Input columns (see assets/leads-template.csv):
  company,website,country,buyer_type,employees,products_match,contact_name,contact_title,email,source,notes
  buyer_type: importer|distributor|wholesaler|brand_owner|retailer|ecommerce_seller (free text is mapped)
  products_match: yes|partial|no (or empty)
Output: same rows + score, tier (A/B/C/X), flags. Prints a summary.
Standard library only.
"""
import argparse, csv, json, re, sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
TYPE_ALIASES = {
    "importer": ["import", "importeur", "importateur", "importador", "importatore", "импорт"],
    "distributor": ["distribut", "dystrybut", "дистриб", "agent", "代理"],
    "wholesaler": ["wholesal", "großhand", "grosshand", "grossist", "mayorist", "atacad", "groothandel", "hurtown", "toptan", "卸"],
    "brand_owner": ["brand", "oem", "private label", "marke"],
    "retailer": ["retail", "chain", "store", "supermarket", "einzelhand", "detaillant"],
    "ecommerce_seller": ["amazon", "ecommerce", "e-commerce", "online shop", "shopify", "seller"],
}
TITLE_GOOD = re.compile(r"(purchas|buyer|buying|sourcing|procure|category|einkauf|achat|compra|acquist|inkoop|owner|founder|ceo|managing director|geschäftsführer|gérant|director)", re.I)


def norm_type(s):
    s = (s or "").lower()
    for key, al in TYPE_ALIASES.items():
        if s == key or any(a in s for a in al):
            return key
    return ""


def to_int(s):
    m = re.search(r"\d[\d,\.]*", s or "")
    if not m:
        return None
    return int(re.sub(r"[,\.]", "", m.group(0)))


def score_row(r, icp, kw, seen):
    w = icp["weights"]
    flags, s = [], 0.0
    cap_b = False
    name = (r.get("company") or "").strip()
    site = (r.get("website") or "").lower().strip()
    email = (r.get("email") or "").lower().strip()
    key = re.sub(r"[^a-z0-9]", "", (site.split("//")[-1].split("/")[0].replace("www.", "") or name.lower()))

    if not name:
        return 0, "X", ["missing company"]
    if key and key in seen:
        return 0, "X", [f"duplicate of row {seen[key]}"]
    seen[key] = r.get("_row")
    low = name.lower() + " " + site
    if any(m in low for m in kw["forwarder_markers"]):
        return 0, "X", ["looks like forwarder/logistics, not a buyer"]
    if any(m in site for m in kw["marketplace_domains"]):
        return 0, "X", ["marketplace page, not a company site"]
    if any(x.lower() in low for x in icp.get("exclude_keywords", [])):
        return 0, "X", ["matches exclude_keywords"]

    country = (r.get("country") or "").upper().strip()
    targets = [c.upper() for c in icp.get("target_countries", [])]
    if targets and country and country not in targets:
        return 0, "X", [f"country {country} not in targets"]
    if country and kw["countries"].get(country, {}).get("region_risk"):
        flags.append("sanctions screening required")
    s += w["country_match"] if country in targets else 0
    if not country:
        flags.append("country unknown")

    bt = norm_type(r.get("buyer_type"))
    bt_points = icp["buyer_types"].get(bt, 0)
    top = max(icp["buyer_types"].values()) or 1
    s += w["buyer_type"] * bt_points / top
    if not bt:
        flags.append("buyer type unknown")

    pm = (r.get("products_match") or "").lower()
    s += w["products_match"] * {"yes": 1, "y": 1, "partial": 0.5, "p": 0.5}.get(pm, 0)
    if not pm:
        flags.append("product fit unchecked")

    emp = to_int(r.get("employees"))
    lo, hi = icp.get("employees_min", 0), icp.get("employees_max", 10**9)
    if emp is None:
        s += w["company_size"] * 0.4
        flags.append("size unknown")
    elif lo <= emp <= hi:
        s += w["company_size"]
    elif emp > hi:
        s += w["company_size"] * 0.5
        flags.append("larger than ICP: expect long vendor onboarding")
    else:
        s += w["company_size"] * 0.2
        flags.append("smaller than ICP: MOQ risk (capped at tier B)")
        cap_b = True

    cname, ctitle = (r.get("contact_name") or "").strip(), (r.get("contact_title") or "").strip()
    if cname and TITLE_GOOD.search(ctitle):
        s += w["named_contact"]
    elif cname:
        s += w["named_contact"] * 0.6
        flags.append("contact is not a buyer role")
    else:
        flags.append("no named contact")

    if email:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
            flags.append("email malformed")
        else:
            local, dom = email.split("@", 1)
            webmail = any(dom.startswith(f) for f in ("gmail.", "yahoo.", "hotmail.", "outlook.", "qq.", "163.", "126.", "mail.ru", "yandex."))
            if local in kw["generic_inboxes"]:
                s += w["personal_email"] * 0.3
                flags.append("generic inbox")
            elif webmail:
                s += w["personal_email"] * 0.5
                flags.append("free webmail: verify it is the company")
            else:
                s += w["personal_email"]
    else:
        flags.append("no email")

    total = sum(w.values()) or 100
    score = round(100 * s / total)
    th = icp.get("tier_thresholds", {"A": 70, "B": 45})
    tier = "A" if score >= th["A"] else "B" if score >= th["B"] else "C"
    if cap_b and tier == "A":
        tier = "B"
    return score, tier, flags


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("leads")
    ap.add_argument("--icp", default=str(ASSETS / "icp-template.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    try:
        icp = json.loads(Path(a.icp).read_text(encoding="utf-8"))
        kw = json.loads((ASSETS / "keywords-multilingual.json").read_text(encoding="utf-8"))
        with open(a.leads, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError as e:
        sys.exit(f"File not found: {e.filename}")
    except json.JSONDecodeError as e:
        sys.exit(f"ICP file is not valid JSON: {e}")
    if not rows:
        sys.exit("Lead file has no rows. Fill assets/leads-template.csv first.")
    need = {"company", "website", "country", "buyer_type"}
    miss = need - set(rows[0].keys())
    if miss:
        sys.exit(f"Missing columns: {', '.join(sorted(miss))}. Use assets/leads-template.csv headers.")

    seen, out = {}, []
    for i, r in enumerate(rows, start=2):
        r["_row"] = i
        sc, tier, flags = score_row(r, icp, kw, seen)
        r.pop("_row")
        r.update(score=sc, tier=tier, flags="; ".join(flags))
        out.append(r)
    out.sort(key=lambda r: ("ABCX".index(r["tier"]), -r["score"]))

    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            wr.writeheader(); wr.writerows(out)
    counts = {t: sum(1 for r in out if r["tier"] == t) for t in "ABCX"}
    print(f"Scored {len(out)} leads: A={counts['A']} B={counts['B']} C={counts['C']} X={counts['X']}")
    for r in out[:10]:
        print(f"  {r['tier']} {r['score']:>3}  {r['company'][:40]:<40} {r['flags']}")
    if counts["A"] < 5:
        print("Fewer than 5 tier-A leads: widen buyer types or neighbouring countries.")
    if a.out:
        print(f"Wrote {a.out}")


if __name__ == "__main__":
    main()
