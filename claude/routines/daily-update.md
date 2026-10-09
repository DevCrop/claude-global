# Daily update routine

Purpose: track Claude Code, RTK and Anthropic releases, check that the installed tools are actually in use, report what matters, and propose setup changes. This routine only reads and reports. It never changes `~/.claude` and never installs anything on its own. An update is reported with its exact command and applied by the user.

Model: Sonnet (target). Run once per day.

Note: the scheduled task has no model field, so it runs on the app default. The first run (2026-10-09) ran on Haiku by decision. Set Sonnet for later runs in the app's Scheduled settings, and check the model shown in the run session.

## Steps

1. Read the installed version: `claude --version`.
2. Read the official changelog with WebFetch: `https://code.claude.com/docs/en/changelog`. Extract entries newer than the version in `state/last-seen.json`. If the file is missing, use the 10 most recent entries.
3. Read `https://www.anthropic.com/news` and list posts from the last 24 hours that concern Claude Code, models, skills, hooks, or subagents.
4. Optional signal only: search X for Claude Code and Claude Dev posts. x.com returns HTTP 402 to automated fetches, so use search snippets and do not rely on them. Official sources decide.
5. For each new item, classify it as: relevant to our setup, informational, or ignore. For relevant items, state the affected file in `claude/` and the proposed change.
6. Tool versions. Claude Code: installed (`claude --version`) against latest (`npm view @anthropic-ai/claude-code version`, cross-checked with the changelog). RTK: installed (`rtk --version`) against latest (`https://github.com/rtk-ai/rtk/releases/latest`). For each outdated tool, write the update command (npm, `winget upgrade rtk-ai.rtk` or `brew upgrade rtk`) in the report without running it.
7. Tool health, read-only:
   - Config drift: `diff -r` of `claude/{CLAUDE.md,RTK.md,settings.json,agents,routines}` against the Claude config directory (`CLAUDE_CONFIG_DIR` or `~/.claude`). Any difference is reported, not fixed.
   - RTK on PATH: `command -v rtk`. Missing means the hook is a no-op and Bash output is not filtered.
   - RTK in use: `rtk gain` total commands against `rtk_total_commands` in `state/last-seen.json`. An unchanged count since the last run is a signal, not proof, because no Bash may have run. Say which it is when unknown.
8. Write `reports/YYYY-MM-DD.md` in this repository with: tool versions, new items, tool health, proposed changes, and what was not verified.
9. Update `state/last-seen.json` with the latest changelog version, `installed_rtk`, `latest_rtk_version` and `rtk_total_commands`. Write a value only if it was read this run.
10. Do not edit the Claude config directory, do not install anything, and do not push. A proposed change is applied only after the user approves it in chat.

## Output format

```
Date: YYYY-MM-DD
Claude Code: installed x.y.z | latest x.y.z | update command (if outdated)
RTK: installed x.y.z | latest x.y.z | update command (if outdated)
Tool health:
- config drift | none or list of files
- rtk on PATH | yes/no
- rtk in use | commands today vs last run | signal or unknown
Relevant:
- item | affected file | proposed change | source URL
Informational:
- item | source URL
Not verified:
- item | reason
```

## Scheduling

Create with the scheduled-task tool after the install phase is verified. Do not schedule before that.
