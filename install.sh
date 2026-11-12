#!/usr/bin/env bash
# Install Vic skills for every major agent.
# Usage: ./install.sh <skill-name|all> [--project]
#   default: personal install to ~/.claude/skills (Claude Code) and ~/.agents/skills (Codex, Cursor, Copilot, Gemini CLI, OpenCode)
#   --project: install into ./.claude/skills and ./.agents/skills of the current folder
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
name="${1:-}"; scope="${2:-}"
if [ -z "$name" ]; then echo "Usage: ./install.sh <skill-name|all> [--project]"; ls "$here/skills"; exit 1; fi
if [ "$scope" = "--project" ]; then base="$PWD"; else base="$HOME"; fi
targets=("$base/.claude/skills" "$base/.agents/skills")
if [ "$name" = "all" ]; then names=$(ls "$here/skills"); else names="$name"; fi
for n in $names; do
  [ -f "$here/skills/$n/SKILL.md" ] || { echo "No skill named $n"; exit 1; }
  for t in "${targets[@]}"; do mkdir -p "$t"; rm -rf "$t/$n"; cp -R "$here/skills/$n" "$t/$n"; echo "Installed $n -> $t/$n"; done
done
