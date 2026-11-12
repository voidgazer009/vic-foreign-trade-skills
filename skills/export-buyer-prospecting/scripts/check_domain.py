#!/usr/bin/env python3
"""Check a sending domain's email authentication, or whether lead email domains can receive mail.

Usage:
  python3 scripts/check_domain.py sender yourcompany.com      # or sales@yourcompany.com; SPF, DKIM, DMARC, MX
  python3 scripts/check_domain.py leads scored.csv            # MX check for every lead email domain

Uses DNS-over-HTTPS (dns.google, fallback cloudflare-dns.com) via the standard library.
If the network is blocked, it says so and prints the manual checks instead.
"""
import argparse, csv, json, re, sys, urllib.parse, urllib.request

RESOLVERS = ["https://dns.google/resolve?", "https://cloudflare-dns.com/dns-query?"]
DKIM_SELECTORS = ["google", "selector1", "selector2", "default", "dkim", "mail", "k1", "s1", "s2", "smtp", "mxvault", "zoho", "qq", "ali", "aliyun", "tencent", "netease"]
FREE_MAIL = ("gmail.", "yahoo.", "hotmail.", "outlook.", "qq.com", "163.com", "126.com", "aol.", "icloud.")


class NetError(Exception):
    pass


def dns_status(name):
    """0 = exists, 3 = NXDOMAIN, 2 = SERVFAIL."""
    for base in RESOLVERS:
        url = base + urllib.parse.urlencode({"name": name, "type": "NS"})
        req = urllib.request.Request(url, headers={"accept": "application/dns-json", "user-agent": "vic-skills"})
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                return json.loads(r.read().decode()).get("Status", 0)
        except Exception:
            continue
    raise NetError("no resolver reachable")


def dns(name, rtype):
    last = None
    for base in RESOLVERS:
        url = base + urllib.parse.urlencode({"name": name, "type": rtype})
        req = urllib.request.Request(url, headers={"accept": "application/dns-json", "user-agent": "vic-skills"})
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
            return [a.get("data", "").strip('"').replace('" "', "") for a in data.get("Answer", []) if a.get("type") in (1, 5, 15, 16, 28)]
        except Exception as e:  # try next resolver
            last = e
    raise NetError(str(last))


def spf_lookups(record):
    return len(re.findall(r"\b(include:|a\b|a:|mx\b|mx:|ptr|exists:|redirect=)", record))


def check_sender(domain, selector=None):
    domain = domain.lower().strip()
    local = ""
    if "@" in domain:
        local, domain = domain.rsplit("@", 1)
    domain = re.sub(r"^(https?://)?(www\.)?", "", domain).split("/")[0]
    ok_all, rows = True, []
    st = dns_status(domain)
    if st == 3:
        print(f"✗ {domain} does not exist in public DNS (NXDOMAIN). Check the spelling, or whether the domain registration lapsed. Nothing can be delivered from or to it.")
        return 1
    if st == 2:
        print(f"✗ DNS for {domain} is broken (SERVFAIL). Ask whoever manages the domain's DNS; check at https://mxtoolbox.com/SuperTool.aspx")
        return 1
    if local in ("sales", "info", "export", "office", "admin", "contact", "service", "marketing", "trade"):
        print(f"⚠ {local}@ is a role address. Cold email from a named person (anna.li@…) gets more replies and looks less like a campaign.")
    if domain.startswith(FREE_MAIL):
        print(f"✗ {domain} is a free mailbox provider. Cold email must go from your own company domain, ideally a separate outreach domain (e.g. getyourbrand.com).")
        return 1
    txt = dns(domain, "TXT")
    spf = [t for t in txt if t.lower().startswith("v=spf1")]
    if len(spf) == 1:
        n = spf_lookups(spf[0])
        rows.append((n <= 10, f"SPF found ({n} top-level lookups; total incl. nested must stay ≤ 10): {spf[0][:120]}"))
        rows.append((not spf[0].rstrip().endswith("+all"), "SPF does not end in +all"))
    elif len(spf) > 1:
        rows.append((False, f"{len(spf)} SPF records: must be exactly one, merge them"))
    else:
        rows.append((False, "No SPF record: add one TXT record listing your mail provider (e.g. v=spf1 include:_spf.google.com ~all)"))
    dm = [t for t in dns("_dmarc." + domain, "TXT") if t.lower().startswith("v=dmarc1")]
    if dm:
        pol = re.search(r"p=(\w+)", dm[0])
        rows.append((True, f"DMARC found, policy {pol.group(1) if pol else '?'}: {dm[0][:100]}"))
        if pol and pol.group(1).lower() == "none":
            print("⚠ DMARC p=none is fine to start; move to p=quarantine once reports show all your senders pass.")
    else:
        rows.append((False, "No DMARC: add TXT _dmarc." + domain + " = v=DMARC1; p=none; rua=mailto:dmarc@" + domain))
    sels = [selector] if selector else DKIM_SELECTORS
    found = [s for s in sels if any("p=" in t for t in dns(f"{s}._domainkey.{domain}", "TXT"))]
    if found:
        rows.append((True, f"DKIM found on selector(s): {', '.join(found)}"))
    elif selector:
        rows.append((False, f"DKIM key not found at {selector}._domainkey.{domain}: enable DKIM signing in your mail provider"))
    else:
        print("⚠ DKIM not found on common selectors. Send yourself a mail and look for 'dkim=pass' in the headers, or rerun with --dkim-selector NAME from your provider.")
    mx = dns(domain, "MX")
    rows.append((bool(mx), "MX records exist (replies can arrive)" if mx else "No MX: replies to this domain will bounce"))
    for ok, msg in rows:
        print(("✓ " if ok else "✗ ") + msg)
        ok_all &= ok
    print(f"→ Blacklists: check {domain} and your sending IP at https://mxtoolbox.com/blacklists.aspx (public DNS cannot query Spamhaus reliably).")
    print("→ If this domain also carries quotes, PIs and payment mails to existing customers, send cold email from a separate outreach domain.")
    print("PASS: authentication basics in place. Still warm up a new domain (see references/deliverability.md)." if ok_all else "FIX the ✗ items before sending any cold email.")
    return 0 if ok_all else 1


def check_leads(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows or "email" not in rows[0]:
        sys.exit("CSV needs an 'email' column.")
    cache, bad = {}, 0
    for r in rows:
        e = (r.get("email") or "").strip().lower()
        if "@" not in e:
            continue
        d = e.split("@", 1)[1]
        if d not in cache:
            cache[d] = dns_status(d) != 3 and (bool(dns(d, "MX")) or bool(dns(d, "A")))
        if not cache[d]:
            bad += 1
            print(f"✗ {r.get('company','?')}: {e} — domain {d} has no mail server, remove it")
    print(f"Checked {len(cache)} domains: {bad} lead email(s) undeliverable. Domains passing MX can still have dead mailboxes; keep hard bounces under 2%.")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["sender", "leads"])
    ap.add_argument("target", help="domain (sender) or CSV path (leads)")
    ap.add_argument("--dkim-selector", help="your provider's DKIM selector, if known")
    a = ap.parse_args()
    try:
        sys.exit(check_sender(a.target, a.dkim_selector) if a.mode == "sender" else check_leads(a.target))
    except NetError as e:
        print(f"Cannot reach DNS-over-HTTPS ({e}). Check manually at https://mxtoolbox.com/SuperTool.aspx : SPF, DMARC, DKIM, MX, blacklist.")
        sys.exit(2)
    except FileNotFoundError as e:
        sys.exit(f"File not found: {e.filename}")


if __name__ == "__main__":
    main()
