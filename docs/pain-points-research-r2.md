# 外贸开发客户痛点调研 · 第二轮 (Round 2) · 2026-11-12

Purpose: input for **export-buyer-prospecting 3.0**. Round 1 (`docs/pain-points-research.md`) covered 15 pain points; this round looks only for **new pain points or new angles** a SOHO / 小工厂 / 外贸业务员 hits while turning a contact into a paid order.

Method: ~30 web searches, 25 pages fetched and read (listed at the end). Quotes below come from fetched pages unless marked *(search excerpt, not fetched)*. Most practitioner sources are Chinese vendor blogs (图灵搜, 灵贸, 环形山, 小满, 网易外贸通). They are useful for describing pains, but their numbers are self-reported, so they are marked **[uncertain]**.

Frequency/importance scale (my estimate, based on how often the topic appears across forums and vendor blogs, plus the cost of a single failure):
- **Freq**: H = weekly for most sellers, M = monthly or per deal, L = rare.
- **Cost**: H = can lose an order or the payment, M = time or margin, L = annoyance.

Overlap check against 2.0: 2.0 has only one line each on "Send samples", "We have a supplier", "Price? give range with Incoterm" (`assets/reply-playbook.md`, `references/outreach-playbook.md`) and one line on consignee-is-a-forwarder (`references/lead-sources.md`). Everything below goes deeper or is new.

---

## Top 8 ranking for a SOHO / small factory

Ranked by value = frequency × cost per failure × how well a stdlib skill can actually fix it.

| Rank | Pain point | Why it ranks here | Skill deliverable (short) |
|---|---|---|---|
| 1 | R2-02 询盘套价 / price-only RFQ triage | Daily for anyone on Alibaba, Made-in-China or Global Sources. Wastes the most hours and leaks the price list to competitors. | `triage_inquiry.py` + 5-field ask-back template + banded-quote footer |
| 2 | R2-01 样品无底洞 / free-sample black hole | Every new lead asks for samples. Real cash loss, and free samples are a low-intent filter failure. | `sample_policy.py` (quadrant decision + fee) + sample confirmation sheet + D+3/7/21 stages in `pipeline.py` |
| 3 | R2-03 报价单算错写错 / quote-sheet errors | One wrong Incoterm, payment wording or missing validity date can wipe out margin. Fully checkable by a linter. | `lint_quote.py` + `quote-sheet-template.md` |
| 4 | R2-09 展会名片跟进衰减 / trade-show lead decay | Canton Fair runs twice a year. Low cost to fix and a high return per lead. | `show_leads.py` (A/B/C tiers, 24–48h due) + 4-fact first-email template |
| 5 | R2-06 邮件被黑改账户 / BEC & look-alike domains | Rare but catastrophic (whole tail payment). A cheap check prevents it. | `check_lookalike.py` + "bank details never change by email" PI clause + checklist |
| 6 | R2-07 买家背调到注册层 / registry-level buyer verification | Needed before any credit term (OA, D/P, B/L-copy). 2.0 lists red flags but has no lookup tool. | `verify_buyer.py` (registry URLs, VIES REST, RDAP domain age) |
| 7 | R2-08 付款条款中途被改 / payment-term erosion | Buyer moves from "70% before shipment" to "against B/L copy". Often the step right before default. | `payment-terms.md` risk ladder + term-change red-flag checklist + reply template |
| 8 | R2-04 美国关税反复 / US tariff whiplash | Only for US-exposed sellers, but there it decides whether a quote survives. Rates change every few months. | `tariff-landscape.md` (dated) + `landed_cost.py` (user supplies rates) + tariff-change outreach trigger |

Just below the cut: R2-10 "已有供应商" deep play, R2-05 China+1 requests, R2-11 customs-data ROI, R2-12 TikTok B2B leads, R2-13 AI-outreach backlash.

---

## R2-01 样品无底洞 · Free samples that never convert

**Quotes**
- "做外贸这么多年，凡是收费打样的客户基本都成了；免费的，贴钱的，倒是一个没成" (I lost 300 RMB on a free sample; the client then found a cheaper supplier). Source: 福步 SOHO thread by ljch4022, posted 2023-08-16. https://bbs.fobshanghai.com/thread-8998893-1-1.html (old, but the original post is still readable).
- "广交会存在不少专门收集样品的采购商，到处索要免费样品，对比完就失联". Also: "无条件免费寄送样品…的询盘转化率通常不足5%". Source: 大数跨境 / 粤享全球, 2026-10-22. https://www.10100.com/article/154951899 **[uncertain: "行业统计" is uncited]**
- "全免费会把不认真询盘的占比推到四成以上". Experience table: free sample with free shipping gives 12–20% valid projects and 4–8% sample-to-order; cost fee credited to the first order gives 45–60% and 15–25%. Source: 环形山 (hxshan), 2026-09-18. https://hxshan.com/insight/sample-and-prototype-policy-overseas-buyers/ **[uncertain: the author says "数值需按自身数据重算"; vendor blog]**

