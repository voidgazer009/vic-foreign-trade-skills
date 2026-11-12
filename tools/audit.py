#!/usr/bin/env python3
"""Vic Skill auditor: official skills-ref validation + Vic house standard (agent-agnostic).
Usage: python3 audit.py <skill_dir>"""
import sys, os, re, json, subprocess, py_compile, pathlib
d = pathlib.Path(sys.argv[1]).resolve(); errs, ok = [], []
def chk(c, msg): (ok if c else errs).append(msg)
r = subprocess.run([os.path.expanduser("~/.local/bin/skills-ref"), "validate", str(d)], capture_output=True, text=True)
chk(r.returncode == 0, f"skills-ref 官方校验: {(r.stdout+r.stderr).strip()[:300]}")
sk = d / "SKILL.md"; chk(sk.exists(), "SKILL.md 存在")
txt = sk.read_text(encoding="utf-8") if sk.exists() else ""
m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
chk(bool(m), "YAML frontmatter 格式正确")
if m:
    fm, body = m.group(1), m.group(2)
    keys = re.findall(r"^([A-Za-z-]+):", fm, re.M)
    allowed = {"name","description","license","compatibility","metadata","allowed-tools"}
    chk(set(keys) <= allowed, f"只用规范允许的 6 个字段 (实际: {keys})")
    nm = re.search(r"^name:\s*(\S+)", fm, re.M); nm = nm.group(1) if nm else ""
    chk(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nm or "X") is not None and len(nm) <= 64, "name 合法")
    chk(nm == d.name, "name 与文件夹同名")
    ds = re.search(r"^description:\s*(.+?)(?=^\S|\Z)", fm, re.M | re.S); ds = ds.group(1).strip() if ds else ""
    chk(40 <= len(ds) <= 1024, f"description 40-1024 字符 (实际 {len(ds)})")
    chk(bool(re.search(r"(Use when|使用场景|当用户|when the user)", ds, re.I)), "description 写明何时使用")
    chk("license:" in fm, "有 license 字段")
    chk(len(txt.splitlines()) < 500, "SKILL.md < 500 行")
    for sec in ["## ", "示例"]:
        pass
    chk(len(re.findall(r"^## ", body, re.M)) >= 3, "正文至少 3 个二级标题（步骤/示例/边界情况）")
    chk(bool(re.search(r"^## (示例|Examples?)", body, re.M)), "正文含示例章节")
    chk(bool(re.search(r"^## (边界情况|Edge cases)", body, re.M | re.I)), "正文含边界情况章节")
for sub in ["scripts", "references", "assets", "evals"]:
    p = d / sub; files = [f for f in p.rglob("*") if f.is_file() and f.name != ".gitkeep"] if p.exists() else []
    chk(len(files) > 0, f"{sub}/ 存在且有真实文件")
chk((d/"LICENSE.txt").exists(), "LICENSE.txt 存在")
# 引用完整：SKILL.md 中引用的相对路径都存在；scripts/references/assets 下文件都被引用
refs = set(re.findall(r"((?:scripts|references|assets)/[\w./-]+)", txt))
for rf in refs: chk((d/rf.rstrip('.')).exists(), f"引用文件存在: {rf}")
chk(not list(d.rglob("__pycache__")) and not list(d.rglob(".DS_Store")), "无 __pycache__ / .DS_Store 垃圾文件")
for sub in ["scripts", "references", "assets"]:
    for f in (d/sub).rglob("*") if (d/sub).exists() else []:
        if f.is_file() and "__pycache__" not in f.parts: rel = f.relative_to(d).as_posix(); chk(rel in txt, f"文件被 SKILL.md 引用: {rel}")
for f in (d/"scripts").rglob("*") if (d/"scripts").exists() else []:
    if f.suffix == ".py":
        try: compile(f.read_text(encoding="utf-8"), str(f), "exec"); chk(True, f"语法 OK {f.name}")
        except Exception as e: chk(False, f"语法错误 {f.name}: {e}")
    if f.suffix == ".sh": chk(subprocess.run(["bash","-n",str(f)]).returncode == 0, f"语法 OK {f.name}")
# Agent-agnostic: scripts use stdlib only and answer --help; no vendor-only tool names
std = set(sys.stdlib_module_names)
for f in (d/"scripts").rglob("*.py") if (d/"scripts").exists() else []:
    src = f.read_text(encoding="utf-8")
    mods = {m.split(".")[0] for m in re.findall(r"^\s*(?:import|from)\s+([\w\.]+)", src, re.M)}
    ext = sorted(m for m in mods - std if m != "__future__")
    chk(not ext, f"{f.name} uses stdlib only" + (f" (external: {ext})" if ext else ""))
    rr = subprocess.run([sys.executable, "-B", str(f), "--help"], capture_output=True, text=True, cwd=d)
    chk(rr.returncode == 0, f"{f.name} --help runs")
vendor = re.findall(r"\b(Bash tool|Read tool|Write tool|Edit tool|str_replace_editor|computer_use|TodoWrite)\b", txt)
chk(not vendor, "SKILL.md names no vendor-only tools" + (f" ({vendor})" if vendor else ""))
chk(bool(re.search(r"^compatibility:", txt, re.M)), "has compatibility field (states runtime needs)")
chk(bool(re.search(r"^## Gotchas", txt, re.M)), "has a Gotchas section")
ev = d/"evals"/"evals.json"
try:
    e = json.loads(ev.read_text()); items = e.get("evals", e) if isinstance(e, dict) else e
    chk(isinstance(items, list) and len(items) >= 3, "evals.json 至少 3 个测试用例")
    chk(any(i.get("should_trigger") is False for i in items), "evals 含不应触发的用例")
    for i in items:
        for fp in i.get("files", []):
            chk((d/fp).exists(), f"eval 文件存在: {fp}")
except Exception as x: chk(False, f"evals.json 可解析: {x}")
for f in d.rglob("*"):
    if f.is_file() and f.suffix in {".md",".py",".sh",".json",".txt",".csv",".yaml",".yml"}:
        chk(not re.search(r"(TODO|TBD|lorem ipsum|待补充)", f.read_text(errors="ignore"), re.I), f"无占位内容: {f.relative_to(d)}")
print(f"通过 {len(ok)} 项, 未通过 {len(errs)} 项")
for x in errs: print("  ✗", x)
sys.exit(1 if errs else 0)
