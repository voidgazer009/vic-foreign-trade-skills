---
name: export-buyer-prospecting
description: End-to-end overseas B2B customer development for exporters and manufacturers, from finding buyers to a safely paid first order. Picks markets, finds importers and distributors with local-language searches, scores leads, finds decision-makers and email patterns, checks deliverability, writes and lints cold emails, LinkedIn and WhatsApp messages, triages price-only inquiries, decides sample policy, lints quotations and Incoterms, follows up trade-show leads, verifies buyers, guards payment terms and email-hacking scams, estimates landed cost under US and Mexico tariffs, and tracks follow-ups. Use when the user wants to 开发客户, 找客户, 找海外买家, 写开发信, 开发信没回复, 进垃圾箱, 找决策人, 报价后客户不回, 询盘套价, 要免费样品, 报价单, 展会客户跟进, 客户背调, 改付款方式, 邮件被黑改账户, 美国关税, 墨西哥关税, or to find, qualify, contact and convert foreign buyers.
license: MIT. See LICENSE.txt
compatibility: Works with any Agent Skills compatible agent. Scripts need Python 3.9+ standard library only. Web search and internet access improve results but are optional.
metadata:
  author: Vic (voidgazer009)
  version: "3.1.0"
  collection: vic-foreign-trade-skills
---

# Export Buyer Prospecting

Turn "I make X, find me buyers in Y" into a ranked list of real importers, the right person at each, messages that land in the inbox and get replies, and a follow-up system that never forgets a lead. Then carry the replies to a first order without losing margin or money: triage inquiries, sample policy, clean quotes, buyer checks and payment safety. Reply to the user in the language they write in.

## Start here: match the user's problem

| The user says | Start at |
|---|---|
| "Find me buyers / 帮我开发客户" | Step 1, run the full workflow |
| "Which country should I target?" | Step 0 |
| "I have a list already" | Step 4 |
| "I find companies but not the right person / only info@" | Step 5 |
| "No one replies / 开发信没回复" | Step 6 first (deliverability), then Step 7 |
| "My emails go to spam / mailbox got blocked" | Step 6 |
| "LinkedIn or WhatsApp outreach" | Step 7 with `--channel` |
| "They replied" / "silent after my quote" | Step 8 |
| "I lose track of follow-ups" | Step 9 |
| "Is this inquiry real? / 询盘套价 / only asks price" | Step 10 |
| "They want free samples" | Step 11 |
| "Check my quotation / PI / which Incoterm" | Step 12 |
| "I have trade-show cards" | Step 9 `import-show`, then `assets/show-followup-template.md` |
| "Is this buyer real? / they want B/L copy or open account / bank details changed" | Step 13 |
| "US or Mexico tariffs / buyer says too expensive because of duty" | Step 12 with `scripts/landed_cost.py` |
| "Can this Brazil/Mexico buyer import? / Inmetro / NOM" | Step 13, then `references/tariff-landscape.md` |

## Workflow

Copy this checklist and tick it off:

- [ ] 0. Choose markets (only if not given)
- [ ] 1. Define the ICP
- [ ] 2. Generate localized search queries
- [ ] 3. Collect leads into the CSV template
- [ ] 4. Score and filter leads
- [ ] 5. Find the decision-maker and research tier-A leads
- [ ] 6. Check the sender domain
- [ ] 7. Write and lint the outreach
- [ ] 8. Handle replies
- [ ] 9. Track follow-ups and deliver
- [ ] 10–13. Deal stage, when a buyer engages: triage, samples, quote, verify and protect payment

### 0. Choose markets
If the user has no target country, read `references/market-selection.md` and propose 2–3 countries with a short table. Never target a whole continent.

### 1. Define the ICP (ideal customer profile)
Ask at most two questions if the user has not said: **what product (with HS code if known)** and **which target countries**. Default everything else from `assets/icp-template.json` and say what you assumed. Save it as `icp.json` with `target_countries` set to the user's countries (the template's DE/FR/US are only an example).

Buyer types, best first for most manufacturers: importer/distributor > wholesaler > brand owner sourcing OEM > large retailer/chain > e-commerce seller. Small Amazon sellers rarely buy container loads; rank them last unless the user sells small MOQ.

