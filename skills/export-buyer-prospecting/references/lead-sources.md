# Lead sources, ranked by quality per hour

Use the first two for every market; add the rest when tier-A leads are fewer than 5.

| # | Source | Finds | How | Watch out |
|---|---|---|---|---|
| 1 | Google with local-language operators | Importers and distributors with their own sites | `scripts/build_queries.py` output | Page 2–5 of results is where small importers hide |
| 2 | Trade-show exhibitor lists | Active buyers and brands in the category | Search "{show} exhibitor list {year}"; the main shows per category: Ambiente / Tendence (home, gift, DE), Canton Fair buyer side, CES (electronics, US), Automechanika (auto parts), Interzoo (pet), Spoga+Gafa (garden), Hong Kong fairs (HKTDC) | Exhibitors are sellers too; keep brands and distributors, drop other factories |
| 3 | Customs / bill-of-lading data | Who actually imports the HS code, volume, current supplier | ImportYeti (US, free), Panjiva, ImportGenius, Volza, TradeAtlas (paid) | Consignee is often a forwarder; read the notify party; data covers sea freight mostly |
| 4 | LinkedIn | Named buyers: purchasing, category, sourcing managers | Google `site:linkedin.com/in` queries; Sales Navigator if the user has it | Connect with a note first, email second |
| 5 | Industry associations and chambers | Member directories of distributors | "{industry} association members {country}" | Directories are often outdated; verify the website is live |
| 6 | Marketplace storefronts | Brand owners selling the product | Amazon brand → brand site → contact | Most are small; check reviews count as a volume proxy |
| 7 | B2B platforms (Alibaba RFQ, Global Sources, Europages, Kompass, Thomasnet) | Buyers posting demand; company directories | Platform search by HS or product | RFQ buyers get 20+ quotes in hours; reply fast and specific |
| 8 | Competitor references | Who buys from competitors | Competitor "where to buy", "partners", "dealers" pages | Distributors listed there may be exclusive |

## Signs a lead is real and active

- Website updated in the last 12 months (news, catalogue year, copyright)
- Sells the same or an adjacent product today
- Has a "Brands"/"Suppliers"/"Partners" page listing foreign brands
- Job posting for a buyer, category manager, or importer role
- Appears in customs data in the last 12 months

## Signs to drop

- Only a marketplace storefront, no company site
- Domain parked or site down
- Name or site contains forwarding/logistics terms (see `forwarder_markers` in the keyword file)
- They manufacture the same product themselves (competitor, not buyer) unless they are a brand outsourcing OEM