**Buyer-side view**
- "If I ask for samples I get ghosted but there's no way I'm going to pay for a minimum order without knowing the quality first." Source: r/ecommerce, about 2025-08. https://www.reddit.com/r/ecommerce/comments/1n1haqt/why_is_sourcing_such_a_nightmare/
- In the same thread, another buyer says suppliers ignore buyers "until they're convinced you're serious"; asking for MOQ in the first message is "not a good start".
- Small Western distributors "同时对接5~10家供应商，前期只愿意投入少量资金做试样" (10100, above).
- So buyers do accept paying for samples when the policy is stated early and the fee is creditable to the first order.

**Frequency / importance**: Freq H, Cost M (300–2,000 RMB per custom sample per hxshan, plus hours of staff time).

**Skill proposal**
- `scripts/sample_policy.py` (stdlib). Input: customisation level (catalog / modified / new tooling), estimated annual order value, buyer type (end-user / distributor / trader / unknown), and whether a courier account was given.
- Output: a policy (free / free + freight collect / cost fee credited to first order / full prepay), a suggested fee band, and the exact English sentence to send.
- Encode hxshan's four quadrants as defaults and let the user override the thresholds.
- `assets/sample-confirmation-sheet.md`: bilingual one-page sheet covering material, the 3 critical dimensions and tolerance, finish, packaging, label, acceptance method, timeline, and quantity plus spares. Also the clauses "sample for internal evaluation, not production standard unless signed" and "declared value = real value" (10100 warns that zero-value declarations get held).
- Add stages to `pipeline.py`: `sample_sent → D+3 receipt check → D+7 test result → D+21 proposal or archive`.

---

## R2-02 询盘套价与"只要报价"RFQ · Price fishing and price-only RFQs

**Quotes**
- "你回一份详实的报价单，两天后他不回了；你不回，隔一周他又来一封，还是这句「Please send us your best price」…这可能是同行在套价". Source: 图灵搜, 2026-10-15. https://www.turingsearch.cn/articles/xunpan-ke-neng-shi-tonghang-tao-jia-2026/
- "三个月后，另一家进口商拿相似规格来压价，报价单上的数字和当初那封几乎一样…那封 RFQ 就是同行贸易商在收表". Source: 灵贸, 2026-07-13. https://linkmao.cn/blog/rfq-price-only-no-specs-scam-check/ (illustrative case; may be a composite)
- "花了好几万开了阿里国际站…询盘质量极速下降，什么人来的都有". Also: "最后要做订单了，给我发了个其他供应商的报价表，比我们低8美分". Source: 邦阅网 community posts dated 2025-04-16 and 2025-04-08, listed on https://www.52by.com/faq/1115

**Buyer-side view**
- Buyers deliberately run wide RFQs: a 20–30 lead pool, then a 5–10 shortlist, then 2–3 finalists for pilot production. Source: NZTE, reviewed 2025-11-05. https://my.nzte.govt.nz/article/20251105-find-and-verify-suppliers-in-china
- So many "send best price" emails are honest first-stage benchmarking, not fraud. The skill should help sellers survive the cut, not insult the buyer.
- Thesourcingblog (a buyer-side guide) says Chinese suppliers ignore RFQs because "very few are serious. Many simply for benchmarking" *(search excerpt, not fetched)*.

**What is new vs 2.0**: 2.0 #14 covers *fraud* buyers and #2 covers *wrong-fit* outbound targets. This is the **inbound** triage of real but low-intent or competitor inquiries, plus how to quote without leaking the price list.

**Frequency / importance**: Freq H (daily on B2B platforms), Cost M (hours, plus price-list leakage).

**Skill proposal**
- `scripts/triage_inquiry.py`: paste the raw inquiry text and optional sender email/domain. It scores linkmao's 7 signals plus turingsearch's 4:
  - no company name
  - "best/lowest price / all products"
  - urgency or a push to WhatsApp
  - email domain does not match the company
  - only asks price over several messages
  - dodges use, country and volume
  - blank template attachment
  - "we have been in business X years" instead of a URL
  - asks for several unrelated categories
- Output: `archive` (≥3 signals) / `ask-first` / `quote`, the signals hit, and the matching reply.
- `assets/reply-playbook.md` additions:
  - 5-field ask-back (model, quantity, destination port, Incoterm, certification) in 50–80 words.
  - "Please share the competing quote's spec so we compare like for like."
  - Banded-price footer: "USD 18–32/pc depending on size/finish; subject to confirmed spec; valid 14 days."
- Rule for the agent: never send a full SKU price list to an `ask-first` lead.

