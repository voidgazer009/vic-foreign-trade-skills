---
name: export-buyer-prospecting
description: Find, qualify, and write first-touch outreach to overseas B2B buyers (importers, distributors, wholesalers, brand owners) for an exporter or manufacturer. Builds localized search queries per target country, scores a lead list against an ideal-customer profile, filters out freight forwarders and dead leads, and drafts a compliant cold email sequence. Use when the user wants to 开发客户, 找客户, 找海外买家, 外贸开发信, find importers/distributors abroad, build a prospect list, qualify leads, or write cold emails to foreign buyers.
license: MIT. See LICENSE.txt
compatibility: Works with any Agent Skills compatible agent. Scripts need Python 3.8+ standard library only. Web search access improves results but is optional.
metadata:
  author: Vic (voidgazer009)
  version: "1.0.0"
  collection: vic-foreign-trade-skills
---

# Export Buyer Prospecting

Turn "I make X, find me buyers in Y" into a ranked list of real importers and a cold email sequence that gets replies. Reply to the user in the language they write in.

## Workflow

Copy this checklist and tick it off:

- [ ] 1. Define the ICP
- [ ] 2. Generate localized search queries
- [ ] 3. Collect leads into the CSV template
- [ ] 4. Score and filter leads
- [ ] 5. Research the top leads
- [ ] 6. Draft and lint the outreach sequence
- [ ] 7. Deliver

### 1. Define the ICP (ideal customer profile)

Ask at most two questions if the user has not said: **what product (with HS code if known)** and **which target countries**. Default everything else from `assets/icp-template.json` and say what you assumed. Save the filled profile as `icp.json`.

Buyer types, best first for most manufacturers: importer/distributor > wholesaler > brand owner sourcing OEM > large retailer/chain > e-commerce seller. Small Amazon sellers rarely buy container loads; rank them last unless the user sells small MOQ.

### 2. Generate localized search queries

```bash
python3 scripts/build_queries.py --product "stainless steel water bottle" --countries DE,FR,US --out queries.md
```

It writes Google operator queries in each country's language (keywords from `assets/keywords-multilingual.json`), plus LinkedIn, trade-show exhibitor, and directory queries. Run the queries if you have web search; otherwise hand the file to the user. Read `references/lead-sources.md` when you need channels beyond Google (customs data, trade shows, marketplaces, associations).

### 3. Collect leads

Fill `assets/leads-template.csv`, one company per row. Columns: `company,website,country,buyer_type,employees,products_match,contact_name,contact_title,email,source,notes`. Record only what a page actually shows; leave a cell empty rather than guess. Never invent an email address.

### 4. Score and filter

```bash
python3 scripts/score_leads.py leads.csv --icp icp.json --out scored.csv
```

Scores 0–100, assigns tier A/B/C/X, and flags problems. Read the summary it prints. Rows tiered **X** are forwarders, marketplaces, duplicates, or wrong countries: drop them. Scoring weights are explained in `references/qualification-rubric.md`; adjust the weights in `icp.json`, never by hand-editing scores.

### 5. Research the top leads

For each tier-A lead (cap at 10 per pass), find on its own website or LinkedIn: what they sell now, one specific recent fact (new line, store opening, trade show, hiring a buyer), and the buyer's name and title. Put the fact in `notes`. This one fact is what makes the email personal; without it, write a tier-B email instead.

### 6. Draft and lint the outreach

Use `assets/email-sequence-template.md` (4 touches over about 14 days). Rules in `references/outreach-playbook.md`. Then lint every email:

```bash
python3 scripts/lint_outreach.py email1.txt --lead-country DE
```

Fix every ✗ and re-run until it passes. Check `references/compliance.md` before sending to the EU, UK, Canada, or the US.

### 7. Deliver

Give the user: the ICP in 3 lines, the scored list (tier A first), and the email sequence for the top lead. Use `assets/report-template.md`.

## Example

**User:** 我们是宁波的不锈钢保温杯工厂，想开发德国的客户

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
> Hi Anna,
>
> Saw Example Trading added a reusable drinkware line at Ambiente this year. We make double-wall 304 stainless bottles in Ningbo for EU importers, LFGB tested, from 1,000 pcs per design.
>
> Would a sample of our two best sellers for the German market be useful?
>
> Li, Sales Manager, [Company], [Address]
> Reply "no thanks" and I won't write again.

## Gotchas

- **Customs-data consignees are often forwarders or 3PLs**, not buyers. Names containing Logistik, Logistics, Freight, Shipping, Spedition, Cargo, Forwarding, Transitaire, Aduanas are tier X. Look for the notify party or the real importer instead.
- **Generic inboxes** (info@, sales@, office@) convert poorly. Keep them only when no named buyer is findable; the scorer penalises them.
- **Germany requires prior consent for email marketing, even B2B** (UWG §7). For DE/AT, prefer LinkedIn or phone for the first touch, or send a strictly individual, relevant inquiry; tell the user this risk plainly.
- **First email: no attachments, no more than one link, plain text, under 120 words.** Catalog PDFs on first touch land in spam and get no reply.
- **Never claim certifications, factory size, or clients the user did not state.** Ask instead.
- **Send in the buyer's local morning**, Tuesday to Thursday. Convert time zones; do not use the user's clock.
- **Check sanctions lists** (OFAC SDN, EU, UN) before engaging buyers in high-risk countries; the scorer flags these countries but cannot screen names.
- Avoid "We are a professional manufacturer with 20 years of experience" and "Dear Sir/Madam": they are the most common spam openers in this industry.

## Edge cases

- **No web search available:** deliver the ICP, `queries.md`, the empty template, and the email sequence with placeholders; tell the user how to fill the CSV.
- **User gives a list already:** skip to step 4.
- **Fewer than 5 tier-A leads:** widen buyer types or neighbouring countries (DE → AT, CH, NL) and say so.
- **User sells via Alibaba/Made-in-China only:** still apply steps 4–6 to RFQ buyers; RFQ replies have the same rules.
