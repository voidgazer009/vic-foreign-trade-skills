# Tariffs and import barriers: US, Mexico, Brazil (dated snapshot)

US section below; Mexico and Brazil sections at the end.


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

## Mexico: higher duty on goods from non-FTA countries (China, India, Korea, Taiwan, Thailand…)

**Last verified: 2026-11-13** on the decrees in the Diario Oficial (sidof.segob.gob.mx). Recheck the fracción before every MX quote.
- DOF 29-12-2025 (in force 2026-01-01): IGI raised on 1,463 tariff lines to 5–50% (most 25% or 35%): textiles, apparel, steel, auto parts, plastics, footwear, toys, furniture, glass, cosmetics, household appliances such as microwave ovens (8516.50.01: 30%). https://sidof.segob.gob.mx/notas/5777376
- DOF 23-04-2026 (in force 2026-04-24): 185 more lines at 5–35%, e.g. stainless-steel tableware/kitchenware 7323.93.05 at 35%, LED-only illuminated signs 9405.61.01 at 25%, other lamps 8539.29.99 at 35%. https://sidof.segob.gob.mx/notas/5785818
- DOF 13-10-2026: a further tariff decree. https://sidof.segob.gob.mx/notas/5800977
- No end date in the decrees. Goods that prove origin under an FTA (USMCA, EU, CPTPP…) keep preferential rates, so a Vietnamese or Malaysian competitor may pay less only if Mexico has an FTA with that origin and the buyer can prove it; check before promising a China+1 saving.
- Not every product is listed: LED panel and downlight luminaires (9405.11 / 9405.42) were not in the three decrees on 2026-11-13. Search the buyer's 8-digit fracción in the decrees, or ask the buyer's agente aduanal.
- On top of IGI: DTA 0.8% of customs value (min. MXN 461.61) and IVA 16% on value + IGI + DTA (usually credited back). `landed_cost.py --dest MX` computes both; customs value is CIF.
- Sales angle: the buyer's duty jumped, not your price. Show landed cost, quote FOB/FCA, and offer bigger, less frequent shipments or a design that changes the fracción only when it is truly correct.

## Brazil: who can import, and LED certification

**Last verified: 2026-11-13** on gov.br (Receita Federal, Inmetro).
- The importer needs Siscomex habilitação (RADAR). Modality "Limitada" caps imports at USD 50,000 or USD 150,000 per 6 consecutive months (Receita Federal, Pergunta 07). A buyer on a USD 50,000 cap cannot take a USD 80,000 first order in its own name: ask the modality early (`verify_buyer.py --country BR --order-usd`). https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/habilitacao/Perguntas-e-Respostas/Pergunta-07
- Inmetro-regulated goods need certification and an Inmetro registration before the import licence (LI) is granted; the certificate alone does not authorise import. Portaria Inmetro 231/2026 (DOU 2026-05-05) covers LED lamps and LED luminaires with built-in driver and LED modules; its FAQ says all such products sold in Brazil must comply from 2030-05-05, with earlier steps in art. 15 for manufacture and import. Luminaires sold without a light source (with a lamp socket) are outside it. Who holds the registration (you or the importer) is a commercial question to settle before the quote. https://www.gov.br/inmetro/pt-br/acesso-a-informacao/perguntas-frequentes/avaliacao-da-conformidade/lampadas-e-luminarias-led-portaria-inmetro-no-231-2026-fabricantes-importadores-comerciantes-e-distribuidores
- Brazil's import taxes cascade (II, IPI, PIS/COFINS, ICMS by state); use the buyer's despachante for landed cost instead of a formula.
