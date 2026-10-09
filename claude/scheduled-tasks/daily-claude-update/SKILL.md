---
name: daily-claude-update
description: Daily check of Claude Code, RTK and Anthropic releases and best practices, tool health, model fit and usage fit; writes a report with ready-to-apply proposals. Never edits the Claude config directory, installs, commits or pushes.
---

Reference copy of the scheduled task body. Replace `<repo>` with the absolute path of this machine's claude-global clone before using it.

Run the daily update routine defined in <repo>/claude/routines/daily-update.md. That file is the single source of truth for the steps and the output format; follow it exactly and do not rely on a copy of the steps anywhere else.

Paths: the report goes to <repo>/reports/YYYY-MM-DD.md, proposals are logged in <repo>/reports/proposals-log.md, the shared state is <repo>/state/last-seen.json.

Hard limits:
- Do not edit anything under the Claude config directory (CLAUDE_CONFIG_DIR or ~/.claude). Exception: the Ponytail hooks write their own `.ponytail-active` flag there; that is not an edit by this task.
- Do not run npm install, winget, brew, or rtk init.
- Do not git push or commit. Leave changes unstaged.
- Never apply a proposed change (settings, rules, agents, the routine itself). Write it into the report as a diff and stop.
- Read session history only through <repo>/scripts/usage-digest.sh, which prints aggregates. Do not open the session log files and do not quote their contents.
- Write only <repo>/reports/ and <repo>/state/last-seen.json.

Finish by stating the report path, the count of relevant items and of proposals, and any tool that is outdated or unhealthy.
