# US tariffs on Chinese goods: dated snapshot

**Last verified: 2026-11-12. Rates change every few months; recheck before every US quote.** Never hard-code a rate in a quote: give the buyer a landed cost with the date you checked (`scripts/landed_cost.py`).

## The stack: check in this order
1. **Is the HTS line a Section 232 product?** Steel, aluminium and copper articles and their derivatives. Since 2026-06-08 the derivatives in Annex I-B pay **25% on the full value**, from every country (proclamation of 2026-06-01, in force to 2027-12-31). This includes every knife line of 8211, the flatware/utensil lines of 8215 and many steel cookware and appliance lines (e.g. 7321). Look the line up in Annex I-B (https://www.whitehouse.gov/wp-content/uploads/2026/06/Annex-I-B.pdf) or in Chapter 99 of the HTS.
2. **Normal (MFN) duty** from https://hts.usitc.gov/ (often compound in chapter 82, e.g. 0.8¢ each + 4.6%: pass `--duty MFN=4.6+0.8c`).
3. **Section 301 China list duty**: 25% (Lists 1–3) or 7.5% (List 4A). It still applies on top of Section 232.
4. **Section 301 "forced-labor" tariff, 12.5%** (since 2026-07-24): applies to most Chinese goods, **but not to Section 232 goods** (HTS note 52(f), heading 9903.05.90).

Worked examples (rates checked 2026-11-12 on hts.usitc.gov; recheck):
- Ordinary consumer good, List 3: MFN 3% + S301 25% + forced-labor 12.5% = 40.5% → `--duty MFN=3 --duty S301=25 --duty S301-FL=12.5`
- Kitchen knife 8211.92.20 (List 4A): 0.8¢ + 4.6% + S232 25% + S301 7.5% → `--duty MFN=4.6+0.8c --duty S232=25 --duty S301=7.5` (about 37.7% on a USD 1.32 knife)
- Steel turner 8215.99.50: MFN 5.3% + S232 25% → check its 301 list before quoting.

Sales angle for 232 products: Vietnam, India or Mexico pay the same 25% Section 232 duty, so moving these lines out of China saves the buyer only the 301 list duty, not the whole stack. Say so with a landed-cost comparison.

- IEEPA tariffs are no longer collected since 2026-02-24 (Supreme Court, Learning Resources v. Trump, 2026-02-20); refunds run through CBP.
- US–China truce extended to 2027-01-10; 178 Section 301 exclusions extended to 2027-01-09.
- Average US tariff on Chinese goods: about 36.5% (July 2026, Congressional Research Service IF12990).
- De minimis is suspended since 2025-08-29: every courier sample to the US needs an entry and may pay duty.
- US customs value is FOB-based (freight excluded). Fees: MPF 0.3464% (min USD 34.58, max 670.86 per formal entry from 2026-10-01) and HMF 0.125% on ocean cargo.

Sources: Congressional Research Service IF12990 (updated 2026-08-18); Beato Capital "China tariffs 2026" (2026-11-11, citing the Federal Register); Supply Chain Dive (2026-11-09); ICC Incoterms tariff guidance note (April 2025); CBP user fees notice (91 FR 48398).

## How sellers respond without giving the margin away
- Do not cut price by reflex: the duty is the buyer's cost, and a cut pays the tariff for them. First show the landed cost and the options.
- Quote FOB or DAP, not DDP, while duties move (ICC's advice). DDP is the only Incoterm where you pay the duty.
- Add the line: "Tariff changes after the quote date are for the buyer's account unless DDP."
- Offer what lowers their landed cost: a different HTS-correct product design or material, bigger shipments (MPF cap), longer validity in exchange for a deposit.
- Expect "hold Q1 orders" and "quote me a Vietnam price". Answer with a plan (see China+1 in `references/inquiry-to-order.md`).
- A tariff change on the buyer's HTS line is a legitimate reason to write: "Your line 9617.00 went from X to Y on {date}; here is what that does to your landed cost and two ways to keep it flat."

Look-ups: US tariff schedule https://hts.usitc.gov/ · Federal Register https://www.federalregister.gov/ · CBP https://www.cbp.gov/trade.
