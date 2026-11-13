# Payment terms and fraud: from first quote to cash in the bank

The money is lost at two moments: when terms slide toward credit, and when bank details "change by email". Both are preventable with a few fixed rules.

## Payment-term risk ladder (safest first)
| Term | Who controls the goods | Typical trap | Before you move to this step |
|---|---|---|---|
| 100% T/T in advance | You | none | light checks (`verify_buyer.py --terms tt100`) |
| 30% deposit, 70% **before shipment** | You | buyer delays balance, goods wait in your warehouse | agree storage cost after N days |
| 30% deposit, 70% **against copy of B/L** | Buyer (goods have sailed) | buyer stops paying once the ship has left; buyer-nominated forwarder releases the cargo on its own house B/L | registry + credit check; your forwarder or the carrier's master B/L; keep original B/L; no telex release or sea waybill before payment |
| L/C at sight | Bank | discrepancies (wrong dates, "Incoterms 2020" missing, spelling) | have your bank review the L/C wording before accepting |
| D/P | Bank, until paid | buyer refuses documents; goods stuck at destination port, auctioned | credit report, credit insurance, **your** forwarder, never a buyer-nominated one |
| O/A (open account) | Buyer | default | full checks, credit-insurance limit ≥ exposure, start small |

Credit insurance (e.g. Sinosure) caps cover per buyer. A small-company policy can cap one buyer far below the order value, so compare limit vs exposure before shipping.

## When the buyer asks to change terms (log it: `pipeline.py log "<co>" terms`)
The first time a buyer asks orally to change the payment method is the first warning sign.
1. Do not agree in the chat or on a call. Ask for the request in writing and the reason.
2. Re-run `verify_buyer.py --terms <new term>` and get a credit report.
3. Check the credit-insurance limit against the new exposure.
4. Counter-offer instead of yes/no: split shipment (first lot on old terms), L/C, or a higher deposit.
5. Amend the contract in writing before shipping.

Reply template:
"Thanks for explaining. For this order we keep the agreed {30% deposit / 70% before shipment}. To help your cash flow we can {split into two shipments / accept an L/C at sight / hold the goods free for 14 days}. Which works better for you?"

## Email hacking (BEC): bank details that "changed"
Typical pattern: a mailbox is hacked, the hacker watches the thread, then sends "our bank account changed" from the real or a look-alike domain (examp1e.com, acme.1td vs acme.ltd, an extra hyphen) and deletes the traces. Losses are often the whole balance payment, and mediators usually split the loss.
- Put the clause in every PI: "Our bank details are fixed in this PI and will never change by email."
- Any new bank detail, in either direction: call a phone number you already had (not one in the new email).
- Before paying, shipping or releasing documents, run `scripts/check_lookalike.py --pipeline pipeline.csv --sender <address>` or `--thread thread.txt`.
- Mailbox hygiene: two-factor login, review auto-forward rules monthly, login alerts on.
- Buyer's bank country differs from the buyer's country, or a third party pays: stop and verify (also a money-laundering and sanctions red flag).
- Hackers also write to YOUR buyer as you ("our new account"). Run `check_lookalike.py --own <your domain>` on threads, and tell key buyers in writing that your bank details never change by email.
- `check_lookalike.py` also stops on any thread text that asks to change bank or payment details, even from a trusted domain, because a hacked real mailbox looks identical.

## FOB with a buyer-nominated forwarder
Common under FOB: the buyer names the forwarder. The forwarder works for the buyer and can release the cargo against its own house B/L while your balance is unpaid. Before open terms or B/L-copy terms: ask for the carrier's master B/L consigned "to order" or to your bank, or move to CIF/CFR with your own forwarder, or keep the payment before shipment.

## Fake-buyer signals (also in SKILL.md Gotchas)
Free webmail with a big urgent order; free samples plus courier to a third country; "registration", "certificate" or "inspection" fees; price accepted at once well above market with open account; a real company's name used by someone else (check the registry's business activity fits the product).
