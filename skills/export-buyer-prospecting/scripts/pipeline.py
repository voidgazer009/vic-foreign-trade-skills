#!/usr/bin/env python3
"""A tiny follow-up tracker (CSV) so no lead is forgotten and no buyer is chased too often.

Usage:
  python3 scripts/pipeline.py add scored.csv [--tiers A,B] [--file pipeline.csv]
  python3 scripts/pipeline.py log "Example Trading GmbH" sent|replied|positive|quoted|sample|won|lost|bounced|unsubscribed|nurture [--note "..."] [--channel email|linkedin|whatsapp|phone]
  python3 scripts/pipeline.py --my-tz Asia/Shanghai today [--date 2026-11-20]
  python3 scripts/pipeline.py stats

Cadence built in: cold touches on day 0/3/7/14 (moved to Tue–Thu) then nurture every 90 days; after a reply,
answer within 4 working hours, then follow up on day 3/8/15; after a quote day 2/7/14/21 then nurture every 60 days.
Leads without a contact start with "find the decision-maker"; DE/AT/CH start on LinkedIn. Bounced and unsubscribed leads are never
scheduled again. 'today' shows each buyer's local send window. Python 3.9+ standard library only.
"""
import argparse, csv, json, sys
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None

ASSETS = Path(__file__).resolve().parent.parent / "assets"
COLS = ["company", "country", "contact_name", "email", "channel", "stage", "touch", "last_date", "next_date", "next_action", "notes", "history"]
COLD = {1: (3, "Touch 2: add one useful fact (template Email 2)"), 2: (4, "Touch 3: proof, or switch channel to LinkedIn"),
        3: (7, "Touch 4: polite close"), 4: (90, "Nurture: new reason to talk (new product, season, trade show)")}
QUOTE = {1: (2, "Confirm the quote matches their needs (no reply needed if correct)"), 2: (5, "Add value: option, bundle, or lead-time info"),
         3: (7, "Third-party proof from a similar buyer"), 4: (7, "Ask directly what is blocking the decision"), 5: (60, "Nurture: next sourcing cycle")}
REPLY = {1: (3, "Ask whether the selection fits; ask annual volume and target price"),
         2: (5, "Add one new fact (lead time, certificate, similar customer); offer a short call"),
         3: (7, "Ask directly: quote now, samples first, or later in the year?"), 4: (45, "Nurture: next sourcing cycle")}
CLOSED = {"won", "lost", "bounced", "unsubscribed"}
WARM = {"replied", "qualified", "engaged"}
LINKEDIN_FIRST = {"DE", "AT", "CH"}


def next_workday(d, tue_thu=False):
    """Roll a follow-up off the weekend (and to Tue–Thu for cold touches, the best reply days)."""
    ok = {1, 2, 3} if tue_thu else {0, 1, 2, 3, 4}
    while d.weekday() not in ok:
        d += timedelta(days=1)
    return d


