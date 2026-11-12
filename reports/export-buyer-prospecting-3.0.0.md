# export-buyer-prospecting 3.0.0 · release report · 2026-11-12

## Why
Vic asked for a second pass of pain-point research and a 3.0. Round 2 (docs/pain-points-research-r2.md, 25 sources, 2025–2026) found 13 new pain points between "buyer found" and "first order paid": price-fishing inquiries, free samples, quote errors, trade-show lead decay, email hacking, buyer verification, payment-term erosion, US tariffs, incumbent suppliers, China+1, customs-data ROI, social-video leads, AI-outreach backlash.

## What changed
6 new scripts (triage_inquiry, sample_policy, lint_quote, check_lookalike, verify_buyer, landed_cost), pipeline additions (import-show, sample track, incumbent, terms flag, per-source stats, state/tz), 3 references, 3 assets, 7 new evals (19 total). See CHANGELOG.

## Real-execution test
A test agent followed only SKILL.md for a Yangjiang kitchenware maker targeting US importers, with live web search: 9 real US leads, scoring, decision-makers, domain check, email 1, pipeline, inquiry triage, quote, landed cost with HTS rates looked up on hts.usitc.gov, samples, buyer check, look-alike domains.
Findings: 1 critical (tariff stack ignored Section 232 derivatives for knives/utensils), 8 major, 11 minor. Fixed in this release: the critical one, all 8 major, and 7 minor.

## Known open items (next round)
- Not yet exercised by the test agent: verify_buyer --terms bl-copy reply flow, import-show with real cards, WhatsApp follow-up lint.
- find_contacts still prints German search hints for US; build_queries LinkedIn query uses only the last product word.
- pipeline: duplicate log events not warned; logging "sample" replaces a running quote track.
- DNSBL blacklist check still manual (mxtoolbox link).
- Tariff reference must be re-verified before 2027-01-10 (truce end) and 2027-01-09 (301 exclusions).

## Audit
tools/audit.py: 178/178 passed (skills-ref validate + house rules).