---

## R2-03 报价单算错、写错 · Quote-sheet errors (Incoterms, DDP, validity, FX, payment wording)

**Quotes**
- "FOB、CFR、CIF 只适用于海运和内河运输…术语用错，出了问题时风险从哪一刻转移给买方，就说不清了". Also: "DAP 和 DDP…一字之差，差的可能是货值的两成". Also: "「30% 预付，70% 尾款」这句话，至少有两种理解：发货前付清…见提单副本付尾款". Source: 阿昌 (energy-storage exporter), 2026-10-01. https://achang.vip/notes/quote-mistakes.html
- "常见踩坑：FOB 报价漏算 THC 和文件费（约 USD 200-500/票），DDP 报价漏算目的国关税和 Customs Bond". Source: 麦特货代, updated 2026-10-07 *(search excerpt, not fetched)*. https://www.mightyshipping.com/guides/fob-cif-ddp-comparison

**Hard facts (sourced)**
- Under Incoterms® 2020, DDP is the **only** rule where the seller pays import tariffs. Under every other rule the buyer bears the import burden. ICC Guidance Note, April 2025. https://www.icc.fi/wp-content/uploads/2025/04/2025-04_using_incoterms_to-manage_tariff_risks.pdf
- ICC suggests DAP instead of DDP to "avoid seller exposure" when tariffs are volatile (same note).
- Under CIF the seller must insure at minimum ICC (C) for at least 110% of contract value; CIP requires ICC (A) (achang, above; consistent with Incoterms 2020).

**Buyer-side view**: "A price without an Incoterm, an MOQ and a lead time is not a quotation. It is an opening remark." Buyers record "Quoted price, currency and Incoterm… note FOB port too" for every supplier and compare row by row. Source: Globalucar (buyer-side Canton Fair guide), 2026-10-19. https://www.global-ucars.com/blog/canton-fair-phase-1-wrap-shortlist-suppliers-48-hours.html

**Frequency / importance**: Freq M (every quote, but errors are occasional), Cost H (one DDP or payment-wording mistake can wipe out the margin or the money).

**Skill proposal**
- `scripts/lint_quote.py` lints a quote or PI in text or CSV. It flags:
  - an Incoterm with no named place or port
  - FOB/CFR/CIF used with air, courier or rail
  - EXW from China to an overseas buyer (export clearance issue)
  - DDP with no HS code or no duty line
  - CIF with no insurance basis
  - missing currency, validity date, MOQ or lead time
  - ambiguous "30/70" wording (requires "balance before shipment" or "against copy B/L" to be explicit)
  - no bank-charges line
  - an "Incoterms 2020" version tag missing (Sinosure notes that L/C banks may treat this as a discrepancy)
- `assets/quote-sheet-template.md`: fields in the order buyers compare them, plus a footer with validity, FX buffer note, and "duties/taxes per Incoterm; government tariff changes after quote date are for buyer's account unless DDP".

---

## R2-04 美国关税反复叠加 · US tariff whiplash on Chinese goods

**Hard facts (sourced, dated; volatile, so recheck before use)**

US average tariff on Chinese goods (CRS IF12990, updated 2026-08-18). https://www.congress.gov/crs-product/IF12990

| Date | Average US tariff on China |
|---|---|
| 2017 | 2.7% |
| March 2025 | 39% |
| April 2025 | 73%, then 164% |
| May 2025 | 49% |
| November 2025 | 39% |
| February 2026 | 34% |
| July 2026 | 36.5% |

US tariff layers and events as of mid-October / November 2026 (Beato Capital, updated 2026-11-11, citing the Federal Register). https://beatocapital.com/guides/china-tariffs-2026/
- Normal duty: MFN + Section 301 list duty (25% Lists 1–3, 7.5% List 4A) + **12.5% Section 301 "forced-labor" tariff** from 2026-07-24 (91 FR 47318).
- Section 232 goods usually pay the 232 rate instead of the 12.5%; drones pay both.
- IEEPA tariffs are no longer collected since 2026-02-24, after *Learning Resources v. Trump* (2026-02-20). Refunds go through CBP's CAPE process, opened 2026-04-20.
- The Section 122 10% surcharge ran 2026-02-24 to 2026-07-24.
- De minimis has been suspended since 2025-08-29. This means courier samples to the US now need an entry and pay duty, which ties into R2-01.

Truce and exclusions:
- The US–China truce was extended to **2027-01-10**. Supply Chain Dive, 2026-11-09. https://www.supplychaindive.com/news/us-china-officially-extend-trade-war-truce-by-2-months/874107/
- 178 Section 301 exclusions were extended to 2027-01-09 (STR and EY, 2026-11-10; search excerpts).

