#!/usr/bin/env python3
"""Triage an inbound inquiry (Alibaba / Made-in-China / website form / trade-show email) before quoting.

Usage:
  python3 scripts/triage_inquiry.py inquiry.txt [--from buyer@domain.com] [--company "Claimed Co Ltd"] [--messages 3]
  cat inquiry.txt | python3 scripts/triage_inquiry.py - --from x@gmail.com

Scores low-intent and price-fishing signals (no company, "best price for all products", no quantity/spec,
push to WhatsApp, free mail with a big order, several unrelated categories...) and positive signals
(quantity, destination, Incoterm, spec, certification, timeline, company website).
Verdict: VERIFY (sender domain imitates the company it names: confirm through the real website first),
QUOTE (send a priced offer), ASK-FIRST (send the 5-field ask-back, give only a price band),
ARCHIVE (polite one-liner, no prices). Prints the matching reply to adapt. Python 3.9+ standard library only.

Most "send best price" emails are honest first-round benchmarking: buyers ask 20-30 suppliers and shortlist 5-10.
The goal is to get shortlisted without leaking a full price list, not to insult the buyer.
"""
import argparse, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_lookalike import judge  # noqa: E402

FREE_MAIL = r"@(gmail|yahoo|hotmail|outlook|live|aol|icloud|mail|gmx|web|yandex|proton|protonmail|qq|163|126|sina)\."
NEG = [
    (r"\b(best|lowest|cheapest|good|final)\s+(price|offer|quotation)s?\b", 1, "asks only for 'best price'"),
    (r"\b(all|full|whole)\s+(your\s+)?(products?|items?|range|catalog(ue)?|price ?list)\b|\bprice ?list\b", 2, "wants a full price list / all products"),
    (r"\b(urgent(ly)?|asap|immediately|right now)\b", 1, "urgency pressure"),
    (r"\bwhats ?app\b|\bwechat\b|\btelegram\b|\bviber\b", 1, "pushes the chat off email/platform"),
    (r"\b(registration|certificate|inspection|import licen[cs]e|handling)\s+fee\b|\bpay\b.{0,30}\bfee\b", 3, "asks the seller to pay a fee (classic scam)"),
    (r"\bfree samples?\b", 1, "asks for free samples before any detail"),
    (r"\bin business (for )?\d+ years\b|\bwe are a (big|large|leading) (company|importer)\b", 1, "boasts size instead of giving a company name/URL"),
    (r"\b(dear (sir|madam|supplier|seller)|dear sir/madam|hello dear)\b", 1, "generic greeting (template sent to many suppliers)"),
]
POS = [
    (r"\b\d[\d,\.]*\s?(k\s)?(pcs|pieces|units|sets|cartons|ctns|pairs|kg|tons?|mt|containers?|x?\s?40\s?(hq|gp|ft)|x?\s?20\s?(gp|ft))\b|\b(moq|quantity|qty)\b[^\n]{0,15}\d", "states a quantity"),
    (r"\b(fob|cif|cfr|exw|ddp|dap|fca|cpt|cip|dpu)\b", "names an Incoterm"),
    (r"\b(port of|destination|deliver(y|ed)? to|ship(ping)? to)\b|\b(hamburg|rotterdam|antwerp|felixstowe|los angeles|long beach|new york|savannah|houston|jebel ali|santos|manzanillo|veracruz|sydney|melbourne|toronto|vancouver)\b", "names a destination"),
    (r"\b(size|dimension|material|capacity|spec(ification)?s?|drawing|model|colou?r|logo|packaging|voltage|weight)\b", "gives or asks for a spec"),
    (r"\b(ce|fda|lfgb|reach|rohs|ul|etl|iso ?\d{4,5}|bsci|sedex|en ?\d{3,5}|ukca|cpsia|prop ?65)\b", "mentions a certification"),
    (r"\b(next|this)\s+(month|quarter|season|year)\b|\b(q[1-4]|january|february|march|april|may|june|july|august|september|october|november|december)\b|\bdeadline\b|\bweeks?\b", "has a timeline"),
    (r"\b(our (customers?|stores?|shops?|clients?)|we (sell|supply|distribute) (to|in)|retail chain|supermarkets?|for (our|the) (market|brand))\b", "says who they sell to"),
    (r"https?://|www\.|\b[a-z0-9-]+\.(com|de|fr|co\.uk|nl|it|es|com\.au|ca|com\.mx|pl|se)\b", "gives a website"),
]
CATS = ["bottle|cup|mug|drinkware", "led|lamp|light", "furniture|chair|table|sofa", "garment|t-shirt|apparel|clothing|textile",
        "shoe|footwear", "phone|charger|cable|electronic", "toy", "tool|hardware", "kitchen|cookware|pan|pot", "bag|backpack|luggage",
        "solar|battery|inverter", "cosmetic|beauty", "machine|machinery", "auto parts|car parts", "pet"]

