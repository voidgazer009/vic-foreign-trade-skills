#!/usr/bin/env python3
"""Decide a sample policy for one buyer request, and print the sentence to send.

Usage:
  python3 scripts/sample_policy.py --custom catalog|modified|new-tooling --buyer importer|distributor|wholesaler|brand|retailer|ecommerce|trader|unknown
         --annual-usd 50000 --sample-cost-usd 40 [--courier-account yes|no] [--verified yes|no] [--country US]

Policies, from most to least generous:
  FREE                     sample free, buyer pays courier (or gives their DHL/FedEx/UPS account)
  FEE-CREDITED             buyer pays the sample cost, credited against the first order
  FEE-PLUS-FREIGHT         buyer pays cost and courier, credited against the first order
  PREPAY-TOOLING           new tooling: buyer pays tooling/proto in advance, refundable or credited above a stated order quantity

Rule of thumb from practitioners: free samples with free shipping attract the most low-intent requests;
a cost fee credited to the first order filters them while serious buyers accept it. Thresholds are defaults:
override them with --free-threshold. Python 3.9+ standard library only.
"""
import argparse

HIGH_RISK = {"NG", "GH", "CI", "CM", "BJ", "IR", "KP", "SY", "CU", "RU", "BY", "VE", "MM", "AF", "SD", "YE", "LY"}
STRONG = {"importer", "distributor", "wholesaler", "brand", "retailer"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--custom", choices=["catalog", "modified", "new-tooling"], required=True)
    ap.add_argument("--buyer", default="unknown", choices=["importer", "distributor", "wholesaler", "brand", "retailer", "ecommerce", "trader", "unknown"])
    ap.add_argument("--annual-usd", type=float, default=0, help="estimated yearly order value from this buyer (0 = unknown)")
    ap.add_argument("--sample-cost-usd", type=float, default=0, help="your cost to make the sample(s)")
    ap.add_argument("--courier-account", choices=["yes", "no"], default="no")
    ap.add_argument("--verified", choices=["yes", "no"], default="no", help="company checked with verify_buyer.py")
    ap.add_argument("--country", default="", help="ISO code of the destination")
    ap.add_argument("--free-threshold", type=float, default=30000, help="min annual USD for a free catalog sample (default 30000)")
    a = ap.parse_args()

    why = []
    if a.custom == "new-tooling":
        pol = "PREPAY-TOOLING"
        why.append("new tooling or a new prototype is real cost; never free")
    elif a.custom == "catalog" and a.buyer in STRONG and a.verified == "yes" and a.annual_usd >= a.free_threshold:
        pol = "FREE"
        why.append(f"verified {a.buyer} with ≥ USD {a.free_threshold:,.0f}/year potential and a stock item")
    elif a.buyer in STRONG and a.verified == "yes":
        pol = "FEE-CREDITED"
        why.append("serious buyer type, but value unknown or item modified: a credited fee keeps goodwill and filters")
    else:
        pol = "FEE-PLUS-FREIGHT"
        why.append("unverified or low-fit buyer: charge cost and courier, credit both on the first order")
    if a.buyer in ("trader", "unknown"):
        why.append("traders and unknown senders collect samples from many suppliers; verify first")
    fee = max(a.sample_cost_usd, 0)
    if pol == "FREE" and a.courier_account == "no":
        why.append("ask for their courier account number, or charge the courier fee")
    print(f"Policy: {pol}")
    for w in why:
        print(f"  - {w}")
    if fee and pol != "FREE":
        print(f"  Fee to quote: USD {fee:,.0f} sample cost + courier at cost")
    elif fee:
        print(f"  Your cost: USD {fee:,.0f} (not charged)")
    if a.country.upper() in HIGH_RISK:
        print(f"  ⚠ {a.country.upper()}: high fraud or sanctions risk. Verify the company and screen names (OFAC, EU, UN) before sending anything; never pay any fee to the buyer.")
    if a.country.upper() == "US":
        print("  ⚠ US: the de minimis exemption is suspended (since 2025-08-29), so courier samples pay duty and need an entry. "
              "Agree who pays (DDP/DAP) before sending. See references/tariff-landscape.md.")
    print("  Declare the real value on the courier invoice; zero-value declarations get held at customs.")
    print("  Send assets/sample-confirmation-sheet.md with the sample and log it: pipeline.py log \"<company>\" sample")

    lines = {
        "FREE": "Happy to send the sample free of charge. Could you share your DHL/FedEx/UPS account number for the freight?",
        "FEE-CREDITED": "The sample costs USD {fee}, which we credit in full against your first order. Freight by your courier account or at cost.",
        "FEE-PLUS-FREIGHT": "The sample is USD {fee} plus courier at cost; both are credited in full against your first order.",
        "PREPAY-TOOLING": "A new sample needs tooling of USD {fee}, paid in advance and credited against orders above {{qty}} pcs. Lead time {{days}} days after payment.",
    }
    print("\nSentence to send (adapt):")
    print("  " + lines[pol].format(fee=f"{fee:,.0f}" if fee else "{fee}"))


if __name__ == "__main__":
    main()
