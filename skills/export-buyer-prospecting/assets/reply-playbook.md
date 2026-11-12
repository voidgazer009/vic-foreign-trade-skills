# Reply playbook: answer within 4 working hours

Classify the reply, then use the matching move. Log it: `python3 scripts/pipeline.py log "<company>" replied|positive`.

| Reply type | Signal | Move |
|---|---|---|
| "Send catalogue / more info" | Mild interest | One page, 5–8 items matching *their* range, plus one question: target market, volume, or price level |
| "What's your price?" | Comparing | Run `scripts/triage_inquiry.py` first. QUOTE: full offer from `assets/quote-sheet-template.md`, linted with `scripts/lint_quote.py`. ASK-FIRST: the 5-field ask-back and a price band only |
| "Too expensive" / "another supplier is cheaper" | Negotiating | Never cut at once. Ask for the competing spec to compare like for like (material, thickness, packaging, certification, Incoterm). Then trade, not discount: a lower price for a higher quantity, a simpler pack or longer lead time |
| "Send samples" | Strong | Run `scripts/sample_policy.py`; send `assets/sample-confirmation-sheet.md` with the sample; log `sample` (day 3/7/21 checks) |
| "We have a supplier" | Polite no | See the three variants below; log `incumbent` with the trigger to watch |
| "We need a non-China option" (China+1) | Policy | Ask what exactly: share %, which SKUs, deadline, audit. Answer honestly what you can do (partner factory abroad, final assembly abroad, or "China core + backup") and by when. Often the order continues if you show a plan |
| "Change payment terms" (ship first, B/L copy, OA) | Risk | Do not agree in the thread. Log `terms`, follow `references/payment-and-fraud.md` |
| "Not now" | Timing | Ask when the next sourcing cycle is; log `nurture` and note the month |
| "Talk to X" / referral | Gold | Thank them, write to X citing the referrer in the first line |
| Out-of-office | None | Do not count as a reply; resend after their return date |
| "Remove me" / "not interested" | Stop | Confirm in one line, log `unsubscribed`, never contact again |

## After a quote goes silent (day 2 / 7 / 14 / 21)
- Day 2: restate their three key needs; "if these are right, no need to reply".
- Day 7: add value: an option, a bundle, a lead-time or freight change.
- Day 14: proof from a similar buyer (anonymised).
- Day 21: ask directly which part is blocking: price, spec, timing, or another supplier.
Never send "Any update?" alone. Every follow-up carries something new.

## "We have a supplier": three variants
- **They are happy, long-term:** "Understood. Many of our customers keep their main supplier and use us for small fast batches, mixed containers or new items. If one of those ever helps, I'm here." Re-touch in 60–90 days with one new fact.
- **They hint at a problem** (late, price rise, quality): ask one question about it, then offer a small trial order or a side-by-side sample. Never criticise the other supplier.
- **They need a second source:** send a short capability page for the same part family, and offer to quote the 2–3 SKUs where a backup matters most.
Buyers loosen when the incumbent is late, raises price or MOQ, has a quality incident, or when they expand or add a category. That is the trigger you log.

## The 5-field ask-back (for price-only inquiries)
Model/spec · quantity per order and per year · destination port · Incoterm · certification needed. 50–80 words, plus a price band ("USD 3.4–4.1/pc depending on size and logo; valid 14 days"). Never send a full SKU price list to a lead you have not qualified.
