# Changelog

## export-buyer-prospecting 3.0.0 · 2026-11-12
From buyers found to a safely paid first order. Built on 13 more pain points (docs/pain-points-research-r2.md, 25 sources).
- New deal stage (steps 10–13) and router rows for inquiries, samples, quotes, trade shows, buyer checks, payment changes and US tariffs
- New `triage_inquiry.py`: price-fishing / low-intent signals → QUOTE / ASK-FIRST / ARCHIVE with the reply to send
- New `sample_policy.py`: free vs credited fee vs prepaid tooling, US de minimis warning, sentence to send
- New `lint_quote.py`: Incoterm with named place and version, sea-only terms by air, EXW from China, DDP duty lines, CIF/CIP insurance, validity, MOQ, lead time, explicit 30/70 trigger, bank-charge and anti-hacking clauses, placeholders
- New `check_lookalike.py`: look-alike buyer domains (l/1, rn/m, TLD swap, hyphen) in a sender or a whole thread
- New `verify_buyer.py`: EU VAT via official VIES, domain age via RDAP, registry links per country, check depth by payment term
- New `landed_cost.py`: buyer landed cost with user-supplied duty layers, US MPF/HMF (FY2027 limits)
- `pipeline.py`: `import-show` (A/B/C trade-show cards), sample day 3/7/21 track, `incumbent` 60-day re-touch, red `terms` flag, results by lead source
- `lint_outreach.py`: AI-tell phrases
- New references: inquiry-to-order, payment-and-fraud, tariff-landscape (dated); new assets: quote-sheet, sample-confirmation-sheet, show-followup; reply playbook adds price objection, China+1, three "we have a supplier" variants, 5-field ask-back
- SKILL.md example no longer carries an invented sender company; 19 evals
- Fixed after a real-execution test (US kitchenware from Yangjiang, live search, 20 findings): Section 232 checked first in the tariff guide (knives 8211 and utensils 8215 pay 25% on full value and skip the 12.5% forced-labor tariff); compound duties (`MFN=4.6+0.8c`) and whole-entry MPF in landed_cost; `--draft` mode so drafts with signature placeholders don't loop; quote linter ignores "unless DDP" and "21 CFR"; triage returns VERIFY when the sender imitates the named company's domain; lead scorer knows ISP mailboxes, email vs website domain mismatch, President/Owner titles and "11-50" ranges; pipeline uses a state/tz column for multi-zone countries; look-alike check never trusts free mail, catches brand.com.evil.net, and warns that a real domain can be hacked; "FDA approved" flagged; SPF ?all warned; free-mail and high-risk-country warnings in verify_buyer and sample_policy

## export-buyer-prospecting 2.0.0 · 2026-11-12
Rebuilt around 15 pain points researched from Chinese and English exporter communities (docs/pain-points-research.md).
- New "Start here" router: jump straight to the user's problem (no replies, spam, no decision-maker, silent after quote…)
- New `scripts/check_domain.py`: SPF / DKIM / DMARC / MX check for the sender domain, MX check for lead emails (DNS-over-HTTPS, stdlib)
- New `scripts/find_contacts.py`: buying-committee searches with local job titles, email pattern inference from a known address, umlaut/accent transliteration
- New `scripts/pipeline.py`: CSV follow-up tracker with cold and post-quote cadences, buyer local time, funnel diagnosis
- `lint_outreach.py`: LinkedIn and WhatsApp modes
- New references: deliverability, decision-makers, channels-and-culture, market-selection; new assets: reply-playbook, linkedin-whatsapp-templates
- Benchmarks section, fake-buyer signals, industrial buying committee, 12 evals
- Fixed after a real-execution test (German drinkware buyers, 27 findings): umlaut-safe buyer types (Großhändler, Händler, Lieferant), whole-word matching (no more Werbeagentur→agent), promotional-products and manufacturer types, closeout-buyer penalty, 30 more generic inboxes; NXDOMAIN and full-address input in check_domain; both umlaut spellings, particles and double names in find_contacts; post-reply track, Tue–Thu roll-over, your-time send windows and LinkedIn-first for DE/AT/CH in pipeline; linter catches [Address] placeholders, fake addresses, 'catalogue', allows BPA-free and caps company names, lists claims to confirm; SKILL.md asks the user for proof points instead of inventing them

## export-buyer-prospecting 1.0.0 · 2026-11-12
- First release: localized query builder (16 languages, 33 countries), ICP lead scorer with forwarder/marketplace/duplicate filtering, cold-email linter, 4-touch sequence, compliance guide (CAN-SPAM, GDPR, UWG §7, PECR, CASL, Spam Act), 6 evals.
