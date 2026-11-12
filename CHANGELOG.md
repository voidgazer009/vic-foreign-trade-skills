# Changelog

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
