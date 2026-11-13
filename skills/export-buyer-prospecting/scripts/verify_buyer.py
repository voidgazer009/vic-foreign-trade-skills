#!/usr/bin/env python3
"""Check that a buyer is a real, matching company before samples, credit terms or big quotes.

Usage:
  python3 scripts/verify_buyer.py --company "Example Trading GmbH" --country DE [--domain example-trading.de]
         [--vat DE123456789] [--terms tt100|tt30-70|lc|dp|bl-copy|oa] [--offline]

Does, with no API key:
  - EU VAT number check via the official VIES REST service (EU member states; not the UK)
  - domain age via RDAP (rdap.org); a domain under 1 year old with a big order is a red flag
  - name vs domain match
  - prints the official registry / directory search links for the country to open by hand
  - prints how deep to check for the payment terms on the table (deeper as risk moves to you)
OpenCorporates is linked, never scraped (its free use is personal only). Python 3.9+ standard library only.
"""
import argparse, json, re, sys, urllib.parse, urllib.request
from datetime import date

EU = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "GR", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK", "XI"}
REG = {
    "GB": "https://find-and-update.company-information.service.gov.uk/search?q={q}",
    "UK": "https://find-and-update.company-information.service.gov.uk/search?q={q}",
    "FR": "https://annuaire-entreprises.data.gouv.fr/rechercher?terme={q}",
    "NL": "https://www.kvk.nl/zoeken/?source=all&q={q}",
    "DE": "https://www.handelsregister.de/ (Normale Suche: firm name) and https://www.northdata.de/{q}",
    "AT": "https://www.firmenbuchgrundbuch.at/ and https://www.northdata.com/{q}",
    "CH": "https://www.zefix.ch/en/search/entity/list?name={q}",
    "AU": "https://abr.business.gov.au/Search/ResultsActive?SearchText={q}",
    "NZ": "https://app.companiesoffice.govt.nz/co/search?q={q}",
    "CA": "https://ised-isde.canada.ca/cc/lgcy/fdrlCrpSrch.html (federal) plus the province registry",
    "US": "the Secretary of State business search of the buyer's state (e.g. NY: https://apps.dos.ny.gov/publicInquiry/ , CA: https://bizfileonline.sos.ca.gov/search/business , TX: https://comptroller.texas.gov/taxes/franchise/ ), and https://www.sec.gov/cgi-bin/browse-edgar?company={q}&owner=include&action=getcompany for listed firms",
    "IE": "https://core.cro.ie/ (company search)",
    "SG": "https://www.bizfile.gov.sg/ (entity search)",
    "BR": "the CNPJ card at https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp (ask for the CNPJ; check status 'ATIVA', activity code (CNAE) and partners (QSA))",
    "MX": "ask for the RFC and the Constancia de Situación Fiscal; check the RFC with SAT and that the name and address match",
}
IMPORT_RIGHT = {  # can this company legally import, and how much?
    "BR": "Brazil: an importer needs Siscomex habilitação (RADAR). 'Limitada' caps imports at USD 50,000 or 150,000 per 6 months; "
          "ask which modality they hold. An order above their cap needs a higher modality first (Receita Federal, verified 2026-11-13).",
    "MX": "Mexico: the importer must be registered in SAT's Padrón de Importadores (and the Padrón Sectorial for sensitive goods such as "
          "steel, textiles, footwear). Ask for proof before production; unregistered buyers often route through an 'importadora' you never met.",
}
BR_CAPS = (50000, 150000)
DEPTH = {
    "tt100": "light: website, domain age, registry entry, address on a map",
    "tt30-70": "light + a call to the company's public phone number; balance must be paid before shipment",
    "lc": "check the issuing bank too (known bank, SWIFT matches); have a bank review the L/C wording",
    "dp": "registry + credit report (Sinosure / credit agency) + you control the forwarder; never a buyer-nominated forwarder under D/P",
    "bl-copy": "registry + credit report + credit insurance limit ≥ exposure; book with YOUR forwarder or the carrier (a buyer-nominated "
               "forwarder's house B/L lets the cargo be released without your original); keep the original B/L and allow no telex release "
               "or sea waybill until the balance is in your bank",
    "oa": "full: registry, credit report, trade references, credit insurance limit ≥ order value, start with a small order",
}


