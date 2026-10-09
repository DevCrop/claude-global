# Daily update routine

Purpose: track Claude Code, RTK and Anthropic releases, check that the installed tools are actually in use, report what matters, and propose setup changes. This routine only reads and reports. It never changes `~/.claude` and never installs anything on its own. An update is reported with its exact command and applied by the user.

Model: Sonnet (target). Run once per day.

Note: the scheduled task has no model field, so it runs on the app default. The first manual run (2026-10-09) ran on Haiku by decision. The first automatic run showed `claude-sonnet-5-5`, but whether that came from a setting or the default is unknown. Set Sonnet explicitly in the app's Scheduled settings and check the model shown in the run session.

## Steps

1. Read the installed version: `claude --version`.
2. Read the official changelog with WebFetch: `https://code.claude.com/docs/en/changelog`. Extract entries newer than the version in `state/last-seen.json`. If the file is missing, use the 10 most recent entries.
3. Read `https://www.anthropic.com/news` and list posts from the last 24 hours that concern Claude Code, models, skills, hooks, or subagents.
4. Optional signal only: search X for Claude Code and Claude Dev posts. x.com returns HTTP 402 to automated fetches, so use search snippets and do not rely on them. Official sources decide.
5. For each new item, classify it as: relevant to our setup, informational, or ignore. For relevant items, state the affected file in `claude/` and the proposed change.
6. Tool versions. Claude Code: installed (`claude --version`) against latest (`npm view @anthropic-ai/claude-code version`, cross-checked with the newest changelog entry; if `npm` is not installed, which is normal for the native installer, use the newest changelog entry alone). RTK: installed (`rtk --version`) against latest (`https://github.com/rtk-ai/rtk/releases/latest`). For each outdated tool, write the update command (npm, `winget upgrade rtk-ai.rtk` or `brew upgrade rtk`) in the report without running it.
   Optional tools, tracked whether or not they are installed:
   - Archify: latest = the release tag at `https://github.com/tt-a1i/archify/releases/latest`. Installed = `~/.claude/skills/archify/` exists (version only if its SKILL.md states one, else unknown). The README does not say where its installer writes files, so a missing folder means "not found", not proof of absence. The README gives no update command and says updates are never automatic; report re-running `npx skills add tt-a1i/archify -g` as unverified.
   - Ponytail: latest = `version` in `https://raw.githubusercontent.com/DietrichGebert/ponytail/main/.claude-plugin/plugin.json` (the repo publishes no release tags). Installed = an entry named `ponytail` in `~/.claude/plugins/installed_plugins.json`. Update path from install guides, unverified in the README: `/plugin marketplace update ponytail`, then `/reload-plugins`.
   - Never install either one. Ponytail stays off by decision (it adds always-on behavior to every session); Archify is installed only when the user asks for a diagram, after reading its SKILL.md. Report only "not installed, latest x.y.z" and the changelog entries since the last run that matter to us.
7. Tool health, read-only:
   - Config drift: `diff -r` of `claude/{CLAUDE.md,RTK.md,settings.json,agents,routines,skills/orchestrate}` against the Claude config directory (`CLAUDE_CONFIG_DIR` or `~/.claude`). Any difference is reported, not fixed.
   - RTK on PATH: `command -v rtk`. Missing means the hook is a no-op and Bash output is not filtered.
   - RTK in use: `rtk gain` total commands against `rtk_total_commands` in `state/last-seen.json`. An unchanged count since the last run is a signal, not proof, because no Bash may have run. Say which it is when unknown.
8. Write `reports/YYYY-MM-DD.md` in this repository with: tool versions, new items, tool health, proposed changes, and what was not verified.
9. Update `state/last-seen.json` with the latest changelog version, `installed_rtk`, `latest_rtk_version`, `rtk_total_commands`, `latest_archify_version` and `latest_ponytail_version`. Write a value only if it was read this run.
10. Do not edit the Claude config directory, do not install anything, and do not push. A proposed change is applied only after the user approves it in chat.

## Output format

```
Date: YYYY-MM-DD
Claude Code: installed x.y.z | latest x.y.z | update command (if outdated)
RTK: installed x.y.z | latest x.y.z | update command (if outdated)
Archify: not installed or x.y.z | latest x.y.z | changes since last run
Ponytail: not installed or x.y.z | latest x.y.z | changes since last run
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

Created on the first machine on 2026-10-09. On a new machine, create it in the app's scheduled tasks from `claude/scheduled-tasks/daily-claude-update/SKILL.md` after replacing `<repo>`, and enable it on one machine only.
