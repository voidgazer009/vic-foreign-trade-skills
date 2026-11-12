#!/usr/bin/env python3
"""Lint a cold B2B outreach email before sending.

Usage:
  python3 scripts/lint_outreach.py email.txt [--lead-country DE] [--touch 1]
  python3 scripts/lint_outreach.py note.txt --channel linkedin     # connection note / InMail
  python3 scripts/lint_outreach.py msg.txt --channel whatsapp      # only to buyers who gave you the number

For email, the first line may be "Subject: ...". Exit code 0 = pass, 1 = fix needed.
Standard library only.
"""
import argparse, re, sys

SPAM = ["guarantee", "best price", "cheapest", "100%", "act now", "urgent", "limited time", "click here",
        "risk-free", "no obligation", "winner", "$$$", "!!!", "dear sir", "dear madam", "dear sir/madam",
        "to whom it may concern", "professional manufacturer", "years of experience", "we are a leading",
        "hope this email finds you well", "high quality and competitive price", "factory direct",
        # AI tells: buyers get dozens of ChatGPT-written mails a day and delete them on sight
        "i hope this message finds you", "i trust this email finds you", "delve", "in today's fast-paced", "in today's competitive",
        "elevate your", "unlock the potential", "seamless", "game-changer", "game changer", "cutting-edge", "synergy",
        "i wanted to reach out", "i am reaching out to explore", "look no further", "rest assured", "tailored solutions"]
CONSENT_COUNTRIES = {"DE", "AT"}
TRADE_ACRONYMS = {"LFGB", "REACH", "ROHS", "FSC", "BSCI", "SEDEX", "AMFORI", "INCOTERMS", "GMBH", "SARL", "LLC"}


SPAM_RE = [r"(?<![-\w])free\b(?!-)", r"\bkostenlos", r"\bgratis\b", r"\bsonderangebot", r"\bgünstigste", r"\bmeilleur prix", r"\bmejor precio"]
OPTOUT = r"(no thanks|unsubscribe|won't write again|will not write again|opt out|abmelden|kein interesse|nicht mehr schreiben|pas intéress|désinscri|no me interesa|darse de baja|non interessat|cancellar)"
ADDRESS = r"(street|\bst\.|str\.|straße|strasse|road|\brd\b|avenue|\bave\b|district|province|building|floor|\bno\.\s*\d+|\b\d{5,6}\b|china|中国|zip|postal)"
CLAIMS = r"\b(LFGB|FDA|CE|REACH|RoHS|BSCI|ISO ?\d{4,5}|SGS|TÜV|TUV|UL|ETL|FSC|GRS|Sedex|EN ?\d{3,5}|\d[\d,\.]* ?(pcs|pieces|units|sets)|\d+\+? years?)\b"
PLACEHOLDER = r"\{[^}]+\}|\[[^\]]{2,40}\]"


DRAFT_HELD = []


def report(checks, draft):
    """Print checks; in draft mode placeholder failures are warnings, everything else still fails."""
    bad = 0
    for ok, msg in checks:
        if not ok and draft and ("placeholder" in msg or "postal address" in msg):
            DRAFT_HELD.append(msg)
            print("⚠ " + msg + " (draft: fill before sending)")
            continue
        print(("✓ " if ok else "✗ ") + msg)
        bad += not ok
    return bad


def spam_hits(low):
    hits = [s for s in SPAM if s in low]
    hits += [re.search(r, low).group(0) for r in SPAM_RE if re.search(r, low)]
    return hits


