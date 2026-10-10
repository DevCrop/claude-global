#!/usr/bin/env bash
# PreToolUse hook (Bash): block git add/stage/commit/push when a secret-looking file would be staged, committed or pushed.
# Blocks with exit 2 + stderr (https://code.claude.com/docs/en/hooks). Internal errors fail open with a warning.
# Limit: it reads the command string. Not seen: aliases, scripts that call git, variables, xargs/find -exec, paths with spaces, brace expansion, eval.
# No timeout of its own: a huge repo can make `git status` slow (set a hook timeout in settings if that bites).
input="$(cat)"
command -v jq >/dev/null 2>&1 || { echo "secret-guard: jq not found, check skipped" >&2; exit 0; }
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"
cwd="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)"
[ -n "$cmd" ] || exit 0

# Fast path: no git word next to add/stage/commit/push means nothing to check.
printf '%s' "$cmd" | grep -Eq '(^|[^[:alnum:]_.-])git([^[:alnum:]_-]|$)' && printf '%s' "$cmd" | grep -Eq '(add|stage|commit|push)' || exit 0

is_secret() {
  b="$(basename "$1" | tr '[:upper:]' '[:lower:]')"
  case "$b" in
    *.example|*.sample|*.template|id_rsa*.pub) return 1 ;;
    .credentials*|.env|.env.*|.claude.json|history.jsonl|*.pem|id_rsa*) return 0 ;;
  esac
  return 1
}
hits=""
judge() { while IFS= read -r f; do [ -n "$f" ] && is_secret "$f" && hits="$hits $f"; done <<< "$1"; }
absdir() { (cd "$1" 2>/dev/null && cd "$2" 2>/dev/null && pwd); }

set -f
cur="${cwd:-.}"
# Quotes, parens, backticks and $ become spaces (so "bash -c 'git add -A'" and $(git add -A) are seen); ; | & split segments.
segs="$(printf '%s\n' "$cmd" | tr '"'"'"'()`$' '      ' | tr ';|&' '\n\n\n')"
while IFS= read -r seg; do
  # shellcheck disable=SC2086
  set -- $seg
  [ "$#" -gt 0 ] || continue
  if [ "$1" = cd ] && [ -n "${2:-}" ]; then d="${2/#\~/$HOME}"; n="$(absdir "$cur" "$d")"; [ -n "$n" ] && cur="$n"; continue; fi
  while [ "$#" -gt 0 ] && [ "${1##*/}" != git ]; do shift; done
  [ "$#" -gt 0 ] || continue
  shift; dir="$cur"
  while [ "$#" -gt 0 ]; do
    case "$1" in
      -C) d="${2/#\~/$HOME}"; n="$(absdir "$dir" "$d")"; [ -n "$n" ] && dir="$n"; shift 2 || shift ;;
      -c) shift 2 || shift ;;
      -*) shift ;;
      *) break ;;
    esac
  done
  verb="${1:-}"; [ "$#" -gt 0 ] && shift
  case "$verb" in add|stage|commit|push) ;; *) continue ;; esac
  git -C "$dir" rev-parse --git-dir >/dev/null 2>&1 || continue
  broad=0; paths=""; dd=0
  for t in "$@"; do
    # commit: words before -- are message text, not paths (staged files are judged from git instead)
    [ "$verb" = commit ] && [ "$dd" = 0 ] && case "$t" in --) dd=1; continue ;; -*) ;; *) continue ;; esac
    case "$t" in
      --all|--update|--force|--pathspec-from-file*) broad=1 ;;
      -*) case "$verb" in
            add|stage) printf '%s' "$t" | grep -Eq '^-[a-zA-Z]*[Aufp][a-zA-Z]*$' && broad=1 ;;
            commit) printf '%s' "$t" | grep -Eq '^-[a-zA-Z]*a[a-zA-Z]*$' && broad=1 ;;
          esac ;;
      .|./|:/|:/*|*[\*\?\[]*) broad=1 ;;
      *) paths="$paths $t"; [ -d "$dir/$t" ] && broad=1 ;;
    esac
  done
  for t in $paths; do is_secret "$t" && hits="$hits $t"; done
  case "$verb" in
    add|stage) [ "$broad" = 1 ] && judge "$(git -C "$dir" status --porcelain --untracked-files=all 2>/dev/null | cut -c4-)" ;;
    commit)
      judge "$(git -C "$dir" diff --cached --name-only 2>/dev/null)"
      [ "$broad" = 1 ] && judge "$(git -C "$dir" diff --name-only 2>/dev/null)" ;;
    push) judge "$(git -C "$dir" ls-files 2>/dev/null)" ;;
  esac
done <<< "$segs"

if [ -n "$hits" ]; then
  echo "secret-guard: blocked. Secret-looking files would be included:$hits" >&2
  echo "Remove them from the change or add them to .gitignore, then retry. *.example, *.sample, *.template are allowed." >&2
  exit 2
fi
exit 0
