# Vic Skills 审核机制 v1.0（2026-11-12）

每个 Skill 每次发布前，必须按顺序通过 7 道关卡（G1–G7）。全部通过才自动推送 GitHub；任何一关不过就修，最多修 3 轮，仍不过就不推送，并向 Vic 说明原因。Vic 已授权（2026-11-12）：通过审核的 Skill 无需再问，自动上传到他的 4 个 Skills 仓库。

## G1 结构规范（自动）
`python3 tools/audit.py <skill目录>` 必须 100% 通过。内容包括：官方 skills-ref 校验；frontmatter 只使用规范字段；name 与文件夹同名；description 40–1024 字符，并写明 Use when 和中文触发词；SKILL.md 少于 500 行；包含 Workflow、Example、Gotchas、Edge cases；scripts/references/assets 中每个文件都被 SKILL.md 引用，引用的文件都存在；脚本只用 Python 标准库并支持 `--help`；不出现特定厂商的工具名；没有 TODO 或 __pycache__。

## G2 脚本回归（自动）
`evals/checks.json` 中的每条检查都要通过（G1 会自动调用 `tools/check_scripts.py`）。每修一个 bug，就加一条检查来锁定，防止复发。

## G3 隐私与真实性（自动 + 人工）
- 自动：SKILL.md、references、assets 中不得出现真实邮箱或电话，只能使用 example 域名和 `{占位符}`。
- 人工：示例中不得编造发件人的公司、姓名、地址或资质；测试中找到的第三方公司不写进 Skill。

## G4 事实时效（自动 + 人工）
- 关税、费率、法规、平台规则这类会过期的数字，必须写明官方来源和 "Last verified YYYY-MM-DD"。超过 90 天，G1 判为不通过，需要重新核实。
- 发布前用 web_fetch 打开原始页面核对一遍，不能只看搜索摘要。

## G5 真实执行测试（子代理）
派测试代理，只给它 Skill 文件夹和 2–3 条 should_trigger=true 的用例（每轮轮换，并覆盖不同国家和渠道）。要求它只按 SKILL.md 完成真实任务（可联网），并报告卡住、绕路或出错的地方。
- 结果分级：Critical（会让用户亏钱、违法或出错）/ Major（流程走不通或结果明显变差）/ Minor。
- 发布条件：0 Critical、0 Major。Minor 写进 report 的待办。

## G6 独立专家评审（另一个子代理，不看测试结果）
评审代理扮演该领域的资深从业者（例如 15 年外贸业务经理），按下表各打 0–10 分，并对每个低于 8 分的项给出具体修改建议：
1. 正确性：事实、法规、计算没有错误
2. 专业深度：一线人员才知道的经验，而非泛泛之谈
3. 可执行性：新手照着做就能得到结果
4. 安全合规：反诈骗、隐私、各国法律
5. 触发准确：该触发时触发，不该触发时不触发
6. 简洁：没有多余内容，细节放在 references
- 发布条件：平均分不低于 8.5，且没有任何一项低于 7。

## G7 发布卫生（自动）
重新打包 `dist/<name>.zip`（zip 顶层为 `<name>/`）；写 `reports/<name>-<version>.md`（G1–G6 的结果）；CHANGELOG、README 版本表、ROADMAP 状态与实际一致；semver 版本号（修复用 patch，新增能力用 minor，重构用 major）；使用 voidgazer009 noreply 身份提交；`git push`、打 tag `<name>-v<version>`；最后用 GitHub API 确认文件已上线。

## 毕业（达标后才开始写下一个 Skill）
1. 发布后至少迭代 2 轮，跨越至少 2 个不同日期。
2. 每条 should_trigger=true 的用例都至少经过一次 G5 真实执行测试并通过。
3. 最近一轮 G5 没有 Critical 或 Major；G6 平均分不低于 9.0。
4. 同类对比：搜索 GitHub、skills.sh、agentskills 等平台上的同主题 Skill，把至少 5 个和本 Skill 逐项对比（覆盖面、脚本、专业深度、安全）。只有本 Skill 在多数项上领先时才算"超过 90% 同类"，对比结果写入 report。
5. 毕业后移入 STATE.md 的 Done 列表，按轮换规则（外贸 → 物流 → 一人公司 → 自媒体）开始下一个 Skill。之后每周仍做一次轻量维护：重新核实过期的事实，处理 GitHub issues。
