#!/usr/bin/env python3
"""Lint a cold B2B outreach email before sending.

Usage:
  python3 scripts/lint_outreach.py email.txt [--lead-country DE] [--touch 1]

The file's first line may be "Subject: ...". Exit code 0 = pass, 1 = fix needed.
Standard library only.
"""
import argparse, re, sys

SPAM = ["free", "guarantee", "best price", "cheapest", "100%", "act now", "urgent", "limited time", "click here",
        "risk-free", "no obligation", "winner", "$$$", "!!!", "dear sir", "dear madam", "dear sir/madam",
        "to whom it may concern", "professional manufacturer", "years of experience", "we are a leading",
        "hope this email finds you well", "high quality and competitive price", "factory direct"]
CONSENT_COUNTRIES = {"DE", "AT"}
TRADE_ACRONYMS = {"LFGB", "REACH", "ROHS", "FSC", "BSCI", "SEDEX", "AMFORI", "INCOTERMS", "GMBH", "SARL", "LLC"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--lead-country", default="")
    ap.add_argument("--touch", type=int, default=1, help="1 = first email (strictest)")
    a = ap.parse_args()
    try:
        text = open(a.file, encoding="utf-8").read()
    except FileNotFoundError:
        sys.exit(f"File not found: {a.file}")
    if not text.strip():
        sys.exit("Email is empty.")

    m = re.match(r"\s*subject:\s*(.+)", text, re.I)
    subject = m.group(1).strip() if m else ""
    body = text[m.end():] if m else text
    words = re.findall(r"[\w'’-]+", body)
    low = text.lower()
    limit = 120 if a.touch == 1 else 90
    checks = []
    checks.append((bool(subject), "has a Subject line"))
    checks.append((0 < len(subject) <= 60, f"subject 1–60 chars (now {len(subject)})"))
    checks.append((not re.search(r"(quotation|catalog|price list|offer)\b", subject, re.I) or a.touch > 1,
                   "subject avoids 'quotation/catalog/price list/offer' on first touch"))
    checks.append((len(words) <= limit, f"body ≤ {limit} words (now {len(words)})"))
    hits = [s for s in SPAM if s in low]
    checks.append((not hits, "no spam or cliché phrases" + (f" (found: {', '.join(hits)})" if hits else "")))
    checks.append((not re.search(r"\{[^}]+\}|\[(first ?name|company|name)\]", text, re.I), "no unfilled placeholders"))
    checks.append((len(re.findall(r"https?://", text)) <= 1, "at most one link"))
    checks.append((not re.search(r"attach|附件|pdf\b|brochure", low) or a.touch > 1, "no attachment on first touch"))
    checks.append((1 <= body.count("?") <= 2, "has one clear question as the CTA"))
    checks.append((bool(re.search(r"(no thanks|unsubscribe|won't write again|opt out|abmelden)", low)), "has an opt-out line"))
    checks.append((bool(re.search(r"\d{3,}|street|str\.|road|rd\.|district|province|zip|postal", low)), "signature includes a postal address"))
    checks.append((text.count("!") <= 1, "at most one exclamation mark"))
    shout = [w for w in re.findall(r"\b[A-Z]{5,}\b", body) if w not in TRADE_ACRONYMS]
    checks.append((not shout, "no SHOUTING words" + (f" (found: {', '.join(shout)})" if shout else "")))

    bad = 0
    for ok, msg in checks:
        print(("✓ " if ok else "✗ ") + msg)
        bad += not ok
    if a.lead_country.upper() in CONSENT_COUNTRIES:
        print("⚠ DE/AT: email marketing needs prior consent even B2B (UWG §7). Prefer LinkedIn/phone first, or keep this a strictly individual inquiry.")
    print("PASS" if not bad else f"FIX {bad} item(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