def get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "export-buyer-prospecting/3.1", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--company", required=True)
    ap.add_argument("--country", required=True, help="ISO code, e.g. DE, GB, US")
    ap.add_argument("--domain", default="")
    ap.add_argument("--vat", default="", help="EU VAT number with country prefix, e.g. DE123456789")
    ap.add_argument("--terms", choices=list(DEPTH), help="payment terms under discussion")
    ap.add_argument("--offline", action="store_true", help="skip network checks, print links only")
    ap.add_argument("--order-usd", type=float, default=0, help="value of the order under discussion, to compare with import caps (BR)")
    a = ap.parse_args()
    cc = a.country.upper()
    q = urllib.parse.quote(a.company)
    red = 0
    print(f"Buyer check: {a.company} ({cc})")

    if a.vat:
        v = re.sub(r"[\s.-]", "", a.vat.upper())
        ms, num = v[:2], v[2:]
        if ms == "GR":
            ms = "EL"
        if ms not in EU:
            print(f"  ⚠ VAT {v}: VIES only covers EU states (not {ms}). Use the national registry instead.")
        elif a.offline:
            print(f"  · VAT: check https://ec.europa.eu/taxation_customs/vies/ for {v}")
        else:
            try:
                d = get(f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{ms}/vat/{num}")
                if d.get("isValid"):
                    nm = (d.get("name") or "").strip()
                    print(f"  ✓ VAT {v} valid in VIES" + (f": {nm}" if nm and nm != "---" else " (name not disclosed by this country)"))
                    if nm and nm != "---":
                        core = re.sub(r"\b(gmbh|ltd|llc|sarl|srl|bv|sa|ag|kg|ohg|ug|limited)\b|[^a-z0-9]", "", a.company.lower())[:8]
                        if core and core not in re.sub(r"[^a-z0-9]", "", nm.lower()):
                            red += 1
                            print(f"  ✗ VIES name '{nm}' does not match '{a.company}'")
                else:
                    red += 1
                    print(f"  ✗ VAT {v} NOT valid in VIES ({d.get('userError', 'invalid')})")
            except Exception as e:
                print(f"  ⚠ VIES unreachable ({e.__class__.__name__}); check by hand at https://ec.europa.eu/taxation_customs/vies/")
    elif cc in EU:
        print("  · Ask for the EU VAT number (normal B2B practice) and re-run with --vat")

    if a.domain:
        dom = re.sub(r"^(https?://)?(www\.)?", "", a.domain.lower().split("@")[-1].strip()).split("/")[0]
        base = re.sub(r"[^a-z0-9]", "", dom.split(".")[0])
        core = re.sub(r"\b(gmbh|ltd|llc|inc|sarl|srl|bv|sa|ag|limited|company|trading|group|co)\b|[^a-z0-9]", "", a.company.lower())
        if core and base not in core and core[:5] not in base:
            print(f"  ⚠ domain '{dom}' does not obviously match the company name; confirm it on the registry entry or their website")
        free = dom in {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "qq.com", "163.com", "gmx.de", "web.de", "mail.com"}
        if free:
            red += 1
            print(f"  ✗ {dom} is free webmail, not a company domain: its age says nothing. Ask for the company website and a company address")
        if not a.offline and not free:
            try:
                d = get(f"https://rdap.org/domain/{dom}")
                reg = next((e.get("eventDate", "") for e in d.get("events", []) if e.get("eventAction") == "registration"), "")
                m = re.search(r"(\d{4})-(\d{2})-(\d{2})", reg)
                if m:
                    born = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    age = (date.today() - born).days / 365.25
                    if age < 1:
                        red += 1
                        print(f"  ✗ domain registered {born} (under 1 year old): high risk for credit terms or big urgent orders")
                    else:
                        print(f"  ✓ domain registered {born} ({age:.0f} years)")
                else:
                    print("  ⚠ RDAP gave no registration date (some ccTLDs such as .de hide it); check the registry entry instead")
            except Exception as e:
                print(f"  ⚠ RDAP lookup failed for {dom} ({e.__class__.__name__}); some ccTLDs have no public RDAP")

    print("  Open by hand:")
    print("   - registry: " + REG.get(cc, "the national company registry of " + cc).format(q=q))
    print(f"   - https://opencorporates.com/companies?q={q} (personal use; link only)")
    print(f"   - https://www.google.com/maps/search/?api=1&query={q} (real premises? warehouse or a flat?)")
    if cc == "US":
        print(f"   - https://www.importyeti.com/ search '{a.company}' (US import records: do they really import your product? who supplies them?)")
    print("  Compare: registered name, address and business activity vs what they told you; does the activity fit your product?")
    if cc in IMPORT_RIGHT:
        print("  Import right: " + IMPORT_RIGHT[cc])
        if cc == "BR" and a.order_usd > BR_CAPS[0]:
            print(f"  ⚠ order USD {a.order_usd:,.0f} is above the USD 50,000 'Limitada' cap" + (" and the USD 150,000 cap" if a.order_usd > BR_CAPS[1] else "")
                  + ": confirm the buyer's habilitação modality (or a trading company importing for them) before production")
    if a.terms in ("bl-copy", "dp", "oa"):
        print("  Payer check: the money must come from the buyer's own company account in the buyer's country. A third-party payer or another country = stop and verify.")
    if a.terms:
        print(f"  Depth for {a.terms}: {DEPTH[a.terms]}")
    print("RED FLAGS: " + str(red) if red else "No automatic red flag. Finish the manual checks above before credit terms.")
    sys.exit(1 if red else 0)


if __name__ == "__main__":
    main()
