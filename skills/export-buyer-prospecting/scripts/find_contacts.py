#!/usr/bin/env python3
"""Find the decision-maker: role search queries + likely email addresses for a named person.

Usage:
  python3 scripts/find_contacts.py roles --company "Example Trading GmbH" --country DE [--industrial]
  python3 scripts/find_contacts.py email --name "Anna Schmidt" --domain example-trading.de [--known "j.mueller@example-trading.de=Jan Müller"]
  python3 scripts/find_contacts.py batch scored.csv --out with_guesses.csv

roles : LinkedIn/Google queries for the buying committee (purchasing + technical/product roles).
email : candidate addresses ranked by how common the pattern is; with --known, the company's real pattern is
        inferred from one address you already found and used first. Guesses are UNVERIFIED: never send to a guess
        without checking it (see references/decision-makers.md).
batch : fills an email_guess column for rows that have contact_name but no email. Uses an email_domain column
        when present, else website; the shop site can differ from the mail domain (kalatex.shop vs kalatex.de).
Standard library only.
"""
import argparse, csv, re, sys, unicodedata
from pathlib import Path

ROLES_BUY = ["Purchasing Manager", "Head of Purchasing", "Procurement Manager", "Buyer", "Sourcing Manager", "Category Manager"]
ROLES_TECH = ["Technical Manager", "Engineering Manager", "Product Manager", "Quality Manager", "R&D Manager"]
ROLES_SMB = ["Owner", "Founder", "Managing Director", "CEO", "General Manager"]
LOCAL_TITLES = {
    "DE": ["Einkaufsleiter", "Leiter Einkauf", "Einkäufer", "Geschäftsführer"], "AT": ["Einkaufsleiter", "Einkäufer", "Geschäftsführer"],
    "FR": ["Responsable achats", "Acheteur", "Gérant", "Directeur général"], "ES": ["Jefe de compras", "Responsable de compras", "Gerente"],
    "MX": ["Gerente de compras", "Comprador", "Director general"], "IT": ["Responsabile acquisti", "Buyer", "Amministratore delegato"],
    "BR": ["Gerente de compras", "Comprador", "Diretor"], "NL": ["Inkoper", "Hoofd inkoop", "Directeur"], "PL": ["Kierownik zakupów", "Kupiec", "Prezes"],
    "JP": ["購買部長", "調達担当", "代表取締役"], "KR": ["구매팀장", "구매담당"],
}
PATTERNS = [  # (pattern, rough global share rank)
    "{first}.{last}", "{f}.{last}", "{first}", "{f}{last}", "{first}{last}", "{last}", "{first}_{last}", "{last}.{first}", "{first}.{l}", "{first}-{last}",
]


PARTICLES = {"von", "van", "de", "der", "den", "da", "di", "del", "della", "la", "le", "du", "ten", "ter", "zu", "dos", "das", "y"}


def ascii_variants(s, umlaut_first=True):
    """'Müller' -> ['mueller', 'muller'] (companies use both)."""
    s = s.strip().lower()
    out = []
    for umlaut in ((True, False) if umlaut_first else (False, True)):
        t = s
        if umlaut:
            for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ø", "oe"), ("å", "aa"), ("æ", "ae")):
                t = t.replace(a, b)
        t = t.replace("ß", "ss")
        t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
        t = re.sub(r"[^a-z\s-]", "", t)
        if t not in out:
            out.append(t)
    return out


def name_variants(full, umlaut_first=True):
    """Return [(first, last), ...] most likely first. Handles umlauts, double first names, particles, double surnames."""
    res = []
    for t in ascii_variants(full, umlaut_first):
        parts = t.split()
        if len(parts) < 2:
            continue
        first, rest = parts[0], parts[1:]
        firsts = [first] if "-" not in first else [first, first.replace("-", ""), first.split("-")[0]]
        core = [w for w in rest if w not in PARTICLES]
        lasts = []
        if len(rest) > 1 and any(w in PARTICLES for w in rest):
            lasts += ["".join(rest), core[-1] if core else rest[-1]]
        elif len(rest) > 1:  # e.g. Spanish double surname: García López
            lasts += [rest[0], "".join(rest), rest[-1]]
        else:
            lasts.append(rest[0].replace("-", ""))
            if "-" in rest[0]:
                lasts.append(rest[0])
        for f in firsts:
            for l in lasts:
                if (f, l) not in res and f and l:
                    res.append((f, l))
    return res


def split_name(full):
    v = name_variants(full)
    return v[0] if v else None


def fill(p, first, last):
    return p.format(first=first, last=last, f=first[0], l=last[0])


