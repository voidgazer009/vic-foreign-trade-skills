# Trade-show follow-up (Canton Fair, Ambiente, NHS...)

Buyers shortlist within 48 hours of a fair and keep 2–3 suppliers per category. "Nice to meet you, please find our catalogue" lands among two hundred identical notes. Import the cards first: `python3 scripts/pipeline.py import-show cards.csv --show "{fair}"` (A due in 48 h, B in 3 days, C quarterly).

## At the booth: write these on the back of each card
SKU or spec discussed · their market and channel · quantity and timing · what you promised (quote, sample, video) · Incoterm and MOQ they mentioned · grade A/B/C.

## Email 1 (A: within 48 h; B: within 3 days): the 4 booth facts
```
Subject: {Fair} booth {no.}: {item} for {their company}

Hi {first name},

Good to meet you at {fair}, booth {no.}, on {day}. You looked at {SKU/spec} for {their market/channel}, around {quantity} for {season}.

As promised, here is {the quote / sample plan / the video of X}: {one-line key facts: price band, MOQ, lead time}.

Shall I {send the sample next week / book a 15-minute call on Tuesday}?

{signature with address}
```

## Email 2 (day 5–7): one new fact
A detail they cared about: test report, a packaging mock-up, a freight estimate to their port. One question.

## Then
No reply after two touches → stage `nurture`, note "show, re-touch {month}". Re-touch before the next fair: "Will you visit {next fair}? We'll have {new item} at booth {no.}."