### 2. Generate localized search queries
```bash
python3 scripts/build_queries.py --product "stainless steel water bottle" --countries DE,FR,US --local-product "de=Edelstahl Trinkflasche,fr=gourde inox" --out queries.md
```
Buyers search in their own language; always pass `--local-product` for non-English markets, and `--extra-terms` for the sales channels that matter (e.g. `Werbeartikel,Haushaltswaren` for drinkware in Germany). Keywords, country time zones and forwarder markers live in `assets/keywords-multilingual.json`; add a country there if missing. Run the queries if you have web search; otherwise hand the file to the user. Read `references/lead-sources.md` for channels beyond Google (customs data, trade shows, directories).

### 3. Collect leads
Fill `assets/leads-template.csv`, one company per row. Record only what a page actually shows; leave a cell empty rather than guess. Never invent an email address.

### 4. Score and filter
```bash
python3 scripts/score_leads.py leads.csv --icp icp.json --out scored.csv
```
Scores 0–100, tiers A/B/C/X, and flags what to research. Drop tier **X** (forwarders, marketplaces, duplicates, wrong countries). Weights are explained in `references/qualification-rubric.md`; tune them in `icp.json`, never by editing scores.

### 5. Find the decision-maker and research tier-A leads
For each tier-A lead (10 per pass):
```bash
python3 scripts/find_contacts.py roles --company "Example Trading GmbH" --country DE [--industrial]
python3 scripts/find_contacts.py email --name "Anna Schmidt" --domain example-trading.de --known "j.mueller@example-trading.de=Jan Müller"
```
Find one specific recent fact (new line, trade show, store opening, buyer job post) and put it in `notes`; it becomes the email's first line. Read `references/decision-makers.md` for who decides by company size and how to verify addresses. A guessed address is never sent unverified. The shop domain and the mail domain can differ (kalatex.shop vs kalatex.de): use the domain of any real address you found.

Write what you found (`contact_name`, `contact_title`, `email`, `buyer_type`, `notes`) back into `leads.csv` and re-run step 4, so tiers reflect the research. `find_contacts.py batch scored.csv` fills unverified guesses for many rows at once.

### 6. Check the sender domain
```bash
python3 scripts/check_domain.py sender usercompany.com
python3 scripts/check_domain.py leads scored.csv
```
Fix every ✗ before any cold email goes out. If the domain does not exist (NXDOMAIN), the user needs a separate outreach domain registered and warmed up before step 7 sends anything. If the domain or mailbox is new, give the user the warm-up table from `references/deliverability.md`. Most "no replies" are spam-folder problems, not copy problems.

### 7. Write and lint the outreach
Before writing, ask the user for what only they know, in one message: one proof point (certification, MOQ, a reference customer or market), and the sender's name, title, company and postal address for the signature. Never invent certifications, MOQs, customers or addresses; leave a clear `{placeholder}` until the user confirms.

Language: if the buyer's website has no English version, write in their language; otherwise English with a local greeting is fine.

- Email: `assets/email-sequence-template.md` (4 touches, day 0/3/7/14), rules in `references/outreach-playbook.md`.
- LinkedIn and WhatsApp: `assets/linkedin-whatsapp-templates.md`. Pick the channel per country from `references/channels-and-culture.md`.
```bash
python3 scripts/lint_outreach.py email1.txt --lead-country DE --company "Example Trading"   # --touch 2..4 for follow-ups
python3 scripts/lint_outreach.py note.txt --channel linkedin
```
Fix every ✗ and re-run until PASS. While the signature still has `{placeholders}` waiting for the user, add `--draft` (same for `lint_quote.py`): it ends in DRAFT PASS, and the final check before sending runs without it. Show the user the ⚠ claims list so they confirm each claim is true. Check `references/compliance.md` before sending to the EU, UK, Canada, Australia or the US.

### 8. Handle replies
Classify each reply with `assets/reply-playbook.md` and answer within 4 working hours. If the user does not say which lead replied, ask before logging. For silent buyers after a quote use its day 2/7/14/21 sequence. Never send "Any update?" alone.

