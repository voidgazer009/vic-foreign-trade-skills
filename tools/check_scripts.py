#!/usr/bin/env python3
"""Run a skill's script regression checks (evals/checks.json).
Usage: python3 check_scripts.py <skill_dir>   exit 0 = all pass"""
import json, os, pathlib, subprocess, sys
d = pathlib.Path(sys.argv[1]).resolve()
f = d / "evals" / "checks.json"
if not f.exists():
    print("no evals/checks.json: add script regression checks"); sys.exit(1)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
bad = 0
for c in json.loads(f.read_text(encoding="utf-8"))["checks"]:
    r = subprocess.run(c["cmd"], shell=True, cwd=d, capture_output=True, text=True, env=env, timeout=120)
    out = r.stdout + r.stderr
    errs = []
    if c.get("expect_exit") is not None and r.returncode != c["expect_exit"]:
        errs.append(f"exit {r.returncode} != {c['expect_exit']}")
    errs += [f"missing '{s}'" for s in c.get("expect", []) if s not in out]
    errs += [f"unexpected '{s}'" for s in c.get("reject", []) if s in out]
    print(("✓ " if not errs else "✗ ") + c["name"] + ("" if not errs else ": " + "; ".join(errs)))
    bad += bool(errs)
print(f"脚本回归 {'全部通过' if not bad else f'{bad} 项失败'}")
sys.exit(1 if bad else 0)
