# Qualification rubric (how score_leads.py scores)

Score = weighted sum, normalised to 0–100. Weights live in `icp.json` → `weights` so the user can tune them.

| Factor | Default weight | Full points when | Partial |
|---|---|---|---|
| buyer_type | 30 | Importer or distributor | Scaled by `buyer_types` points: wholesaler 24/30, brand owner 22/30, retailer 15/30, e-commerce 8/30 |
| products_match | 25 | `yes`: sells the same or adjacent product now | `partial` = 50% |
| company_size | 15 | Employees within `employees_min`–`employees_max` | Unknown 40%, larger 50% (slow onboarding), smaller 20% (MOQ risk) |
| named_contact | 15 | Named person with a buying title (purchasing, sourcing, category, buyer, owner/founder/MD for SMBs; also Einkauf, achat, compras, acquisti, inkoop) | Named but other role 60% |
| personal_email | 10 | Named mailbox on company domain | Generic inbox (info@, sales@…) 30% |
| country_match | 5 | Country in `target_countries` | — |

Tiers (defaults, editable in `tier_thresholds`): **A ≥ 70**, **B ≥ 45**, **C < 45**. A lead smaller than `employees_min` is capped at tier B (MOQ risk); a free-webmail address earns 50% of the email points.

**Tier X (score 0)** regardless of points: duplicate website, forwarder/logistics name, marketplace URL instead of company site, matches `exclude_keywords`, or country outside targets.

Flags never change the score but tell you what to research next: `product fit unchecked`, `no named contact`, `sanctions screening required`, `free webmail: verify it is the company`.

## Tuning tips

- Selling small MOQ (under 500 pcs)? Raise `ecommerce_seller` to 20 and lower `employees_min` to 1.
- Selling to chains/tenders? Raise `retailer` to 28 and `employees_max` to 100000.
- Product is commodity (price-led)? Raise `products_match` weight; fit matters more than size.