### 9. Track follow-ups and deliver
```bash
python3 scripts/pipeline.py add scored.csv
python3 scripts/pipeline.py log "Example Trading GmbH" sent
python3 scripts/pipeline.py --my-tz Asia/Shanghai today
python3 scripts/pipeline.py stats
```
Log `sent` again after answering a reply; replied leads move to a post-reply track (day 3/8/15), not the cold sequence. `today` lists every due action with the send window on both the buyer's and the user's clock (pass the user's own zone); `stats` diagnoses where the funnel breaks (bounces, spam, copy, wrong person) after 30+ contacts.

US, Canada, Australia, Brazil and Mexico span several time zones: fill `state` (US) or `tz` in the leads CSV so send windows are right. When the window falls in the user's night, tell them to use scheduled send. Trade-show cards: `pipeline.py import-show cards.csv --show "Canton Fair 140"` grades them A (due within 48 h), B (3 days), C (quarterly). Other events: `sample` (day 3/7/21 checks), `incumbent` ("we have a supplier", 60-day re-touch, `--note` the trigger to watch), `terms` (buyer asks to change payment terms: flagged red until `verified --note`). Show leads follow their own track (email 2 on day 5, then re-touch before the next fair); follow-ups skip the buyer's weekend (Fri–Sat in most Gulf states). The same event twice on one day is refused unless `--force`. `stats` splits results by lead source.

Deliver with `assets/report-template.md`: ICP in 3 lines, the scored list (tier A first), the sender-domain status, the sequence for the top lead, and today's actions.

## Deal stage (steps 10–13)

### 10. Triage inbound inquiries
```bash
python3 scripts/triage_inquiry.py inquiry.txt --from buyer@domain.com --company "Claimed Co Ltd"
```
VERIFY → the sender's domain imitates the company it names: contact the company through its real website before anything else. QUOTE → step 12. ASK-FIRST → send its 5-field ask-back with a price band only. ARCHIVE → one polite line, no prices. Never send a full price list to an unqualified lead. More in `references/inquiry-to-order.md` (platform RFQs, social DMs, customs data, China+1).

### 11. Samples
```bash
python3 scripts/sample_policy.py --custom catalog --buyer importer --annual-usd 50000 --sample-cost-usd 30 --verified yes --country US
```
Use the sentence it prints, agree the spec with `assets/sample-confirmation-sheet.md`, then log `sample`.

### 12. Quote
Fill `assets/quote-sheet-template.md`, then:
```bash
python3 scripts/lint_quote.py quote.txt --mode sea --dest US
python3 scripts/landed_cost.py --fob 1.32 --qty 3000 --freight 600 --duty MFN=4.6+0.8c --duty S232=25 --duty S301=7.5   # US buyers
python3 scripts/landed_cost.py --fob 6.80 --qty 2000 --freight 2400 --dest MX --duty IGI={rate from the decree}            # Mexico
```
Fix every ✗. Duty rates come from the official tariff database, with the date checked. Read `references/tariff-landscape.md` before any US quote: check Section 232 first (steel, aluminium, copper and derivatives such as knives and kitchen utensils), because 232 goods skip the 12.5% forced-labor tariff. For Mexico, check the buyer's fracción against the 2026 non-FTA decrees (5–50%); for Brazil, check the importer's habilitação cap and Inmetro registration before quoting regulated goods. Say the reference's "last verified" date. On "too expensive", follow the reply playbook: compare specs, trade instead of discount.

### 13. Verify the buyer and protect the payment
```bash
python3 scripts/verify_buyer.py --company "Example Trading GmbH" --country DE --domain example-trading.de --vat DE123456789 --terms bl-copy
python3 scripts/check_lookalike.py --pipeline pipeline.csv --own usercompany.com --thread thread.txt
python3 scripts/pipeline.py log "Example Trading GmbH" verified --note "called known number; terms stay 30/70 before shipment"
```
Run `verify_buyer.py` before free samples, credit terms or a big first order; depth grows with risk (`--terms`; `--order-usd` for Brazil's import caps). Run `check_lookalike.py` with `--own` on every mail that mentions bank details, payment or document release: it stops on look-alikes of the buyer's or the user's domain and on any request to change bank details. Follow `references/payment-and-fraud.md` when the buyer asks to change terms (under FOB, a buyer-nominated forwarder can release the cargo without your original B/L). Log `verified` with what was checked to clear the red flag.

## Example

**User:** 我们是宁波的不锈钢保温杯工厂，有 LFGB 认证，起订 1000 个，想开发德国的客户

**Agent output (abridged):**

> ICP: 德国进口商/分销商/礼品促销品公司，10–500 人，年采购 ≥1 个 40HQ，HS 9617.00。
>
> | Tier | Company | Type | Score | Why |
> |---|---|---|---|---|
> | A | Example Trading GmbH | Importer | 86 | Sells drinkware, 45 staff, buyer named |
> | X | Example Logistik GmbH | Forwarder | 0 | Customs-data consignee is a forwarder |
>
> **Email 1 (Day 0)**
> Subject: Insulated bottles for your autumn catalogue
>
> Hi Ms Schmidt,
>
> Saw Example Trading added a reusable drinkware line at Ambiente this year. We make double-wall 304 stainless bottles in Ningbo for EU importers, LFGB tested, from 1,000 pcs per design.
>
> Would a sample of our two best sellers for the German market be useful?
>
> {Your name}, {Title}, {Company}, {Street address}, Ningbo, China
> Reply "no thanks" and I won't write again.

## Gotchas

- **Customs-data consignees are often forwarders or 3PLs**, not buyers. Names containing Logistik, Logistics, Freight, Shipping, Spedition, Cargo, Forwarding, Transitaire, Aduanas are tier X. Look for the notify party or the real importer instead.
- **Generic inboxes** (info@, sales@, office@) convert poorly. Keep them only when no named buyer is findable; the scorer penalises them.
- **Germany requires prior consent for email marketing, even B2B** (UWG §7). For DE/AT, prefer LinkedIn or phone for the first touch, or send a strictly individual, relevant inquiry; tell the user this risk plainly.
- **First email: no attachments, no more than one link, plain text, under 120 words.** Catalog PDFs on first touch land in spam and get no reply.
- **Never claim certifications, factory size, or clients the user did not state, and never invent the sender's name, company or address.** Ask instead, or leave a `{placeholder}` that `lint_outreach.py` will flag.
- **Send in the buyer's local morning**, Tuesday to Thursday. Convert time zones; do not use the user's clock.
- **Most "no reply" problems are deliverability.** Check the sender domain (step 6) before rewriting copy, and never cold-email from QQ, 163 or Gmail.
- **Keep cold email off the main company domain.** A spam reputation hit there puts quotes, PIs and payment mails to existing customers in spam too.
- **Hard bounces above 2% damage the domain.** Never send bulk to guessed addresses.
- **WhatsApp only after the buyer gave the number or wrote first.** Unsolicited messages get the number blocked and reported.
- **Fake-buyer signals:** free webmail with a big urgent order, free samples plus courier to a third country, "registration" or "certificate" fees, changed ship-to details. Pause and verify before spending money.
- **Check sanctions lists** (OFAC SDN, EU, UN) before engaging buyers in high-risk countries; the scorer flags these countries but cannot screen names.
- **Bank details never change by email, and the first oral request to change payment terms is the warning sign.** Confirm any change by phone on a number you already had; never agree to "ship first, pay against B/L copy" in the chat.
- **"FDA approved" is false for food-contact goods.** FDA does not approve or certify kitchenware; say "tested to FDA 21 CFR food-contact requirements, report available".
- **Tariff numbers expire.** Never quote a US duty rate from memory; use the dated reference and tell the user to recheck it. Prefer FOB or DAP over DDP while duties move.
- **Most "best price" inquiries are honest benchmarking.** Answer fast and politely; protect the price list, not your pride.
- Avoid "We are a professional manufacturer with 20 years of experience" and "Dear Sir/Madam": they are the most common spam openers in this industry.

## Edge cases

- **No web search or no internet:** deliver the ICP, `queries.md`, the empty template, and the sequence with placeholders; `check_domain.py` prints manual check steps when DNS is unreachable.
- **User gives a list already:** skip to step 4.
- **Fewer than 5 tier-A leads:** widen buyer types or neighbouring countries (DE → AT, CH, NL) and say so.
- **User sells via Alibaba/Made-in-China only:** apply steps 4, 7 and 8 to RFQ buyers; RFQ replies have the same rules, and speed wins.
- **Industrial or technical product:** use `--industrial` in step 5 and write separately to the technical and purchasing contacts.
- **User asks for freight rates, contracts or legal advice:** outside this skill; give the checklist from the references and suggest a forwarder, bank or lawyer.
- **Buyer is in a sanctioned or high-risk country, or wants goods shipped to a third country:** stop at step 13 and screen names before anything is sent.
