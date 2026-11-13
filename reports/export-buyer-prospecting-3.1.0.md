# export-buyer-prospecting 3.1.0 · release report · 2026-11-13

Iteration round 1 after the 3.0.0 release (review process v1.2).

## G1 Structure · pass
`tools/audit.py`: 189/189 passed (skills-ref validate + house rules, including the three rules added in review v1.2). SKILL.md 206 lines.

## G2 Script regression · pass
`evals/checks.json`: 25/25 (11 new, one per bug fixed this round).

## G3 Privacy and authenticity · pass
Automatic scan now covers evals/ too; it found 3 real-looking third-party domains in test fixtures and checks (replaced by example domains). No invented sender data in SKILL.md or assets.

## G4 Freshness · pass
Opened on the official pages on 2026-11-13: Mexico decrees DOF 29-12-2025, 23-04-2026 and 13-10-2026 (sidof.segob.gob.mx, full texts searched by tariff line); Ley Federal de Derechos art. 49 (diputados.gob.mx, DTA 8 al millar); Receita Federal habilitação FAQ (Pergunta 07); Inmetro FAQ on Portaria 231/2026. US section unchanged (verified 2026-11-12).

## G5 Real-execution test · in-house (not independent)
The run had no sub-agent tool, so the main agent ran the test by following only SKILL.md and its files, with live web search. Cases (rotated from round 0's US kitchenware and DE drinkware): eval 17 (DE buyer asks 70% against B/L copy and says the bank account changed), eval 18 (Canton Fair cards from US, MX, AU, SA, AE, GB), eval 4 (LED panel importers in Mexico and Brazil).

Findings before fixes: 0 critical, 7 major, 8 minor.
- Major: Mexico's 2026 non-FTA duties (5–50%) absent; Brazil importer caps and Inmetro registration absent; red terms flag could never be cleared; show cards graded by substring ("specs" matched "pcs" → A; catalogue collectors → B); show leads fell onto the cold sequence after email 1; look-alike check listed the user's own address as "new" and passed a bank-change mail from a trusted (possibly hacked) mailbox; FOB buyer-nominated forwarder trap missing from B/L-copy guidance.
- Minor: duplicate log events advanced the sequence; sample silently replaced a running quote track; German Impressum hints for any country; LinkedIn query used one word ("LED") and English country names; Gulf Fri–Sat weekends ignored; duplicate show cards dropped silently; night send windows not flagged; real-looking domains in fixtures.
All 15 fixed and locked by checks; the three scenarios re-run clean. After fixes: 0 critical, 0 major.

## G6 Expert review · in-house (not independent)
Scored by the main agent in the role of a 15-year export sales manager, without an independent reviewer. Under review v1.2 these scores do not count toward graduation.

| Item | 3.0.0 | 3.1.0 | Note |
|---|---|---|---|
| Correctness | 8 | 9 | MX/BR facts now dated and sourced |
| Professional depth | 7.5 | 8.5 | nominated-forwarder trap, BR import caps, Gulf weekends |
| Executability | 8 | 8.5 | stuck red flag and show track fixed |
| Safety and compliance | 8 | 9 | bank-change stop even from trusted domains, own-domain spoofing |
| Trigger accuracy | 8.5 | 8.5 | 2 new evals (1 negative) |
| Concision | 7.5 | 8 | two Gotchas merged; country detail in references |
| **Average** | 7.9 | **8.58** | no item below 7 |

## Competitor comparison (preliminary, for graduation)
From SKILL.md and README excerpts of 7 same-topic skills (not yet full reads): xiongQvQ/b2b-lead-hunter (paid search APIs, SMTP sending), zhangruiying12138-web/foreign-trade-lead-agent (image-to-leads, cold emails), microsoft/cat-agent-skills b2b-outreach-suite (generic B2B copy and objections), ITch8/customs-data-skills (customs-data SOP), noique/cross-border-ecommerce-skills google-whatsapp / linkedin prospecting (channel-specific), qpood/b2b-buyer-qualification (buyer briefs), fleixweb/superleads (prospecting + background checks).
Where this skill leads: coverage from first email to paid first order (inquiry triage, samples, quote lint, payment and BEC safety, dated tariffs), stdlib scripts with regression checks, no API keys. Where others lead: actual sending/automation (b2b-lead-hunter), product-image search (foreign-trade-lead-agent), deeper customs-data method (customs-data-skills). A full item-by-item comparison is due before graduation.

## Known open items (next round)
- Run G5 and G6 with independent sub-agents (this round's do not count toward graduation).
- Not yet covered: Brazil import-tax cascade (II, IPI, PIS/COFINS, ICMS) as a calculation; Mexico IGI per fracción is a manual lookup; LGPD (BR) and Mexico privacy rows in compliance.md; DNSBL blacklist check still manual.
- G5 coverage per eval is now tracked in vic-skills/STATE.md. Exercised so far: 1 (DE, 2.0 test), the US deal-stage flow (3.0 test, close to 14–16), and 4, 17, 18 (this round, in-house). Still to run: 2, 3, 5, 6, 7, 8, 9, 13, 20.
- Re-verify US tariffs before 2027-01-09 (301 exclusions) and 2027-01-10 (truce end).
