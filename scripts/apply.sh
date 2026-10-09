#!/usr/bin/env bash
# Copy the managed files from claude/ into the Claude config directory.
# Works on macOS bash and Git Bash on Windows. Never touches credentials,
# projects/, sessions/, plugins/ or any other runtime data.
set -eu

repo="$(cd "$(dirname "$0")/.." && pwd)"
src="$repo/claude"
dest="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
stamp="$(date +%Y%m%d-%H%M%S)"
backup="$dest-backup-$stamp"

# Files and directories copied. scheduled-tasks/ is excluded: it is created in the app.
# Skills are listed one by one: other skills (for example archify) live in the same directory.
items="CLAUDE.md RTK.md settings.json agents routines skills/orchestrate skills/project-setup"

mkdir -p "$dest"

for item in $items; do
  if [ -e "$dest/$item" ]; then
    mkdir -p "$backup/$(dirname "$item")"
    cp -R "$dest/$item" "$backup/$(dirname "$item")/"
  fi
done
[ -d "$backup" ] && echo "backup: $backup"

for item in $items; do
  if [ -d "$src/$item" ]; then
    mkdir -p "$dest/$item"
    cp -R "$src/$item/." "$dest/$item/"
  else
    cp "$src/$item" "$dest/$item"
  fi
  echo "applied: $item"
done

if ! command -v rtk >/dev/null 2>&1; then
  echo "warning: rtk not found in PATH. settings.json hooks it; Bash still runs, RTK filtering is off." >&2
  echo "  macOS: brew install rtk    Windows: winget install rtk-ai.rtk" >&2
fi