def load(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def tzmap():
    try:
        return {k: v.get("tz") for k, v in json.loads((ASSETS / "keywords-multilingual.json").read_text(encoding="utf-8"))["countries"].items()}
    except Exception:
        return {}


def find(rows, company):
    m = [r for r in rows if r["company"].lower() == company.lower()] or [r for r in rows if company.lower() in r["company"].lower()]
    if not m:
        sys.exit(f"No lead named '{company}'. Run 'today' or open the CSV to see names.")
    if len(m) > 1:
        sys.exit("Several matches: " + "; ".join(r["company"] for r in m) + ". Use the full name.")
    return m[0]


def schedule(r, today, days, action, tue_thu=False):
    d = today + timedelta(days=days)
    r["next_date"] = (next_workday(d, tue_thu) if days else d).isoformat()
    r["next_action"] = action


def cmd_add(a, today):
    rows = load(a.file)
    have = {r["company"].lower() for r in rows}
    tiers = set(a.tiers.upper().split(","))
    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        src = list(csv.DictReader(f))
    n = 0
    for s in src:
        if s.get("tier", "A").upper() not in tiers or s["company"].lower() in have:
            continue
        cc = s.get("country", "").upper()
        email, name = s.get("email", ""), s.get("contact_name", "")
        if not email and not name:
            action, ch = "Find the decision-maker first (find_contacts.py roles)", "email"
        elif cc in LINKEDIN_FIRST:
            action, ch = "Touch 1: LinkedIn connection note (consent rules make cold email risky here)", "linkedin"
        elif not email:
            action, ch = "Touch 1: LinkedIn note, or find and verify the email (find_contacts.py email)", "linkedin"
        else:
            action, ch = "Touch 1: send the personalised first email", "email"
        rows.append({"company": s["company"], "country": cc, "contact_name": name,
                     "email": email, "channel": ch, "stage": "new", "touch": "0", "last_date": "",
                     "next_date": today.isoformat(), "next_action": action, "notes": s.get("notes", ""), "history": ""})
        n += 1
    save(a.file, rows)
    print(f"Added {n} leads to {a.file} (tiers {','.join(sorted(tiers))}). Run 'today' for the to-do list.")


def cmd_log(a, today):
    rows = load(a.file)
    r = find(rows, a.company)
    ev = a.event
    r["history"] = (r.get("history", "") + f" | {today} {ev}" + (f" ({a.note})" if a.note else "")).strip(" |")
    r["last_date"] = today.isoformat()
    if a.channel:
        r["channel"] = a.channel
    t = int(r.get("touch") or 0)
    if ev == "sent":
        if r["stage"] in WARM:
            seq, cold = REPLY, False
            r["stage"] = "engaged"
        else:
            seq, cold = (QUOTE, False) if r["stage"] == "quoted" else (COLD, True)
        t += 1; r["touch"] = str(t)
        if r["stage"] in ("new", ""):
            r["stage"] = "contacted"
        days, act = seq.get(t, seq[max(seq)])
        if t >= max(seq):
            r["stage"] = "nurture"
        schedule(r, today, days, act, tue_thu=cold)
    elif ev in ("replied", "positive"):
        r["stage"] = "replied" if ev == "replied" else "qualified"
        r["touch"] = "0"
        schedule(r, today, 0, "Answer within 4 working hours (assets/reply-playbook.md), then log 'sent'")
    elif ev == "quoted":
        r["stage"], r["touch"] = "quoted", "1"
        schedule(r, today, QUOTE[1][0], QUOTE[1][1])
    elif ev == "sample":
        r["stage"] = "sample"
        schedule(r, today, 7, "Check the sample arrived; ask for test feedback and timeline")
    elif ev == "nurture":
        r["stage"] = "nurture"
        schedule(r, today, 90, COLD[4][1])
    elif ev in CLOSED:
        r["stage"], r["next_date"] = ev, ""
        r["next_action"] = {"won": "Hand over to order follow-up; ask for a referral", "lost": "Ask why (one line) and add to nurture in 6 months",
                            "bounced": "Do not resend: find another contact", "unsubscribed": "DO NOT CONTACT"}[ev]
    save(a.file, rows)
    print(f"{r['company']}: stage {r['stage']}, next {r['next_date'] or '—'} → {r['next_action']}")


def cmd_today(a, today):
    rows = load(a.file)
    if not rows:
        sys.exit(f"{a.file} is empty. Run 'add' first.")
    tz = tzmap()
    mine = ZoneInfo(a.my_tz) if (a.my_tz and ZoneInfo) else None
    due = sorted([r for r in rows if r.get("next_date") and r["next_date"] <= today.isoformat() and r["stage"] not in CLOSED],
                 key=lambda r: (r["stage"] not in ("replied", "qualified"), r["next_date"]))
    print(f"{len(due)} action(s) due on {today}:")
    for r in due:
        win = ""
        z = tz.get(r.get("country", "").upper())
        if z and ZoneInfo and not r["next_action"].startswith("Find"):
            bz = ZoneInfo(z)
            st = datetime(today.year, today.month, today.day, 8, 30, tzinfo=bz)
            en = st + timedelta(hours=2)
            win = f" · send 08:30–10:30 {z}"
            if mine:
                win += f" = {st.astimezone(mine):%H:%M}–{en.astimezone(mine):%H:%M} your time"
            if r["stage"] not in WARM and today.weekday() not in (1, 2, 3):
                win += " (cold mail does best Tue–Thu)"
        late = (today - date.fromisoformat(r["next_date"])).days
        print(f"  [{r['stage']}] {r['company']} ({r.get('country','')}) via {r.get('channel','email')}: {r['next_action']}"
              + (f" · {late} day(s) overdue" if late > 0 else "") + win)
    stale = [r for r in rows if r["stage"] in ("replied", "qualified", "quoted", "sample") and r.get("last_date")
             and (today - date.fromisoformat(r["last_date"])).days > 21]
    if stale:
        print("Warm leads with no activity for 21+ days: " + ", ".join(r["company"] for r in stale))


def cmd_stats(a, today):
    rows = load(a.file)
    if not rows:
        sys.exit(f"{a.file} is empty.")
    def hist(r, ev):
        return f" {ev}" in r.get("history", "")
    contacted = [r for r in rows if int(r.get("touch") or 0) > 0 or r["stage"] not in ("new",)]
    n = len(contacted) or 1
    replied = sum(1 for r in contacted if hist(r, "replied") or hist(r, "positive"))
    positive = sum(1 for r in contacted if hist(r, "positive") or r["stage"] in ("qualified", "quoted", "sample", "won"))
    bounced = sum(1 for r in contacted if r["stage"] == "bounced")
    won = sum(1 for r in rows if r["stage"] == "won")
    print(f"Contacted {len(contacted)} · replies {replied} ({100*replied/n:.1f}%) · positive {positive} ({100*positive/n:.1f}%) · bounces {bounced} ({100*bounced/n:.1f}%) · won {won}")
    if len(contacted) < 30:
        print("Fewer than 30 contacted: too early to judge; keep going.")
        return
    if bounced / n > 0.02:
        print("Diagnosis: bounce rate above 2% is hurting your domain. Verify emails before sending (check_domain.py leads).")
    elif replied / n < 0.01:
        print("Diagnosis: under 1% replies usually means mail lands in spam. Run check_domain.py sender and slow down (references/deliverability.md).")
    elif replied / n < 0.03:
        print("Diagnosis: delivered but not compelling. Sharpen targeting (tier A only) and the personal first line (references/outreach-playbook.md).")
    elif positive / max(replied, 1) < 0.2:
        print("Diagnosis: replies but few positive: wrong buyer type or wrong person. Re-check ICP and decision-makers.")
    else:
        print("Healthy: above typical 1–3% B2B cold benchmarks. Scale volume slowly.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default="pipeline.csv")
    ap.add_argument("--date", help="override today (YYYY-MM-DD)")
    ap.add_argument("--my-tz", help="your IANA time zone, e.g. Asia/Shanghai, to show send windows on your clock")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add"); p.add_argument("csv"); p.add_argument("--tiers", default="A,B")
    p = sub.add_parser("log"); p.add_argument("company")
    p.add_argument("event", choices=["sent", "replied", "positive", "quoted", "sample", "won", "lost", "bounced", "unsubscribed", "nurture"])
    p.add_argument("--note"); p.add_argument("--channel", choices=["email", "linkedin", "whatsapp", "phone"])
    sub.add_parser("today"); sub.add_parser("stats")
    a = ap.parse_args()
    if a.date:
        today = date.fromisoformat(a.date)
    elif a.my_tz and ZoneInfo:
        today = datetime.now(ZoneInfo(a.my_tz)).date()
    else:
        today = date.today()
    try:
        {"add": cmd_add, "log": cmd_log, "today": cmd_today, "stats": cmd_stats}[a.cmd](a, today)
    except FileNotFoundError as e:
        sys.exit(f"File not found: {e.filename}")


if __name__ == "__main__":
    main()