ASK_BACK = """Hi {name},

Thanks for your inquiry about {product}. To quote you an exact price rather than a rough one, could you confirm:
1. Model or spec (size, material, finish, logo)
2. Quantity per order and per year
3. Destination port or city
4. Preferred Incoterm (FOB {port} / CIF / DAP)
5. Any certification needed for your market

For orientation, this range usually runs {band} depending on spec and quantity.

Best regards,
{signature}"""
ARCHIVE = """Hi,

Thank you for your message. We quote per project once we know the model, quantity and destination. If you send those, we will come back with a firm offer within one working day.

Best regards,
{signature}"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="inquiry text file, or - for stdin")
    ap.add_argument("--from", dest="sender", default="", help="sender email address")
    ap.add_argument("--company", default="", help="company name the sender claims")
    ap.add_argument("--messages", type=int, default=1, help="how many messages so far that only asked for price")
    a = ap.parse_args()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    low = text.lower()
    neg, pos = [], []
    for pat, w, why in NEG:
        if re.search(pat, low):
            neg.append((w, why))
    for pat, why in POS:
        if re.search(pat, low):
            pos.append(why)
    snd = a.sender.lower()
    if snd and re.search(FREE_MAIL, snd):
        big = re.search(r"\b\d+\s?(x\s?)?(40|20)\s?(hq|gp|ft)|containers?\b|\b\d{4,}[\d,]*\s?(pcs|pieces|units)\b", low)
        neg.append((2 if big else 1, "free webmail" + (" with a big order" if big else "")))
    if snd and "@" in snd:
        sdom = snd.split("@")[1]
        body_doms = {d.lower() for d in re.findall(r"(?:www\.|@|https?://)([a-z0-9-]+(?:\.[a-z0-9-]+)+)", low)}
        for bd in sorted(body_doms - {sdom}):
            hit = judge(bd, sdom)
            if hit:
                neg.append((4, f"sender domain imitates the company's own site ({hit}): possible impersonation"))
                break
    if a.company and snd and "@" in snd:
        dom = re.sub(r"[^a-z0-9]", "", snd.split("@")[1].split(".")[0])
        core = re.sub(r"\b(gmbh|ltd|llc|inc|co|sarl|srl|bv|sa|ag|limited|company|trading|group)\b|[^a-z0-9]", "", a.company.lower())
        if not re.search(FREE_MAIL, snd) and core and dom not in core and core[:5] not in dom:
            neg.append((2, f"email domain '{dom}' does not match claimed company '{a.company}'"))
    if not a.company and not re.search(r"\b(gmbh|ltd|llc|inc|s\.?a\.?r\.?l|s\.?r\.?l|b\.?v|ag|co\.|company|limited|corp)\b", low):
        neg.append((1, "no company name"))
    cats = sum(1 for c in CATS if re.search(r"\b(" + c + r")", low))
    if cats >= 3:
        neg.append((2, f"asks about {cats} unrelated product categories (often a trader collecting prices)"))
    if a.messages >= 2 and "states a quantity" not in pos:
        neg.append((2, f"{a.messages} messages that only ask for price, no spec or quantity"))
    if len(text.split()) < 25:
        neg.append((1, "very short, template-like message"))
    n = sum(w for w, _ in neg)
    p = len(pos)
    scam = any("fee" in why for _, why in neg)
    imp = any("impersonation" in why for _, why in neg)
    if imp:
        verdict = "VERIFY"
    elif scam or n >= 5:
        verdict = "ARCHIVE"
    elif p >= 3 and n <= 2:
        verdict = "QUOTE"
    else:
        verdict = "ASK-FIRST"
    print(f"Verdict: {verdict}  (risk {n}, intent {p}/8)")
    for w, why in neg:
        print(f"  ✗ {why} (+{w})")
    for why in pos:
        print(f"  ✓ {why}")
    if scam:
        print("  ⚠ Fee requests are a known scam pattern. Do not pay anything; see references/compliance.md fake-buyer signals.")
    if verdict == "VERIFY":
        print("\nNext: do not quote or send samples yet. Write to the company through the contact on its real website")
        print("(or call its public number) and ask whether this request is theirs. Run scripts/check_lookalike.py on the sender.")
        return
    if verdict == "QUOTE":
        print("\nNext: send a full quote with assets/quote-sheet-template.md and lint it with scripts/lint_quote.py.")
        print("Quote only the items asked for; never attach the whole price list.")
    elif verdict == "ASK-FIRST":
        print("\nNext: reply within 4 working hours with the ask-back below. Give a price band, not a SKU price list.\n")
        print(ASK_BACK)
    else:
        print("\nNext: archive or send this one-liner. No prices.\n")
        print(ARCHIVE)
    print("\nVerify the company (scripts/verify_buyer.py) before samples, credit terms or any payment.")


if __name__ == "__main__":
    main()
