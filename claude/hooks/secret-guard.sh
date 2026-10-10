#!/usr/bin/env bash
# PreToolUse hook (Bash): block git add/commit/push when a secret-looking file would be staged, committed or pushed.
# Blocks with exit 2 + stderr (https://code.claude.com/docs/en/hooks). Internal errors fail open with a warning.
# Limit: it reads the command string, so aliases, scripts that call git, and eval are not seen.
input="$(cat)"
command -v jq >/dev/null 2>&1 || { echo "secret-guard: jq not found, check skipped" >&2; exit 0; }
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"
cwd="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)"
[ -n "$cmd" ] || exit 0

# Fast path: anything that is not git add/commit/push is allowed at once.
re='(^|[;&|[:space:]])git([[:space:]]+(-C[[:space:]]+[^[:space:]]+|-c[[:space:]]+[^[:space:]]+|--[a-z-]+=[^[:space:]]+))*[[:space:]]+(add|commit|push)([[:space:]]|$|[;&|])'
printf '%s' "$cmd" | grep -Eq "$re" || exit 0

is_secret() {
  case "$(basename "$1")" in
    .env.example|.env.sample|.env.template) return 1 ;;
    .credentials*|.env|.env.*|.claude.json|history.jsonl|*.pem|id_rsa*) return 0 ;;
  esac
  return 1
}

# Split the chain into segments and judge each git add/commit/push on its own.
printf '%s\n' "$cmd" | sed -E 's/(&&|\|\||;|\|)/\n/g' | while IFS= read -r seg; do
  printf '%s' "$seg" | grep -Eq "$re" || continue
  dir="$cwd"
  c="$(printf '%s' "$seg" | sed -nE 's/.*git[[:space:]]+-C[[:space:]]+("[^"]+"|[^[:space:]]+).*/\1/p' | tr -d '"')"
  [ -n "$c" ] && dir="$c"
  [ -n "$dir" ] || dir="."
  git -C "$dir" rev-parse --git-dir >/dev/null 2>&1 || continue
  verb="$(printf '%s' "$seg" | grep -Eo '(^|[[:space:]])(add|commit|push)([[:space:]]|$)' | head -1 | tr -d '[:space:]')"
  broad=0
  printf '%s' "$seg" | grep -Eq '(^|[[:space:]])(-A|--all|\.|-u|--update|-a|-am|-f|--force)([[:space:]]|$)' && broad=1
  {
    case "$verb" in
      add)
        # explicit paths: judge the names given; broad forms: judge everything git would pick up
        for t in $(printf '%s' "$seg" | sed -E 's/.*[[:space:]]add[[:space:]]*//'); do case "$t" in -*) ;; *) echo "$t" ;; esac; done
        [ "$broad" = 1 ] && git -C "$dir" status --porcelain --untracked-files=all 2>/dev/null | cut -c4-
        ;;
      commit)
        git -C "$dir" diff --cached --name-only 2>/dev/null
        [ "$broad" = 1 ] && git -C "$dir" diff --name-only 2>/dev/null
        ;;
      push) git -C "$dir" ls-files 2>/dev/null ;;
    esac
  } | { found=""; while IFS= read -r f; do [ -n "$f" ] && is_secret "$f" && found="$found $f"; done; [ -n "$found" ] && echo "$found" >> "${TMPDIR:-/tmp}/secret-guard.$$"; true; }
done
f="${TMPDIR:-/tmp}/secret-guard.$$"
if [ -s "$f" ]; then
  echo "secret-guard: blocked. Secret-looking files would be included:$(tr '\n' ' ' < "$f")" >&2
  echo "Remove them from the change or add them to .gitignore, then retry. .env.example/.sample/.template are allowed." >&2
  rm -f "$f"; exit 2
fi
rm -f "$f" 2>/dev/null
exit 0
