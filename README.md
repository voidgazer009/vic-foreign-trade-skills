# Vic · Foreign Trade Agent Skills

**外贸全流程 Agent Skills 合集** — open-source skills that turn any AI agent into a senior export sales and trade specialist. Works with **Claude (Code / claude.ai / API), OpenAI Codex, Cursor, GitHub Copilot, Gemini CLI, OpenCode** and any agent that follows the [Agent Skills open standard](https://agentskills.io/specification).

Every skill is audited before release: official `skills-ref validate` + the Vic house standard (`tools/audit.py`): complete folder structure, stdlib-only scripts, gotchas, examples, evals.

## Skills

| Skill | 作用 | Version | Status |
|---|---|---|---|
| [export-buyer-prospecting](skills/export-buyer-prospecting) | 开发海外客户全流程：选市场 → 本地语言找买家 → 评分剔除货代 → 找决策人邮箱 → 邮箱送达体检 → 开发信/领英/WhatsApp 话术检查 → 回复与报价后跟进 → 跟进看板。解决 15 个外贸人真实痛点（[调研](docs/pain-points-research.md)） | 2.0.0 | ✅ Released |

Coming next, one at a time, each polished before the next: see [ROADMAP.md](ROADMAP.md).

## Install

**One command (Claude Code + Codex + Cursor + Copilot + Gemini CLI + OpenCode):**
```bash
git clone https://github.com/voidgazer009/vic-foreign-trade-skills.git
cd vic-foreign-trade-skills && ./install.sh export-buyer-prospecting
```
Copies the skill into `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex, Cursor, Copilot, Gemini CLI, OpenCode). Add `--project` to install into the current repo instead.

**claude.ai / Claude desktop:** download [`dist/export-buyer-prospecting.zip`](dist/export-buyer-prospecting.zip) → Settings → Capabilities → Skills → Upload.

**Any other agent:** copy `skills/<name>/` into the folder your agent scans for skills.

## Skill structure (Vic standard)

```
skill-name/
├── SKILL.md          # frontmatter (name, description, license, compatibility, metadata) + instructions
├── LICENSE.txt
├── scripts/          # Python 3 standard library only — runs anywhere
├── references/       # loaded on demand
├── assets/           # templates, data
└── evals/            # evals.json + test files (incl. should-not-trigger cases)
```

## 中文说明

这是 Vic 外贸技能合集。每个技能都是一个标准文件夹，装进任意支持 Agent Skills 的 AI 工具后，直接对它说"帮我开发德国客户"就会自动调用。脚本只用 Python 标准库，无需安装依赖。

## License

MIT © Vic (voidgazer009). Contributions and issues welcome.
