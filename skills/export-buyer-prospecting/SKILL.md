---
name: export-buyer-prospecting
description: End-to-end overseas B2B customer development for exporters and manufacturers. Picks target markets, finds importers, distributors and wholesalers with local-language searches, scores leads and drops forwarders and dead leads, finds the decision-maker and their email pattern, checks email deliverability (SPF, DKIM, DMARC, warm-up), writes and lints cold emails plus LinkedIn and WhatsApp messages, handles replies and silent buyers after a quote, and tracks follow-ups. Use when the user wants to 开发客户, 找客户, 找海外买家, 写开发信, 开发信没回复, 开发信进垃圾箱, 找决策人邮箱, 报价后客户不回, 领英开发, WhatsApp 开发, or to find, qualify and contact foreign buyers.
license: MIT. See LICENSE.txt
compatibility: Works with any Agent Skills compatible agent. Scripts need Python 3.9+ standard library only. Web search and internet access improve results but are optional.
metadata:
  author: Vic (voidgazer009)
  version: "2.0.0"
  collection: vic-foreign-trade-skills
---

# Export Buyer Prospecting

Turn "I make X, find me buyers in Y" into a ranked list of real importers, the right person at each, messages that land in the inbox and get replies, and a follow-up system that never forgets a lead. Reply to the user in the language they write in.

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
Fix every ✗ before any cold email goes out. If the domain or mailbox is new, give the user the warm-up table from `references/deliverability.md`. Most "no replies" are spam-folder problems, not copy problems.

### 7. Write and lint the outreach
Before writing, ask the user for what only they know, in one message: one proof point (certification, MOQ, a reference customer or market), and the sender's name, title, company and postal address for the signature. Never invent certifications, MOQs, customers or addresses; leave a clear `{placeholder}` until the user confirms.

Language: if the buyer's website has no English version, write in their language; otherwise English with a local greeting is fine.

- Email: `assets/email-sequence-template.md` (4 touches, day 0/3/7/14), rules in `references/outreach-playbook.md`.
- LinkedIn and WhatsApp: `assets/linkedin-whatsapp-templates.md`. Pick the channel per country from `references/channels-and-culture.md`.
```bash
python3 scripts/lint_outreach.py email1.txt --lead-country DE --company "Example Trading"   # --touch 2..4 for follow-ups
python3 scripts/lint_outreach.py note.txt --channel linkedin
```
Fix every ✗ and re-run until PASS. Show the user the ⚠ claims list so they confirm each claim is true. Check `references/compliance.md` before sending to the EU, UK, Canada, Australia or the US.

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

Deliver with `assets/report-template.md`: ICP in 3 lines, the scored list (tier A first), the sender-domain status, the sequence for the top lead, and today's actions.

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
> Li Wei, Sales Manager, Shinetime Housewares, No. 88 Xingning Rd, Ningbo 315000, China
> Reply "no thanks" and I won't write again.

## Gotchas

- **Customs-data consignees are often forwarders or 3PLs**, not buyers. Names containing Logistik, Logistics, Freight, Shipping, Spedition, Cargo, Forwarding, Transitaire, Aduanas are tier X. Look for the notify party or the real importer instead.
- **Generic inboxes** (info@, sales@, office@) convert poorly. Keep them only when no named buyer is findable; the scorer penalises them.
- **Germany requires prior consent for email marketing, even B2B** (UWG §7). For DE/AT, prefer LinkedIn or phone for the first touch, or send a strictly individual, relevant inquiry; tell the user this risk plainly.
- **First email: no attachments, no more than one link, plain text, under 120 words.** Catalog PDFs on first touch land in spam and get no reply.
- **Never claim certifications, factory size, or clients the user did not state.** Ask instead.
- **Send in the buyer's local morning**, Tuesday to Thursday. Convert time zones; do not use the user's clock.
- **Most "no reply" problems are deliverability.** Check the sender domain (step 6) before rewriting copy, and never cold-email from QQ, 163 or Gmail.
- **Keep cold email off the main company domain.** A spam reputation hit there puts quotes, PIs and payment mails to existing customers in spam too.
- **Hard bounces above 2% damage the domain.** Never send bulk to guessed addresses.
- **WhatsApp only after the buyer gave the number or wrote first.** Unsolicited messages get the number blocked and reported.
- **Fake-buyer signals:** free webmail with a big urgent order, requests for free samples plus courier to a third country, pressure to pay "registration" or "certificate" fees, changed bank or ship-to details. Pause and verify before spending money.
- **Check sanctions lists** (OFAC SDN, EU, UN) before engaging buyers in high-risk countries; the scorer flags these countries but cannot screen names.
- Avoid "We are a professional manufacturer with 20 years of experience" and "Dear Sir/Madam": they are the most common spam openers in this industry.

## Edge cases

- **No web search or no internet:** deliver the ICP, `queries.md`, the empty template, and the sequence with placeholders; `check_domain.py` prints manual check steps when DNS is unreachable.
- **User gives a list already:** skip to step 4.
- **Fewer than 5 tier-A leads:** widen buyer types or neighbouring countries (DE → AT, CH, NL) and say so.
- **User sells via Alibaba/Made-in-China only:** apply steps 4, 7 and 8 to RFQ buyers; RFQ replies have the same rules, and speed wins.
- **Industrial or technical product:** use `--industrial` in step 5 and write separately to the technical and purchasing contacts.
- **User asks for freight costs, quotations, contracts or payment terms:** outside this skill; answer briefly or use a dedicated skill.
