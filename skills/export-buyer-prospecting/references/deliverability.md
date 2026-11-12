# Deliverability: get into the inbox before you rewrite the copy

Read this when replies are under 1%, emails bounce, the user's mailbox got limited, or before a new domain sends its first cold email.

## Diagnose first: which "no reply" is it?
| Symptom | Likely cause | Fix |
|---|---|---|
| Bounce messages come back | Dead addresses or domain auth failure | Read the bounce code; clean the list; `check_domain.py leads` |
| No bounce, near-zero replies | Landing in spam | `check_domain.py sender`, warm up, cut volume |
| Buyer says "never got it" | Spam folder | Send a test to your own Gmail and Outlook; check headers for spf=pass dkim=pass dmarc=pass |
| Delivered, read, no reply | Targeting or copy | references/outreach-playbook.md |

## Setup (once)
1. **Never cold-email from QQ, 163, Gmail or other free mailboxes.** Their reputation is shared and not yours.
2. **Use a separate outreach domain** (e.g. `getbrand.com`, or a subdomain) so a reputation hit never puts quotes, PIs and payment mails to old customers in spam.
3. **SPF**: exactly one TXT record, ≤ 10 DNS lookups including nested includes, ends in `~all` or `-all`.
4. **DKIM**: enable signing in the mail provider, publish the key, 2048-bit where offered.
5. **DMARC**: start `v=DMARC1; p=none; rua=mailto:…`, move to `quarantine` once reports are clean.
6. Since February 2024 Gmail requires SPF or DKIM from every sender, and SPF + DKIM + DMARC, one-click unsubscribe and a spam rate under 0.3% from bulk senders (5,000+/day to Gmail). Yahoo and Microsoft apply similar rules.

Run: `python3 scripts/check_domain.py sender yourdomain.com` until it prints PASS.

## Warm-up for a new mailbox or domain (about 2–4 weeks)
| Days | Cold emails per mailbox per day | Notes |
|---|---|---|
| 1–3 | 5–10 | Mostly real conversations: colleagues, existing customers |
| 4–7 | 10–20 | Tier-A leads only |
| 8–14 | 20–30 | Watch bounces daily |
| 15+ | 30–50 max | Add mailboxes to grow, not volume per mailbox |

## Red lines (stop sending the same day)
- Hard bounce rate above 2% (some guides say 3%; use 2% to be safe)
- Spam complaints above 0.3%
- Sudden jump in volume (e.g. a trade-show list of thousands sent in one day)
- Same body sent to hundreds of people: vary the first line per lead

## If the domain is already burned
Pause cold sending 1–2 weeks, send only to people who reply to you, fix SPF/DKIM/DMARC, clean the list, restart at warm-up day 1.
