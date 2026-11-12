#!/usr/bin/env python3
"""Lint a quotation or proforma invoice (PI) before it goes to the buyer.

Usage:
  python3 scripts/lint_quote.py quote.txt [--mode sea|air|courier|rail|multimodal] [--dest US]

Catches the mistakes that cost margin or money (Incoterms® 2020 rules):
  - Incoterm without a named port/place, or without "Incoterms 2020"
  - FOB / FAS / CFR / CIF used for air, courier, rail or containers to a door (use FCA / CPT / CIP)
  - EXW from China (the buyer cannot clear Chinese export customs; use FCA)
  - DDP without HS code and duty line (DDP is the only rule where the seller pays import duty)
  - CIF/CIP without the insurance basis (CIF: ICC (C) min 110%; CIP: ICC (A) min 110%)
  - missing currency, validity date, MOQ, lead time, payment terms, bank-charge line
  - ambiguous "30/70" with no trigger for the balance (before shipment? against B/L copy?)
  - no "bank details never change by email" line (email-hacking scams)
Exit code 1 if any ✗. Python 3.9+ standard library only.
"""
import argparse, re, sys

TERMS = ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CPT", "CIP", "DAP", "DPU", "DDP"]
SEA_ONLY = {"FAS", "FOB", "CFR", "CIF"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--mode", choices=["sea", "air", "courier", "rail", "multimodal"], help="transport mode, if known")
    ap.add_argument("--dest", default="", help="destination country ISO code")
    ap.add_argument("--draft", action="store_true", help="placeholders are warned, not failed, until the user fills them")
    a = ap.parse_args()
    raw = open(a.file, encoding="utf-8").read()
    # mask mentions that are not the chosen term: "unless DDP", "21 CFR 177" (US food-contact rules), "DDP is ..."
    t = re.sub(r"(?i)\b(unless|except|other than|not|instead of|rather than)\s+(under\s+)?(EXW|FCA|FAS|FOB|CFR|CIF|CPT|CIP|DAP|DPU|DDP)\b", r"\1 \2-", raw)
    t = re.sub(r"(?i)\b\d+\s*C\.?F\.?R\.?(\s*(§|part|sec\.?)?\s*[\d.]+)?", "US-REG", t)
    up = t.upper()
    low = t.lower()
    found = [x for x in TERMS if re.search(rf"\b{x}\b", up)]
    res = []  # (ok, level, message)

    def chk(ok, msg, warn=False):
        res.append((ok, "⚠" if (warn and not ok) else ("✓" if ok else "✗"), msg))

    ph = re.findall(r"\{[^}]{1,40}\}", t)
    chk(not ph, "no unfilled placeholders" + (f" (found {', '.join(ph[:4])})" if ph else ""), warn=a.draft)
    chk(bool(found), "Incoterm stated" + (f" ({', '.join(found)})" if found else ""))
    for term in found:
        m = re.search(rf"\b{term}\b[\s,:-]*([A-Za-z][A-Za-z .'-]{{2,30}})", t, re.I)
        place = m.group(1).strip() if m else ""
        named = bool(place) and not re.match(r"(price|incoterms?|term|basis|per|usd|eur|unit|total|and|or)\b", place, re.I)
        chk(named, f"{term} has a named port/place (e.g. '{term} Ningbo')")
    chk(bool(re.search(r"incoterms?\s*®?\s*2020", low)), "says 'Incoterms® 2020' (L/C banks may treat a missing version as a discrepancy)", warn=True)
    mode = a.mode or ("air" if re.search(r"\b(air ?freight|by air|airport)\b", low) else "courier" if re.search(r"\b(dhl|fedex|ups|tnt|express|courier)\b", low)
                      else "rail" if re.search(r"\b(rail|train)\b", low) else None)
    if mode and mode not in ("sea",):
        bad = [x for x in found if x in SEA_ONLY]
        chk(not bad, f"no sea-only term for {mode} transport" + (f" (found {', '.join(bad)}: use FCA / CPT / CIP)" if bad else ""))
    if "EXW" in found:
        chk(False, "EXW from China: the buyer cannot clear Chinese export customs. Offer FCA (your factory or warehouse) instead", warn=True)
    if "DDP" in found:
        chk(bool(re.search(r"\b(hs|hts)\s*(code)?\s*[:#]?\s*\d{4}", low)), "DDP lists the HS/HTS code")
        chk(bool(re.search(r"\b(duty|duties|tariff|import tax|vat|gst)\b", low)), "DDP has a duty / import-tax line (you pay it under DDP)")
        chk(False, "DDP: you carry every tariff change until delivery; ICC suggests DAP when duties are volatile" + (" (US duties change often)" if a.dest.upper() == "US" else ""), warn=True)
    if "CIF" in found or "CIP" in found:
        chk(bool(re.search(r"insur", low)), "CIF/CIP states the insurance cover (CIF: ICC (C) min 110%; CIP: ICC (A) min 110%)")
    chk(bool(re.search(r"\b(usd|eur|gbp|rmb|cny|aud|cad|jpy|us\$|\$|€|£)", low)), "currency stated")
    chk(bool(re.search(r"\b(valid(ity)?|expires?|good until)\b", low)), "validity date stated (e.g. 'valid until 2026-12-15')")
    chk(bool(re.search(r"\b(moq|minimum order)\b", low)), "MOQ stated")
    chk(bool(re.search(r"\b(lead ?time|delivery time|production time|ready in|days after)\b", low)), "lead time stated")
    pay = re.search(r"\b(payment|t/?t|l/?c|d/?p|d/?a|deposit|balance|paypal|o/?a)\b", low)
    chk(bool(pay), "payment terms stated")
    split = re.search(r"\b(\d{2})\s*%?\s*/\s*(\d{2})\s*%?", t) or re.search(r"\b\d{2}\s*%\s*(deposit|t/?t|advance)", low)
    if split:
        trig = re.search(r"(before (shipment|loading|delivery)|against (the )?(copy|scan)( of)? (the )?(b/?l|bill of lading)|after inspection|before release)", low)
        chk(bool(trig), "balance trigger is explicit ('balance before shipment' or 'against copy of B/L')")
    chk(bool(re.search(r"bank (charges?|fees?)", low)), "says who pays bank charges", warn=True)
    chk(bool(re.search(r"(never|not) (be )?chang\w* (by|via) (e-?mail|email)|bank details (are )?(fixed|will not change)", low)),
        "states that bank details never change by email (anti email-hacking clause)", warn=True)
    if a.dest.upper() == "US":
        chk(bool(re.search(r"tariff|duty|duties", low)), "US: says who bears tariff changes after the quote date", warn=True)

    for ok, lvl, msg in res:
        print(f"{lvl} {msg}")
    bad = sum(1 for ok, lvl, _ in res if lvl == "✗")
    print(("DRAFT PASS: fill the placeholders, then re-run without --draft" if a.draft and ph else "PASS") if not bad else f"FIX {bad} item(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
