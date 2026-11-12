# Finding and verifying the decision-maker

Read this when a lead has only info@/sales@, no named contact, or before sending to a guessed address.

## Who decides, by company size
- **Under ~50 staff**: owner / managing director. In DE/AT the legal *Impressum* page names the Geschäftsführer.
- **50–500**: purchasing manager, head of buying, category manager.
- **500+ / chains**: category manager for your category; expect vendor registration, audits and long cycles.
- **Industrial and technical products** (machinery, components, electrical): a buying committee. The technical/engineering/quality manager approves the spec before purchasing compares price. Reach both, separately.

`python3 scripts/find_contacts.py roles --company "X" --country DE --industrial` prints the searches.

## Getting the address
1. Company website: team, about, Impressum, press, PDF catalogues (often list buyers).
2. Find **one real address** at the company (press contact, a PDF, a trade-show listing) to learn its pattern, then:
   `python3 scripts/find_contacts.py email --name "Jan Müller" --domain firm.de --known "a.schmidt@firm.de=Anna Schmidt"`
3. Pattern tools if the user has them: Hunter, Apollo, RocketReach, Snov (free tiers are small).
4. LinkedIn: connect first with a note (assets/linkedin-whatsapp-templates.md), ask for email only after they accept.

## Verify before sending
- `check_domain.py leads` removes domains with no mail server.
- For guessed mailboxes use a verifier the user trusts (NeverBounce, ZeroBounce, Hunter verify). Treat "catch-all" results as risky: send only to tier-A with a real hook.
- Never send to an unverified guess in bulk. Each hard bounce lowers domain reputation for everyone at the company sending mail.

## Gatekeeper route
If only info@ exists: write two lines asking who handles sourcing of {category}, name the reason, and ask for the right person. Referral replies convert better than cold.
