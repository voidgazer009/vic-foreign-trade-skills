# 外贸开发客户痛点调研 · 2026-11

Sources read: 雨果网 (cifnews), 福步外贸论坛, OKKI/小满, 图灵搜, KoneB2B, 光算科技, 协守外贸, 星谷云, 外贸邦, 博客园, Tendata, Bilvio, papaverAI, Belkins, Instantly/Woodpecker benchmarks, B2B Data Index (2025–2026).

| # | 痛点 Pain point | What people say | How export-buyer-prospecting 2.0 solves it |
|---|---|---|---|
| 1 | 不知道开发哪个市场 | "一个大洲全勾上，导出几千条，回音很少" | Step 0 market selection with Trade Map / Comtrade / ImportYeti scoring, pick 2–3 countries |
| 2 | 找到的公司不对口（零售、同行、货代） | "Google 来的客户真的是目标客户吗？" | ICP + `score_leads.py` tiers A/B/C/X, drops forwarders, marketplaces, duplicates, small-MOQ risk |
| 3 | 英文搜不到小进口商 | Buyers search in their own language | `build_queries.py` 16 languages, 33 countries, localized product names |
| 4 | 找不到决策人，只有 info@ | "70% 的邮箱是无效的——要么是 info@，要么已作废" | `find_contacts.py` buying-committee searches (purchasing + technical), email pattern inference from one known address, verification rules |
| 5 | 开发信进垃圾箱、邮箱被封 | "回复还没退信多"；QQ/163 发开发信落垃圾箱是常态 | `check_domain.py` SPF/DKIM/DMARC/MX checks, separate outreach domain, warm-up table, 2% bounce and 0.3% complaint red lines |
| 6 | 开发信像群发、自嗨，没人回 | "质量好、价格低、交期快… You said nothing" | Personal-fact first line, 4-touch sequence, `lint_outreach.py` 13 checks incl. Chinglish clichés |
| 7 | 领英加了好友不会聊 | "加了1000多个好友…收效甚微" | LinkedIn note / accept / value templates, `--channel linkedin` lint |
| 8 | 渠道用错（邮件 vs WhatsApp vs 电话） | "有些客户发邮件不看，打电话才有反应" | Channel-by-country matrix, WhatsApp opt-in rules and 24h window |
| 9 | 报价后客户消失，只会 "Any update?" | "80% 的客户在初次报价后一周内没有回复" | Quote-silence sequence day 2/7/14/21, each with new value |
| 10 | 回复了不知道怎么接 | 发目录？报价？ | Reply playbook: 8 reply types with the next move |
| 11 | 跟进全靠脑子记，客户丢失 | "回复消息散落在个人账号、邮箱和 WhatsApp" | `pipeline.py` CSV tracker: due actions, buyer local time, stale warm leads |
| 12 | 不知道问题出在哪一环 | 没回复 = 送达？名单？文案？ | `pipeline.py stats` funnel diagnosis after 30+ contacts |
| 13 | 文化差异 | "德国人要数据和认证，中东客户要尊重和人情" | Culture notes per region |
| 14 | 合规与骗子 | GDPR、德国 UWG、制裁；假买家 | Compliance guide, sanctions flags, fake-buyer signals |
| 15 | SOHO 一个人做不过来 | "一个客户平均 15 分钟" | Scripts automate queries, scoring, guessing, linting and scheduling; agent does the research |