def lint_short(text, channel, draft=False):
    low, n = text.lower(), len(text.strip())
    words = len(re.findall(r"[\w'’-]+", text))
    hits = spam_hits(low)
    checks = [(not hits, "no spam or cliché phrases" + (f" (found: {', '.join(hits)})" if hits else "")),
              (not re.search(PLACEHOLDER, text), "no unfilled placeholders like {Name} or [Address]"),
              (not re.search(r"https?://", text), "no links in a first message"),
              (not re.search(r"(catalog|price list|attach|pdf)", low), "no catalogue or price list pushed")]
    if channel == "linkedin":
        checks += [(n <= 300, f"connection note ≤ 300 characters (now {n}; free accounts may be limited to 200)"),
                   (not re.search(r"(we are|our company|manufacturer|factory)", low), "about them, not about your company"),
                   (low.count("?") <= 1, "at most one question")]
    else:
        checks += [(words <= 60, f"≤ 60 words (now {words})"), (text.count("\n\n") <= 2, "short: max 3 paragraphs"),
                   (low.count("?") == 1, "exactly one question")]
    bad = report(checks, draft)
    if channel == "whatsapp":
        print("⚠ WhatsApp: message only buyers who gave you the number or contacted you first; stop on request. Max 3 nudges in a short window.")
    print("PASS" if not bad else f"FIX {bad} item(s)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--lead-country", default="")
    ap.add_argument("--touch", type=int, default=1, help="1 = first email (strictest)")
    ap.add_argument("--channel", choices=["email", "linkedin", "whatsapp"], default="email")
    ap.add_argument("--draft", action="store_true", help="placeholders such as {Your name} are allowed (warned, not failed) until the user fills them")
    ap.add_argument("--company", help="buyer company name, so its spelling in capitals is not flagged as shouting")
    a = ap.parse_args()
    try:
        text = open(a.file, encoding="utf-8").read()
    except FileNotFoundError:
        sys.exit(f"File not found: {a.file}")
    if not text.strip():
        sys.exit("Email is empty.")

    if a.channel != "email":
        sys.exit(lint_short(text, a.channel, a.draft))

    m = re.match(r"\s*subject:\s*(.+)", text, re.I)
    subject = m.group(1).strip() if m else ""
    body = text[m.end():] if m else text
    words = re.findall(r"[\w'’-]+", body)
    low = text.lower()
    limit = 120 if a.touch == 1 else 90
    checks = []
    checks.append((bool(subject), "has a Subject line"))
    checks.append((0 < len(subject) <= 60, f"subject 1–60 chars (now {len(subject)})"))
    pushy = re.search(r"(quotation|catalog(ue)?|price ?list|offer|angebot|katalog|preisliste)\b", subject, re.I)
    if pushy and re.search(r"\b(your|ihr|ihren|votre|su|vostro)\b[^.]*" + re.escape(pushy.group(0)), subject, re.I):
        pushy = None  # "for your autumn catalogue" is about the buyer, not a pitch
    checks.append((not pushy or a.touch > 1,
                   "subject avoids 'quotation/catalog/price list/offer' on first touch"))
    checks.append((len(words) <= limit, f"body ≤ {limit} words (now {len(words)})"))
    hits = spam_hits(low)
    checks.append((not hits, "no spam or cliché phrases" + (f" (found: {', '.join(hits)})" if hits else "")))
    checks.append((not re.search(PLACEHOLDER, text), "no unfilled placeholders like {Name} or [Address]"))
    checks.append((len(re.findall(r"https?://", text)) <= 1, "at most one link"))
    checks.append((not re.search(r"attach|附件|pdf\b|brochure", low) or a.touch > 1, "no attachment on first touch"))
    checks.append((1 <= body.count("?") <= 2, "has one clear question as the CTA"))
    checks.append((bool(re.search(OPTOUT, low)), "has an opt-out line"))
    sig = "\n".join(body.strip().splitlines()[-4:])
    checks.append((bool(re.search(ADDRESS, sig, re.I)) and not re.search(PLACEHOLDER, sig), "signature includes a real postal address"))
    checks.append((text.count("!") <= 1, "at most one exclamation mark"))
    fda = re.search(r"\bfda[- ](approved|certified|certificate|approval|registered product)\b", low)
    checks.append((not fda, "no 'FDA approved/certified' (FDA does not approve or certify food-contact items; say 'tested to FDA 21 CFR food-contact requirements, report available')"))
    names = set(re.findall(r"\b[A-Z]{5,}\b", subject)) | {w.upper() for w in (a.company or "").split()}
    shout = [w for w in re.findall(r"\b[A-Z]{5,}\b", body) if w not in TRADE_ACRONYMS and w not in names]
    checks.append((not shout, "no SHOUTING words" + (f" (found: {', '.join(shout)})" if shout else "")))

    bad = report(checks, a.draft)
    claims = sorted(set(m.group(0) for m in re.finditer(CLAIMS, body)))
    if claims:
        print("⚠ Confirm with the user these claims are true before sending: " + ", ".join(claims))
    if a.lead_country.upper() in CONSENT_COUNTRIES:
        print("⚠ DE/AT: email marketing needs prior consent even B2B (UWG §7). Prefer LinkedIn/phone first, or keep this a strictly individual inquiry.")
    print(("DRAFT PASS: fill every {placeholder} with the user's real details, then re-run without --draft" if a.draft and DRAFT_HELD else "PASS") if not bad else f"FIX {bad} item(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