**Quotes (exporter side)**
- "12月份的时候，其中一个客户发来邮件，说'先hold一下Q1的订单'". Also: one client stockpiled about 60% more in Q4, then ordered one small container in Q1. Another asked the trader to "帮他报了一版越南工厂的价格". Source: Simple (10-year SOHO turned 5-person trader), 2026-03-29. https://www.simplewholesale.cn/article/trump-tariff-how-we-deal-with-it
- Same author: "没降价…关税加的是客户那头的事…如果我为了留住客户主动降价，那等于我在替美国政府的政策买单".

**Buyer-side view**: US importers now track a duty stack per HTS line and price "landed cost". A Chinese quote that ignores the stack looks naive (Beato's worked example: 3% + 25% + 12.5% = 40.5% duty).

**Frequency / importance**: Freq M for US-exposed sellers (L for others), Cost H.

**Skill proposal**
- `references/tariff-landscape.md`: a dated snapshot with a "last verified" line and a rule to recheck before quoting. Covers the stacking formula, de minimis effect on samples, and the source list (USITC HTS, Federal Register, CBP).
- `scripts/landed_cost.py`: the user supplies HTS rates (no hardcoded rates, because they expire). It computes the buyer's landed cost from FOB, freight, insurance, duty layers, and MPF/HMF. Its purpose is the "help the buyer re-plan" email, not a price cut.
- Outreach trigger: add "tariff change on your HTS line" as a signal-based first line in `outreach-playbook.md`.

---

## R2-05 客户要求 China+1 · Buyer demands a non-China supply option

**Quotes**
- "From H2 2026, all orders must comply with China+1 strategy. Please confirm your alternative supply capability outside China by end of June." The author's first reaction: "完了，这客户要跑了". The client's answer: "中国+1是总部的全球采购政策…你只要能证明你有中国以外的供应选项，订单照下".
- Same article, after two months of trying Vietnam, India and Turkey: Vietnam unit price +12–15% with MOQ doubled; lead time "跟我说35天…你按50天做计划比较稳"; Turkey→Hamburg 40HQ freight about 40% above Shanghai→Hamburg. Final split: China 70–75%, Vietnam 25–30%, at +8% price.
- Source: Simple, 2026-09-17. https://www.simplewholesale.cn/article/china-plus-one-requirement-from-client **[uncertain: a single anecdote]**

**Buyer-side view**: the client says the request is "not targeted at you"; they want supply security, not the lowest cost.

**Frequency / importance**: Freq L–M (growing among EU and US mid-to-large importers), Cost H (losing a stable account).

**Skill proposal**
- `references/china-plus-one.md`, a response playbook:
  1. Clarify what the buyer actually requires (% share, which SKUs, deadline, audit needs).
  2. Answer honestly about what you can and cannot do; "give me 6 months" is acceptable.
  3. Offer the options a small seller really has: partner factory abroad, finishing or assembly abroad, or "Chinese core + backup line".
- Add a reply type "China+1 / origin requirement" to `reply-playbook.md`.
- Add an `origin_requirement` field to `icp-template.json` and `leads-template.csv`.

---

## R2-06 邮件被黑、收款账户被改 · Business email compromise and look-alike domains

**Quotes and cases**
- Case: a Taizhou exporter's mailbox was hacked. Fake emails sent its Argentine buyer's **US$35k tail payment** to a look-alike UK account; "以上邮件均被黑客即时删除". The loss was settled by mediation at 70% buyer / 30% seller. Source: 浙江贸促会, 2025-06-12. https://www.ccpitzj.gov.cn/art/2025/6/12/art_1229574285_49118.html
- Case: a fake buyer's domain ended ".1TD" while the real French company's ended ".LTD". The fraud was only spotted after converting the text to upper case. Source: 宁波金融业联合会 (Sinosure Ningbo staff), 2025-05-26. http://www.nbfa.org.cn/NewsList.aspx?CategoryId=142&ContentId=8234
- "那抄送的邮箱地址中一个不起眼的'l'成了'i'…" (loss of 80k+ RMB). Source: 温州网, 2025-03-24 *(search excerpt, not fetched)*. https://news.66wz.com/system/2025/03/24/105677549.shtml

**Hard fact (sourced; Korean data, used as a proxy since no Chinese aggregate was found)**
- Korea's FSS reported 1,591 trade-fraud cases worth US$96M from 2021 to H1 2025, of which **95.4% were email-hacking account-change scams**. Source: FSS press release 2025-09-29, via KDI EIEC *(search excerpt of the official PDF; koreabizwire page was blocked)*. https://eiec.kdi.re.kr/policy/callDownload.do?dtime=20250929161410&filenum=1&num=271716
- US EXIM (2025-01-29) describes the same pattern hitting its export-credit policyholders *(search excerpt)*. https://grow.exim.gov/blog/is-your-international-customers-payment-going-to-the-right-place

**Buyer-side view**: the mediator held the **buyer** mainly at fault for paying a new account without a phone check (ccpitzj). But exporters still lose the money or the client. Both sides want a written "account never changes by email" rule.

**Frequency / importance**: Freq L, Cost H (the whole balance payment).

**Skill proposal**
- `scripts/check_lookalike.py` (stdlib): compare a sender address with the known buyer domain in `leads.csv`. Checks:
  - edit distance
  - homoglyphs (l/1/I, rn/m, 0/o)
  - TLD swap (.ltd/.1td, .com/.co)
  - added hyphens
  - free-mail vs corporate
- Flag any email in a thread whose domain differs from the first message.
- `assets/pi-bank-clause.md`: an English PI footer, "Our bank details are fixed in this PI. We will never change them by email; confirm any change by phone/video with [name]."
- Mailbox hygiene checklist: 2FA, auto-forward rules audit, login alerts.

---

## R2-07 买家背调做到注册层 · Registry-level buyer verification before credit terms

**Quotes and cases (Sinosure Ningbo, 2025-05-26)** http://www.nbfa.org.cn/NewsList.aspx?CategoryId=142&ContentId=8234
- A "US buyer" ordered textiles; the real company with that name makes photovoltaics. The impostor used a prepayment as bait, then disappeared with the balance.
- An Italian buyer accepted a price 20% above market at once and wanted fast shipment on open account. A credit check showed a new shell company.
- A Saudi buyer proactively offered Sinosure cover and was found to be "广撒网…集中密切联系多家不同行业的出口商".
- The 信步天下 app's credit "red light" stopped a US$950k deal on 30% deposit + 70% OA.

**Hard facts (sourced)**
- UK Companies House is free to view: officers, filings, persons with significant control. Source: Companies House search page. https://find-and-update.company-information.service.gov.uk/
- From 2025-11-18, directors and PSCs must verify their identity with Companies House. WONE Global *(search excerpt)*. https://woneglobal.org/capabilities/commercial-intelligence-and-market-research/guide/company-and-counterparty-checks/
- EU VIES confirms whether a VAT number is active for intra-EU trade. It does not cover the UK. Your Europe *(search excerpt)*. https://europa.eu/youreurope/business/finance-and-tax/vat/check-vat-number-vies/index_en.htm
- OpenCorporates search is free "for personal use only"; business use needs a paid API from GBP 2,250/yr, as of 2026-10-19. Paul Lange directory *(search excerpt)* **[licence matters for an open-source skill]**.
- Turingsearch's 5 free checks before quoting: website exists and domain age; registry business scope; physical premises on maps; import records; email-domain age (2026-10-15, link in R2-02).

**Buyer-side view**: buyers run the same checks on suppliers ("request a copy of the supplier's Chinese business licence and cross-check it in official government databases", NZTE 2025-11-05). Asking for a registration number is normal B2B practice and does not offend.

**Frequency / importance**: Freq M (each first deal on credit terms), Cost H.

**Skill proposal**
- `scripts/verify_buyer.py` (stdlib `urllib`, `json`):
  - Builds registry lookup URLs by country (UK Companies House, EU e-Justice/BRIS, US state Secretary of State, etc.).
  - Calls the VIES REST endpoint for EU VAT numbers.
  - Gets domain registration date via RDAP (`rdap.org`).
  - Compares the registry name/address with the email domain and the claimed address.
  - Output: a verification card stored on the lead row.
- Do not scrape OpenCorporates; link to it only.
- `references/compliance.md` addition: "verification depth by payment term". 100% TT before shipment needs light checks; D/P, B/L copy or OA needs a registry check, Sinosure/credit report, and a phone call to the registered number.

---

## R2-08 付款条款被一步步改掉 · Payment-term erosion mid-deal

**Quotes and cases**
- Sinosure Guangdong case (published 2025-03):
  - A Zhongshan micro furniture maker had a US$440k Saudi order on 30% deposit + 70% before shipment.
  - Before shipment the buyer asked to ship first and pay "见提单副本付款". The seller agreed without written terms and the buyer defaulted.
  - The policy (小微企业信保易) caps one buyer at **US$150k**, so even the payout left heavy losses.
  - Sinosure's lesson: "在买家初次口头提出修改合同支付方式时，风险苗头已初显".
  - Source: https://nb.sinosure.com.cn/xwzx/xbsa/2025/03/219644.shtml
- Turkish buyer at a fair: "等收到货款后再将提单电放". The goods sat unclaimed, local customs would not let the exporter take them back without a formal rejection, and after 4 months they were auctioned. The original importer bought them cheaply. Source: nbfa 2025-05-26 (link in R2-07).

**Buyer-side view**: not found in a fetched buyer source. Buyers' cash-flow pressure (Red Sea delays in the Sinosure case) is the usual stated reason **[uncertain]**.

**Frequency / importance**: Freq M (per deal with new or mid-size buyers), Cost H.

**Skill proposal**
- `references/payment-terms.md`: a risk ladder from TT 100% → 30/70 before shipment → L/C at sight → D/P → B/L copy → OA. For each step: who controls the goods, typical traps (buyer-nominated forwarder under D/P, telex release), and what to do before moving down a step (written amendment, credit check, insurance limit vs exposure).
- Checklist "buyer asks to change terms": stop, get it in writing, rerun R2-07, check insurance cap vs order value, offer a counter (split shipment, L/C).
- Reply template: polite refusal with an alternative.
- `pipeline.py`: flag `terms_changed=yes` leads as red.

---

## R2-09 展会名片跟进衰减 · Trade-show / Canton Fair lead decay

**Quotes**
- "展台收了近百张名片，回国后统一群发 'Nice to meet you'，两周后只有两三个回复". The fix offered: tier the cards on return, handle the high-intent tier within 24–48h, and make the first email state 4 booth facts (show and booth number, SKU or spec discussed, market/quantity/window, promised next step). Source: 灵贸, 2026-09-09. https://linkmao.cn/blog/trade-show-follow-up-low-reply/
- "很多业务员觉得…样品是敲门砖…但不少工厂老板坚决不同意" (Canton Fair sample requests, 10100, 2026-10-22, link in R2-01).

**Buyer-side view**
- Buyers shortlist inside 48 hours. "Generic messages lose. 'Thank you for your time, please send your catalogue' arrives in an inbox alongside two hundred identical notes and reads as nothing."
- Buyers keep "two or three [suppliers] per part category" and archive suppliers who stay silent after two nudges.
- Source: Globalucar, 2026-10-19 (link in R2-03).
- An ecommerce buyer: "I have 1000x more luck going to tradeshows… meeting actual suppliers in person" (Reddit thread, link in R2-01).

**Hard fact**: the 140th Canton Fair Phase 1 ran 15–19 Oct 2026, with a changeover 20–22 Oct (Globalucar).

**Frequency / importance**: Freq M (2–4 shows a year), Cost M–H (the most expensive leads a SOHO buys).

**Skill proposal**
- `scripts/show_leads.py`: import a card CSV (name, company, email, show, booth notes, asked for quote/sample, window). Assign tiers A/B/C, set due dates (A ≤48h, B ≤72h, C quarterly), and merge into `leads.csv` with `source=show:<name>`.
- `assets/show-followup-template.md`: a 4-fact first email, a second email at +5–7 days with one new fact, then park with "展会-暂缓" and a re-touch month.
- A booth note-taking card (fields that buyers also record: SKU, Incoterm, MOQ, sample status).

---

## R2-10 "我们已有供应商" 深打法 · Incumbent supplier: when the door actually opens

(2.0 has one line; this is the new angle of **timing triggers**.)

**Quotes**
- "'keep your contact in our supplier database'…意思是「你进候选池了，等下一次我这边出问题或要加供应商时会找你」".
- The author lists four situations (long-term incumbent, incumbent being complained about, second-source need, simply not now) and four moments when buyers loosen: incumbent late delivery, price or MOQ increase, a quality incident, buyer expansion or a new category.
- Don'ts: cut price at once, criticise the incumbent, chase "just following up".
- Source: 图灵搜, 2026-10-14. https://www.turingsearch.cn/articles/kehu-shuo-yi-you-yi-gong-ying-shang-le-zen-me-qie-jin-qu/

**Buyer-side view**: "keep a second source in Bucket B for the same part family. Single-source dependence… is a risk you are taking on your own balance sheet" (Globalucar, 2026-10-19). Buyers do want backups.

**Frequency / importance**: Freq H (most common polite no), Cost M.

**Skill proposal**
- `pipeline.py`: a new status `incumbent` with a `trigger_watch` field (delivery, price, quality, expansion) and a 60–90-day value re-touch.
- `assets/reply-playbook.md`: 3 tiered replies (no supplier / unhappy / long-term incumbent: pitch the increment such as small fast batches or mixed containers).
- Read supplier concentration from customs data (one supplier for years vs switching often).

---

## R2-11 海关数据买了用不起来 · Paying for customs data that doesn't turn into buyers

**Quotes**
- "一个做机械配件的朋友，去年雄心勃勃地花了5万块…半年过去了，数据是下载了一大堆，但一个像样的客户都没开发出来". Source: 小满 OKKI, 2026-01-30. https://www.xiaoman.cn/article/991.html **[vendor selling its own bundle; anecdote]**
- Same source gives rough annual prices: 腾道 5–10万, 环球慧思 4–8万, bundles 2–5万 **[uncertain: vendor-reported, conflicts with round-1 figures]**.

**Hard facts (sourced)**
- ImportYeti's free plan covers US ocean import bills of lading from 2015. Downloads and Mexico data are paid only. The Pro price was not public on 2026-10-11.
- Importers can request manifest confidentiality under 19 CFR 103.31(d) (2 years, renewable).
- The EU does not publish customs records by company.
- Source for all three: Outfound, last updated 2026-10-11. https://outfound.ai/compare/importyeti (competitor of ImportYeti; facts cross-cite CFR).

**Buyer-side view**: none relevant. Customs data is invisible to buyers, but busy importers "hear from many suppliers who found them the same way" (Outfound).

**Frequency / importance**: Freq L (a yearly purchase decision), Cost M–H (30–100k RMB).

**Skill proposal**
- `references/customs-data.md`, a buy-or-not checklist:
  - Does your market publish named records (US, parts of LatAm, India) or not (EU)?
  - Trial with 3 of your existing clients' names.
  - Total cost = fee + hours.
- A reading guide: forwarder consignees, shipment rhythm, supplier concentration.
- `score_leads.py`: add forwarder/broker name patterns for consignees (extending the 2.0 forwarder drop to customs-record names).

---

## R2-12 TikTok / 短视频 B2B 询盘多、成交少 · Social video leads with low B2B fit

**Quotes**
- "TikTok上平均每1000次播放会收到一次询盘，其中约3%-10%的询盘最终会转化为订单" (practitioner estimate).
- A toy factory closed 100+ B2B customers in 10 months (10–20% of sales).
- An industrial vending-machine factory got 4–5 inquiries a day but "目前为止还没有成交", comparing the channel to "在大海里钓金枪鱼".
- Source: 亿邦动力, 2025-09-03. https://www.ebrun.com/20250903/598204.shtml **[uncertain: interview figures]**

**Buyer-side view**: "每天领英上会收到差不多10家工厂的消息，中国的供应商没事就给我发产品目录，我看都不会看，直接一键到（邮箱）垃圾桶" (a buyer quoted by Liz, same article). Ecommerce buyers "live on TikTok" and find suppliers there, but first orders are usually under US$20k.

**Frequency / importance**: Freq M (for consumer goods), Cost M. Low fit for heavy industrial goods.

**Skill proposal**
- `references/lead-sources.md` section "inbound social leads":
  - Product-fit rule (small consumer goods fit; >US$50k industrial goods poor fit).
  - Qualifying questions for DM leads (channel they sell on, first-order size, platform).
  - Moving the chat to email with a PI on safe terms (the factory owner says buyers fear "付款了不发货" off-platform, so offer a trade-assurance alternative).
- `pipeline.py`: add `source=tiktok` so funnel stats show the channel's real conversion.

---

## R2-13 AI 群发反噬与自动化失控 · AI outreach backlash and missing guardrails

(Partly overlaps 2.0 #6. The new angle is **agent guardrails and metric honesty** as more users run AI agents.)

**Quotes**
- After 80,000 mass emails, a US prospect replied: "Please remove me from your list. I receive 50 similar emails every day, all written by ChatGPT." Source: 网易外贸通, 2026-10-13. https://www.163.com/dy/article/L950GQIB05561G2R.html (vendor; the anecdote ends in a product pitch).
- "'生成了多少客户'与'完成了多少客户开发'并不是同一个概念…如果目标客户定义错误，Agent会更快地找到大量不匹配的企业". Its practical tips: count candidates, matched buyers, valid contacts, delivered, and inquiries separately; set send caps, stop conditions and human review nodes. Source: 麦穗AI获客 on 雨果网, 2026-10-23. https://www.cifnews.com/article/189632

**Buyer-side view**: the "50 ChatGPT emails a day" quote above. Buyers increasingly recognise and resent AI tone.

**Frequency / importance**: Freq H among AI-tool users, Cost M (domain reputation, brand).

**Skill proposal**
- `pipeline.py stats`: split the funnel into candidate → matched → valid contact → delivered → replied → inquiry → order.
- Add an agent safety block to `SKILL.md`: a daily send cap, a never-contact list, stop on bounce >2%, and a human approval step before the first send per batch.
- `lint_outreach.py`: add AI-tell phrases ("I hope this email finds you well", "delve", "in today's fast-paced") **[minor; partial overlap with 2.0 cliché check]**.

---

## Uncertainties and gaps

- **Vendor-blog numbers** (hxshan sample conversion table, 10100 "<5%", ebrun TikTok ratios, xiaoman customs-data prices) are self-reported and not audited. Use them as illustrative ranges only, and say so in any reference doc.
- **US tariff figures** change every few weeks. Everything in R2-04 is dated (last checked 2026-11-11/12). The truce ends 2027-01-10, so 3.0 must not hardcode rates.
- **BEC frequency in China**: no national Chinese aggregate was found. The Korean FSS figure is a proxy, from a search excerpt of the official PDF rather than a full fetch.
- **Buyer-side view for payment-term erosion (R2-08)** was not found in a fetched source.
- **China+1 (R2-05)** rests on one detailed SOHO account plus round-1 search snippets (cifnews/180238, yicai 2026-05-22) that were not re-fetched this round.
- **toutiao 2026-05-12 sample article** and **alinegpt sample checklist** from earlier searches were not fetched this round, so they are not cited.
- **OpenCorporates licence**: free use is personal only. An open-source skill should link to it, not scrape or call its API.
- Pages that failed to load: fumasoft (bot wall), joinf (HTTP 567), koreabizwire (captcha).

## Sources fetched this round (25 fetched + 1 search-only)

1. 图灵搜 套价, 2026-10-15. https://www.turingsearch.cn/articles/xunpan-ke-neng-shi-tonghang-tao-jia-2026/
2. 图灵搜 已有供应商, 2026-10-14. https://www.turingsearch.cn/articles/kehu-shuo-yi-you-yi-gong-ying-shang-le-zen-me-qie-jin-qu/
3. 福步 free-sample thread, 2023-08-16. https://bbs.fobshanghai.com/thread-8998893-1-1.html
4. 邦阅网 Alibaba RFQ thread and related posts, 2022–2025. https://www.52by.com/faq/1115
5. CRS IF12990, 2026-08-18. https://www.congress.gov/crs-product/IF12990
6. Beato Capital China tariffs 2026, updated 2026-11-11. https://beatocapital.com/guides/china-tariffs-2026/
7. Sinosure DP case, 2025-03. https://nb.sinosure.com.cn/xwzx/xbsa/2025/03/219644.shtml
8. 宁波金融业联合会 贸易避险十八招 (上), 2025-05-26. http://www.nbfa.org.cn/NewsList.aspx?CategoryId=142&ContentId=8234
9. 环形山 sample policy, 2026-09-18. https://hxshan.com/insight/sample-and-prototype-policy-overseas-buyers/
10. 大数跨境 广交会样品, 2026-10-22. https://www.10100.com/article/154951899
11. Simple tariff response, 2026-03-29. https://www.simplewholesale.cn/article/trump-tariff-how-we-deal-with-it
12. Simple China+1, 2026-09-17. https://www.simplewholesale.cn/article/china-plus-one-requirement-from-client
13. 亿邦动力 TikTok B2B, 2025-09-03. https://www.ebrun.com/20250903/598204.shtml
14. 灵贸 trade-show follow-up, 2026-09-09. https://linkmao.cn/blog/trade-show-follow-up-low-reply/
15. 灵贸 price-only RFQ, 2026-07-13. https://linkmao.cn/blog/rfq-price-only-no-specs-scam-check/
16. 小满 customs data, 2026-01-30. https://www.xiaoman.cn/article/991.html
17. Outfound ImportYeti review, 2026-10-11. https://outfound.ai/compare/importyeti
18. 雨果网 AI 获客能力边界, 2026-10-23. https://www.cifnews.com/article/189632
19. 网易外贸通 AI 开发客户, 2026-10-13. https://www.163.com/dy/article/L950GQIB05561G2R.html
20. 浙江贸促会 BEC mediation case, 2025-06-12. https://www.ccpitzj.gov.cn/art/2025/6/12/art_1229574285_49118.html
21. ICC Incoterms tariff guidance note, 2025-04. https://www.icc.fi/wp-content/uploads/2025/04/2025-04_using_incoterms_to-manage_tariff_risks.pdf
22. 阿昌 报价 8 个坑, 2026-10-01. https://achang.vip/notes/quote-mistakes.html
23. Reddit r/ecommerce "Why is sourcing such a nightmare?", about 2025-08. https://www.reddit.com/r/ecommerce/comments/1n1haqt/why_is_sourcing_such_a_nightmare/
24. Globalucar Canton Fair buyer shortlist, 2026-10-19. https://www.global-ucars.com/blog/canton-fair-phase-1-wrap-shortlist-suppliers-48-hours.html
25. NZTE find and verify suppliers, reviewed 2025-11-05. https://my.nzte.govt.nz/article/20251105-find-and-verify-suppliers-in-china
26. *(search result, not fetched; corroborated by STR, EY, SCMP, TT News excerpts)* Supply Chain Dive truce extension, 2026-11-09. https://www.supplychaindive.com/news/us-china-officially-extend-trade-war-truce-by-2-months/874107/

Cited from search excerpts only (not fetched): mightyshipping, KDI/FSS PDF, EXIM blog, 温州网, Your Europe VIES, WONE Global, Paul Lange, thesourcingblog, STR, EY.
