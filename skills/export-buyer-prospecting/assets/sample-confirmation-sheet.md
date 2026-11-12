# Sample confirmation sheet (send with every sample, bilingual where useful)

Samples that arrive without an agreed spec get "not what we expected" and no order. Fill this in with the buyer before you ship.

| Field | Agreed |
|---|---|
| Buyer / contact | {company, name} |
| Item and model | {model} |
| Material | {e.g. 18/8 (304) stainless, PP lid} |
| 3 critical dimensions + tolerance | {e.g. height 255 mm ±1, Ø 73 mm ±0.5, capacity 500 ml ±10} |
| Finish / colour | {powder coat, Pantone} |
| Logo / label / packaging | {method, position, box} |
| Tests the buyer will run | {e.g. LFGB food contact, 12 h heat retention} |
| Acceptance: who decides, by when | {name, date} |
| Quantity sent (+ spares) | {n + 1} |
| Sample fee and credit | {USD x, credited against first order ≥ n pcs} |
| Courier, who pays, declared value | {DHL acct #, real value} |

Notes:
- "This sample is for evaluation. It becomes the production standard only when both sides sign it."
- Declare the real value. Zero-value declarations get held at customs; to the US, samples pay duty because de minimis is suspended.
- Log it: `python3 scripts/pipeline.py log "{company}" sample` → reminders on day 3 (arrived?), 7 (test result?), 21 (proposal or archive).
