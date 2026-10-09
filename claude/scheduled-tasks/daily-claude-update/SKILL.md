---
name: daily-claude-update
description: Check Claude Code and RTK versions, tool health and Anthropic news; write a report only. Never edits the Claude config directory, installs, or pushes.
---

Reference copy of the scheduled task body. Replace `<repo>` with the absolute path of this machine's claude-global clone before using it.

Run the daily update routine defined in <repo>/claude/routines/daily-update.md.

Steps:
1. Run `claude --version` to get the installed version.
2. Fetch https://code.claude.com/docs/en/changelog and list only entries newer than the version recorded in <repo>/state/last-seen.json (field latest_changelog_version). If the file is missing, use the 10 most recent entries.
3. Fetch https://www.anthropic.com/news and list posts from the last 24 hours about Claude Code, models, skills, hooks, subagents, or the API.
4. X is optional and returns HTTP 402 to automated fetches. Do not rely on it.
5. Classify each new item as relevant (with affected file under claude/ and proposed change), informational, or ignore.
6. Tool versions: Claude Code installed vs `npm view @anthropic-ai/claude-code version` (without npm, use the newest changelog entry); RTK installed (`rtk --version`) vs https://github.com/rtk-ai/rtk/releases/latest. For an outdated tool, write the update command in the report and do not run it. Also track Archify (latest release tag at https://github.com/tt-a1i/archify/releases/latest; installed = ~/.claude/skills/archify/ exists) and Ponytail (latest = version in https://raw.githubusercontent.com/DietrichGebert/ponytail/main/.claude-plugin/plugin.json; installed = an entry named ponytail in ~/.claude/plugins/installed_plugins.json). Report "not installed, latest x.y.z" when absent. Never install either one.
7. Tool health, read-only: `diff -r` of claude/{CLAUDE.md,RTK.md,settings.json,agents,routines,skills/orchestrate} against the Claude config directory (CLAUDE_CONFIG_DIR or ~/.claude); `command -v rtk`; `rtk gain` total commands vs rtk_total_commands in last-seen.json (unchanged is a signal, not proof).
8. Write <repo>/reports/YYYY-MM-DD.md using the output format in the routine file. Each item must include its source URL.
9. Update <repo>/state/last-seen.json with the latest changelog version, installed_rtk, latest_rtk_version, rtk_total_commands, latest_archify_version, latest_ponytail_version and today's date. Write a value only if it was read this run.

Hard limits:
- Do not edit anything under the Claude config directory (CLAUDE_CONFIG_DIR or ~/.claude).
- Do not run npm install, winget, brew, or rtk init.
- Do not git push or commit. Leave changes unstaged.
- Do not apply proposed config changes. Only propose them in the report.

Finish by stating the report path, the count of relevant items, and any tool that is outdated or unhealthy.