def infer_pattern(known_email, known_name):
    """Return (pattern, umlaut_style) where umlaut_style True means ü→ue, False means ü→u."""
    local = known_email.split("@")[0].lower()
    for style in (True, False):
        for fl in name_variants(ascii_variants(known_name, style)[0]):
            for p in PATTERNS:
                if fill(p, *fl) == local:
                    return p, style
    return None, True


def guesses(name, domain, known=None, warn=print):
    pat, style = None, True
    if known:
        if "=" not in known:
            warn("⚠ --known needs \"email=Full Name\" to learn the pattern, e.g. \"a.schmidt@firm.de=Anna Schmidt\". Ignored.")
        else:
            ke, kn = known.split("=", 1)
            pat, style = infer_pattern(ke.strip(), kn.strip())
            if not pat:
                warn(f"⚠ Could not match {ke.strip()} to a known pattern for '{kn.strip()}'. Showing common patterns; tell the agent the pattern if you can see it.")
    nv = name_variants(name, style)
    if not nv:
        return [], None
    order = ([pat] if pat else []) + [p for p in PATTERNS if p != pat]
    domain = re.sub(r"^(https?://)?(www\.)?", "", domain.lower()).split("/")[0].split("@")[-1]
    out = []
    # best pattern across every name variant first, then other patterns for the main variant
    for p in order[:1]:
        out += [f"{fill(p, *fl)}@{domain}" for fl in nv]
    for p in order[1:]:
        out += [f"{fill(p, *nv[0])}@{domain}"]
    seen = []
    for e in out:
        if e not in seen:
            seen.append(e)
    return seen, pat


def has_mx(domain):
    try:
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from check_domain import dns, dns_status
        return dns_status(domain) != 3 and bool(dns(domain, "MX"))
    except Exception:
        return None  # offline: unknown


def cmd_roles(a):
    roles = ROLES_BUY + (ROLES_TECH if a.industrial else []) + ROLES_SMB
    local = LOCAL_TITLES.get(a.country.upper(), [])
    q = " OR ".join(f'"{r}"' for r in roles[:8] + local[:3])
    print(f"# Buying committee at {a.company}\n")
    print("Google → LinkedIn people:")
    print(f'  site:linkedin.com/in "{a.company}" ({q})')
    print("Company team pages:")
    print(f'  "{a.company}" (team OR "about us" OR impressum OR "ansprechpartner" OR "contact") ({" OR ".join(chr(34)+r+chr(34) for r in (local or ROLES_BUY)[:4])})')
    print("\nWho to contact first:")
    print("  • Under ~50 staff: the owner / managing director decides; write to them.")
    print("  • 50–500: purchasing or category manager; cc nobody on the first email.")
    if a.industrial:
        print("  • Industrial / technical products: also reach the technical or engineering manager; they approve the spec before purchasing compares price.")
    print("  • Germany/Austria: the Impressum page legally lists the Geschäftsführer (managing director).")


def cmd_email(a):
    g, pat = guesses(a.name, a.domain, a.known)
    if not g:
        sys.exit("Give a first and last name, e.g. --name \"Anna Schmidt\".")
    dom = g[0].split("@")[1]
    mx = has_mx(dom)
    if mx is False:
        print(f"✗ {dom} has no mail server (MX). The company may mail from another domain (check its Impressum/contact page or any address you found).")
    print(f"Pattern inferred from known address: {pat}" if pat else "No known address: ranked by how common each pattern is in B2B.")
    for i, e in enumerate(g[:6], 1):
        print(f"  {i}. {e}")
    print("UNVERIFIED. Verify before sending (references/decision-makers.md). A bounce costs more domain reputation than a skipped lead.")


def cmd_batch(a):
    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("Empty CSV.")
    n = 0
    for r in rows:
        r.setdefault("email_guess", "")
        dom = r.get("email_domain") or r.get("website")
        if r.get("contact_name") and not r.get("email") and dom:
            g, _ = guesses(r["contact_name"], dom, warn=lambda m: None)
            if g:
                r["email_guess"] = g[0] + " (unverified)"
                n += 1
    out = a.out or a.csv
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"Added {n} unverified guesses → {out}. Verify each before sending.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("roles"); r.add_argument("--company", required=True); r.add_argument("--country", default=""); r.add_argument("--industrial", action="store_true")
    e = sub.add_parser("email"); e.add_argument("--name", required=True); e.add_argument("--domain", required=True); e.add_argument("--known", help='"email=Full Name" of someone at the same company')
    b = sub.add_parser("batch"); b.add_argument("csv"); b.add_argument("--out")
    a = ap.parse_args()
    {"roles": cmd_roles, "email": cmd_email, "batch": cmd_batch}[a.cmd](a)


if __name__ == "__main__":
    main()
