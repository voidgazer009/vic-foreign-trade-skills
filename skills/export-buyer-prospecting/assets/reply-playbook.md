# Reply playbook: answer within 4 working hours

Classify the reply, then use the matching move. Log it: `python3 scripts/pipeline.py log "<company>" replied|positive`.

| Reply type | Signal | Move |
|---|---|---|
| "Send catalogue / more info" | Mild interest | One page, 5–8 items matching *their* range, plus one question: target market, volume, or price level |
| "What's your price?" | Comparing | Price range with Incoterm (FOB/CIF/DDP), MOQ, lead time; ask target price and annual volume |
| "Send samples" | Strong | Confirm specs, who pays sample and courier, and their test timeline; log `sample` |
| "We have a supplier" | Polite no | "What would you improve with your current supplier?" Offer a side-by-side sample |
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
