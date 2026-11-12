#!/usr/bin/env python3
"""Estimate the buyer's landed cost per unit, so you talk about their real cost, not only your FOB price.

Usage:
  python3 scripts/landed_cost.py --fob 4.20 --qty 5000 --freight 3200 [--insurance-pct 0.3]
         --duty MFN=4.6+0.8c --duty S232=25 --duty S301=7.5 [--dest US] [--other 450] [--entry-value 48000]

--duty NAME=percent, optionally +Nc (US cents per unit) or +$N (dollars per unit) for compound rates
such as "0.8¢ each + 4.6%" → MFN=4.6+0.8c. Several items on one entry: run once per item with
--entry-value <total entry value> so the MPF min/max is applied to the whole entry and split pro rata.

All duty rates are YOUR input (percent of customs value). Nothing is hard-coded because tariffs change
every few months: look up the HTS line at https://hts.usitc.gov/ (US) or the destination's tariff database and
note the date you checked. US: adds MPF (0.3464%, min/max per entry) and HMF (0.125%) on ocean entries.
US customs value is FOB-based (freight is excluded); EU/UK/most others use CIF value.

Use it to (1) show a US buyer the same landed cost from you vs another origin, (2) decide between FOB/DAP/DDP,
(3) write the "tariff changed on your HTS line" email. It does not replace a customs broker. Python 3.9+ stdlib only.
"""
import argparse, re

MPF_RATE, MPF_MIN, MPF_MAX = 0.003464, 34.58, 670.86  # US FY2027 (from 2026-10-01, 91 FR 48398); CBP adjusts min/max every October
HMF_RATE = 0.00125


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fob", type=float, required=True, help="your FOB price per unit")
    ap.add_argument("--qty", type=int, required=True)
    ap.add_argument("--freight", type=float, default=0, help="total ocean/air freight for the shipment")
    ap.add_argument("--insurance-pct", type=float, default=0.3, help="cargo insurance as %% of CIF (default 0.3)")
    ap.add_argument("--duty", action="append", default=[], help="NAME=percent, repeatable, e.g. MFN=3 S301=25")
    ap.add_argument("--dest", default="US")
    ap.add_argument("--other", type=float, default=0, help="other buyer costs: broker, drayage, port fees (total)")
    ap.add_argument("--air", action="store_true", help="air shipment (no US HMF)")
    ap.add_argument("--entry-value", type=float, default=0, help="total customs value of the whole entry when it has several items (US MPF)")
    a = ap.parse_args()
    goods = a.fob * a.qty
    ins = (goods + a.freight) * a.insurance_pct / 100
    us = a.dest.upper() == "US"
    base = goods if us else goods + a.freight + ins
    lines, total_duty = [], 0.0
    for d in a.duty:
        name, _, spec = d.partition("=")
        m = re.fullmatch(r"\s*([\d.]+)\s*%?\s*(?:\+\s*(\$)?([\d.]+)\s*(c|¢)?)?\s*", spec)
        if not m:
            raise SystemExit(f"Bad --duty '{d}': use NAME=percent, e.g. MFN=4.6+0.8c or S232=25")
        r = float(m.group(1))
        per_unit = 0.0
        if m.group(3):
            per_unit = float(m.group(3)) / 100 if m.group(4) else float(m.group(3))
        amt = base * r / 100 + per_unit * a.qty
        total_duty += amt
        lines.append((name + (f" ({r:g}% + {per_unit:g}/unit)" if per_unit else ""), r, amt))
    fees = 0.0
    if us:
        ev = a.entry_value or goods
        mpf = min(max(ev * MPF_RATE, MPF_MIN), MPF_MAX) * goods / ev
        hmf = 0 if a.air else goods * HMF_RATE
        fees = mpf + hmf
    landed = goods + a.freight + ins + total_duty + fees + a.other
    print(f"Goods FOB {goods:,.2f} · freight {a.freight:,.2f} · insurance {ins:,.2f}")
    print(f"Duty base ({'FOB value, US' if us else 'CIF value'}): {base:,.2f}")
    for n, r, amt in lines:
        print(f"  {n}: {r:g}% = {amt:,.2f}")
    print(f"  total duty {total_duty:,.2f} ({100*total_duty/base if base else 0:.1f}% of duty base)")
    if us:
        print(f"  MPF + HMF {fees:,.2f}")
    if a.other:
        print(f"  other costs {a.other:,.2f}")
    print(f"Landed cost {landed:,.2f} = {landed/a.qty:,.4f} per unit (FOB {a.fob:,.4f}; uplift x{landed/goods:.2f})")
    if not a.duty:
        print("⚠ No duty given: look up the HTS line and pass --duty NAME=percent for each layer.")
    print("Note the date you checked the rates; tariffs on China change often (see references/tariff-landscape.md).")


if __name__ == "__main__":
    main()
