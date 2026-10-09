#!/usr/bin/env bash
# Prints which official Claude Code docs pages changed since the last --update run,
# with a short line diff of each. Read-only except for the local cache in reports/
# (gitignored), and only when --update is passed. Needs curl. Works on macOS bash and
# Git Bash on Windows.
set -eu

repo="$(cd "$(dirname "$0")/.." && pwd)"
cache="$repo/reports/docs-cache"
pages="best-practices memory sub-agents permissions costs model-config hooks-guide settings"
update=0
[ "${1:-}" = "--update" ] && update=1

command -v curl >/dev/null 2>&1 || { echo "curl not found" >&2; exit 2; }
mkdir -p "$cache"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

for p in $pages; do
  url="https://code.claude.com/docs/en/$p.md"
  if ! curl -fsSL -m 30 "$url" -o "$tmp" 2>/dev/null || [ ! -s "$tmp" ]; then
    echo "FETCH-FAIL $p ($url)"
    continue
  fi
  old="$cache/$p.md"
  if [ ! -f "$old" ]; then
    echo "NEW      $p ($(wc -c < "$tmp" | tr -d ' ') bytes, baseline, no diff)"
  elif cmp -s "$old" "$tmp"; then
    echo "SAME     $p"
  else
    echo "CHANGED  $p ($url)"
    diff "$old" "$tmp" | grep '^[<>]' | head -60 | sed 's/^/    /' | cut -c1-240
    echo "    (diff truncated to 60 lines)"
  fi
  [ "$update" -eq 1 ] && cp "$tmp" "$old"
done
exit 0
