#!/usr/bin/env bash
# Aggregate-only digest of the local Claude Code session logs: counts and token totals
# per model, tool, subagent type and Bash command word. It never prints message text,
# file paths or command arguments. Usage: bash scripts/usage-digest.sh [--days N]
# Needs jq (already required by the status line).
set -eu

days=7
if [ "${1:-}" = "--days" ]; then days="${2:?--days needs a number}"; fi
case "$days" in ''|*[!0-9]*) echo "--days needs a whole number" >&2; exit 2 ;; esac
dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"

command -v jq >/dev/null 2>&1 || { echo "jq not found" >&2; exit 2; }
[ -d "$dir" ] || { echo "no session logs at $dir"; exit 0; }
files="$(find "$dir" -maxdepth 2 -name '*.jsonl' -mtime "-$days" 2>/dev/null)"
[ -n "$files" ] || { echo "no sessions in the last $days days"; exit 0; }

# shellcheck disable=SC2086
printf '%s\n' "$files" | tr '\n' '\0' | xargs -0 jq -s --argjson days "$days" '
  def ts: (.timestamp | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601);
  def word($c):
    ($c | split(" ")) as $t
    | ($t[0] // "") as $a
    | if ($a | test("^[A-Za-z][A-Za-z0-9_.-]*$")) then
        (($t[1] // "") as $b
          | if ($a | IN("git","rtk","npm","npx","pnpm","yarn","brew","claude","gh","docker","cargo","pip","go","kubectl","make"))
               and ($b | test("^[a-z][a-z-]*$"))
            then "\($a) \($b)" else $a end)
      else "other" end;
  (now - ($days * 86400)) as $cut
  | map(select(type == "object" and .timestamp != null and ((try ts catch 0) >= $cut))) as $e
  | ($e | map(select(.type == "assistant"))) as $a
  | ($e | map(select(.type == "user"))) as $u
  | ($a | [.[].message.content[]? | select(type == "object" and .type == "tool_use")]) as $uses
  | {
      window_days: $days,
      sessions: ($e | map(.sessionId) | unique | length),
      assistant_turns: ($a | length),
      models: ($a | group_by(.message.model) | map({
        model: .[0].message.model, turns: length,
        output_tokens: (map(.message.usage.output_tokens // 0) | add)}) | sort_by(-.turns)),
      tokens: {
        input: ($a | map(.message.usage.input_tokens // 0) | add),
        output: ($a | map(.message.usage.output_tokens // 0) | add),
        cache_read: ($a | map(.message.usage.cache_read_input_tokens // 0) | add),
        cache_creation: ($a | map(.message.usage.cache_creation_input_tokens // 0) | add)},
      top_tools: ($uses | group_by(.name) | map({tool: .[0].name, n: length}) | sort_by(-.n) | .[:12]),
      subagents: ($uses | map(select(.name == "Agent" or .name == "Task") | (.input.subagent_type // "general-purpose"))
        | group_by(.) | map({type: .[0], n: length}) | sort_by(-.n)),
      bash_command_words: ($uses | map(select(.name == "Bash") | word(.input.command // ""))
        | group_by(.) | map({cmd: .[0], n: length}) | sort_by(-.n) | .[:12]),
      tool_errors: ($u | [.[].message.content[]? | select(type == "object" and .type == "tool_result" and .is_error == true)] | length),
      peak_context_tokens_top5: ($a | group_by(.sessionId) | map(map((.message.usage.input_tokens // 0)
        + (.message.usage.cache_read_input_tokens // 0) + (.message.usage.cache_creation_input_tokens // 0)) | max)
        | sort | reverse | .[:5])
    }'
