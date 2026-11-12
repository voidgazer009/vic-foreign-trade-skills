# From inquiry to first order: inbound leads, samples, competition

## Platform and website inquiries (Alibaba, Made-in-China, Global Sources, your site)
Buyers send wide RFQs on purpose (a pool of 20–30, then a shortlist of 5–10, then 2–3 for pilot orders), so most "send best price" mails are honest benchmarking. Some are competitors collecting your price list.
- Triage every inquiry: `scripts/triage_inquiry.py inquiry.txt --from <address> --company "<claimed name>"`.
- QUOTE: answer within a few hours with the items asked, not the catalogue.
- ASK-FIRST: the 5-field ask-back and a price band. A real buyer answers; a price collector usually doesn't.
- ARCHIVE: one polite line, no prices.
- Speed still wins: reply within 4 working hours on business days; platform reply time affects ranking.

## Samples
Free samples with free shipping attract the most low-intent requests; a sample fee credited against the first order filters them, and serious buyers accept it when the policy is said early. Practitioner figures vary and are not audited; measure your own with `pipeline.py stats`.
- Decide per request: `scripts/sample_policy.py`.
- Agree the spec first: `assets/sample-confirmation-sheet.md`.
- Day 3 / 7 / 21 follow-ups are scheduled when you log `sample`.

## Trade-show leads
See `assets/show-followup-template.md`. A-grade cards are answered within 48 hours with four booth facts.

## Social video and DMs (TikTok, Instagram, Facebook groups)
Good fit for small consumer goods and e-commerce sellers (first orders often under USD 20k); poor fit for heavy industrial goods. Qualify DM leads with three questions: where they sell, first-order size, timing. Move to email and a PI; buyers fear paying off-platform, so offer a safe term (deposit + balance before shipment, or a platform's trade assurance). Tag them `source=tiktok` in the leads CSV so `pipeline.py stats` shows the channel's real conversion.

## Customs data: buy or not?
Before paying for a subscription (often tens of thousands of RMB per year):
- Does your target market publish named import records? US bills of lading: yes (ImportYeti free tier; importers may request confidentiality). Several Latin American countries and India: yes, through paid providers. The EU: no company-level records.
- Test it with three of your existing customers' names: does it find them, and their real volumes?
- Count total cost: fee + the hours to work the data. A list nobody contacts is worth nothing.
- Read records for: consignee that is a forwarder (drop), shipment rhythm (monthly = real importer), number of suppliers (one supplier for years = hard to switch; switching often = open door).

## The buyer asks for a non-China option (China+1)
Often head-office policy, not a sign they are leaving. Ask what is required (share %, SKUs, deadline, audit). Expect higher unit prices, bigger MOQs and longer real lead times in Vietnam, India or Turkey than quoted. Options for a small seller: a partner factory abroad for part of the volume, final assembly abroad, or "China core + backup line". Show a written plan and a date.

## AI-driven outreach: guardrails
Buyers now get dozens of AI-written mails a day and delete them on sight. Rules for an agent using this skill:
- A daily send cap per mailbox (see `references/deliverability.md`), a do-not-contact list, and stop at 2% bounces.
- A human approves the first message of every batch.
- Count the funnel honestly: candidates → matched buyers → valid contacts → delivered → replied → inquiry → order. "Generated 500 leads" is not customer development.
