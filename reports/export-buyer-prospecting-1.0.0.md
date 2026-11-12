# Audit · export-buyer-prospecting 1.0.0 · 2026-11-12

```
通过 77 项, 未通过 0 项
```

## Script tests
```
Scored 8 leads: A=2 B=2 C=0 X=4
  A 100  Example Trading GmbH                     
  A  80  Maison Exemple SARL                      generic inbox
  B  77  Tiny Gifts LLC                           smaller than ICP: MOQ risk (capped at tier B); free webmail: verify it is the company
  B  65  Big Retail Inc                           larger than ICP: expect long vendor onboarding
  X   0  Example Logistik GmbH                    looks like forwarder/logistics, not a buyer
  X   0  BottleShop on Amazon                     marketplace page, not a company site
  X   0  Example Trading GmbH dup                 duplicate of row 2
  X   0  Moscow Import OOO                        country RU not in targets
Fewer than 5 tier-A leads: widen buyer types or neighbouring countries.

⚠ DE/AT: email marketing needs prior consent even B2B (UWG §7). Prefer LinkedIn/phone first, or keep this a strictly individual inquiry.
PASS
email-bad.txt: FIX 8 item(s)
```
