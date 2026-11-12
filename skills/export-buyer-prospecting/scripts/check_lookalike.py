#!/usr/bin/env python3
"""Catch look-alike sender domains before money moves (email-hacking / BEC scams).

Usage:
  python3 scripts/check_lookalike.py --known example-trading.de --sender anna@examp1e-trading.de
  python3 scripts/check_lookalike.py --known example-trading.de --thread thread.txt      # every address in a pasted thread
  python3 scripts/check_lookalike.py --pipeline pipeline.csv --sender anna@examp1e-trading.de  # known domains from your leads

Flags: one or two characters changed (l/1/I, rn/m, 0/o, vv/w), letters swapped, hyphen added or removed,
TLD swapped (.de/.com, .ltd/.1td, .co/.com), the company name on free webmail, and any new domain that
appears in the middle of a thread. Exit code 1 on a suspicious match.

A changed bank account "by email" is the most common trade fraud: never pay or accept new bank details
without a phone or video call to a number you already had. Python 3.9+ standard library only.
"""
import argparse, csv, re, sys

FREE = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com", "aol.com", "icloud.com", "gmx.de", "gmx.net", "web.de",
        "yandex.com", "proton.me", "protonmail.com", "qq.com", "163.com", "126.com", "mail.com", "googlemail.com", "ymail.com", "msn.com",
        "me.com", "zoho.com", "t-online.de", "comcast.net", "optonline.net", "verizon.net", "att.net", "sbcglobal.net", "bellsouth.net",
        "cox.net", "charter.net", "earthlink.net", "orange.fr", "free.fr", "libero.it", "btinternet.com", "sky.com", "bigpond.com", "sina.com"}
GLYPH = [("rn", "m"), ("vv", "w"), ("cl", "d"), ("1", "l"), ("i", "l"), ("0", "o"), ("5", "s"), ("3", "e"), ("ı", "i"), ("а", "a"), ("е", "e"), ("о", "o"), ("р", "p"), ("с", "c")]


def norm(s):
    s = s.lower()
    for a, b in GLYPH:
        s = s.replace(a, b)
    return s.replace("-", "")


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def split(d):
    parts = d.lower().strip(".").split(".")
    if len(parts) >= 3 and parts[-2] in ("co", "com", "org", "net", "ltd"):
        return ".".join(parts[:-2]), ".".join(parts[-2:])
    return ".".join(parts[:-1]), parts[-1]


def judge(known, dom):
    if dom == known:
        return None
    if dom.endswith("." + known):
        return None  # a real subdomain of the trusted domain
    kb0 = split(known)[0]
    if re.search(rf"(^|[.-]){re.escape(kb0)}([.-]|$)", dom) and not dom.endswith(known):
        return f"trusted name used inside another domain: {dom} (the real domain is the last part, not {known})"
    kb, kt = split(known)
    db, dt = split(dom)
    if dom in FREE:
        return None
    if norm(db) == norm(kb) and dt == kt:
        return f"look-alike characters: {dom} imitates {known}"
    if db == kb and dt != kt:
        return f"TLD swapped: {dom} vs {known}"
    if norm(db) == norm(kb):
        return f"look-alike name and different TLD: {dom} vs {known}"
    d = lev(db, kb)
    if 0 < d <= 2 and len(kb) >= 5:
        return f"{d} character(s) different: {dom} vs {known}"
    if kb in db and len(db) - len(kb) <= 8:
        return f"name with extra text: {dom} vs {known}"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--known", action="append", default=[], help="a buyer domain you already trust (repeatable)")
    ap.add_argument("--pipeline", help="take trusted domains from the email column of pipeline.csv / leads.csv")
    ap.add_argument("--sender", help="the address that just wrote to you")
    ap.add_argument("--thread", help="text file with a pasted email thread (headers included)")
    ap.add_argument("--company", default="", help="buyer company name, to catch it used on free webmail")
    a = ap.parse_args()
    known = {k.lower().split("@")[-1] for k in a.known}
    if a.pipeline:
        with open(a.pipeline, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                e = (r.get("email") or "").lower()
                if "@" in e and e.split("@")[1] not in FREE:
                    known.add(e.split("@")[1])
    addrs = []
    if a.sender:
        addrs.append(a.sender.lower())
    if a.thread:
        addrs += [m.lower() for m in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", open(a.thread, encoding="utf-8").read())]
    if not addrs:
        sys.exit("Give --sender or --thread.")
    if not known:
        sys.exit("Give --known or --pipeline so there is a trusted domain to compare with.")
    known -= FREE
    bad = 0
    seen = []
    for e in addrs:
        dom = e.split("@")[1]
        if dom in seen:
            continue
        seen.append(dom)
        hits = [h for h in (judge(k, dom) for k in known) if h]
        if dom in FREE and a.company and re.sub(r"[^a-z]", "", a.company.lower())[:6] in re.sub(r"[^a-z]", "", e.split("@")[0]):
            hits.append(f"company name on free webmail: {e}")
        if hits:
            bad += 1
            for h in hits:
                print(f"✗ {e}: {h}")
        elif dom in FREE:
            print(f"⚠ {e}: free/ISP mailbox. Anyone can open one in any name, so it can never be a trusted payment sender")
        elif dom in known:
            print(f"✓ {e}: matches a trusted domain. A hacked real mailbox looks identical: a bank change is still a STOP until confirmed by phone")
        else:
            print(f"⚠ {e}: new domain, not in your trusted list. Confirm by phone before acting on payment or bank details")
    if a.thread and len(seen) > 1:
        print(f"⚠ thread uses {len(seen)} domains: {', '.join(seen)}. Hackers often reply from a look-alike in the middle of a thread.")
    if bad:
        print("STOP: do not change bank details, ship, or release documents. Call the buyer on a number you already had.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
