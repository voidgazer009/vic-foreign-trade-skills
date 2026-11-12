# Quotation / PI template (fields in the order buyers compare them)

Buyers put every supplier's quote into one comparison sheet. A price without Incoterm, MOQ and lead time is not a quote. Lint before sending: `python3 scripts/lint_quote.py quote.txt --mode sea --dest {country}`.

```
Quotation No. {Q-YYYY-NNN} · Date {YYYY-MM-DD} · Incoterms® 2020
To: {Buyer company}, attn. {Name}

Item 1: {model} · {material, size, finish} · {logo/packaging}
  Unit price: {USD x.xx}/pc {FOB Ningbo | FCA {place} | CIF {port} | DAP {place}}
  MOQ: {n} pcs per design · Carton: {pcs/ctn, ctn size, GW}
  Lead time: {n} days after deposit and artwork approval

Payment: {30}% T/T deposit, {70}% balance before shipment   (or: L/C at sight)
Bank charges: each party pays its own bank's charges
Validity: valid until {YYYY-MM-DD}. Prices based on USD/CNY {rate}; we re-quote if it moves more than 3%.
Duties and import taxes: for the buyer's account under {term}. Tariff changes after this date are for the buyer's account unless DDP.
Our bank details are fixed in this PI and will never change by email. Confirm any change by phone with {name, number}.
{Your name}, {title}, {company}, {address}
```

## Choosing the term
- **Sea:** FOB / CFR / CIF are for sea and inland waterway only. Container to a door → FCA / CPT / CIP.
- **Air, courier, rail:** FCA, CPT, CIP, DAP. Never FOB "by air".
- **EXW from China:** avoid; the buyer cannot clear Chinese export customs. Use FCA your factory.
- **DDP:** the only term where you pay import duty and VAT. You carry every tariff change until delivery. With volatile duties (US), offer DAP and give the buyer a landed-cost estimate (`scripts/landed_cost.py`) instead.
- **CIF:** insurance minimum ICC (C), 110% of value. **CIP:** minimum ICC (A), 110%.
- Don't forget local costs in FOB: THC and document fees (roughly USD 200–500 per shipment; check with your forwarder).

## "30/70" must say when the 70% is due
"Balance before shipment" (you hold the goods) and "balance against copy of B/L" (the goods have sailed) are very different risks. Write the trigger out.
