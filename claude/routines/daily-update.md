# Daily update routine

Purpose: track Claude Code, RTK and Anthropic releases and best practices, check that the installed tools are actually in use, fit the setup to the models and to how the user really works, and propose improvements every day. This routine only reads, reports and proposes. It never changes `~/.claude`, never edits a managed file and never installs anything on its own. An update or a proposal is reported with its exact command or diff and applied by the user, through a branch and a PR.

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
   - Ponytail: latest = `version` in `https://raw.githubusercontent.com/DietrichGebert/ponytail/main/.claude-plugin/plugin.json` (the repo publishes no release tags). Installed = an entry named `ponytail` in `~/.claude/plugins/installed_plugins.json`, enabled = `"ponytail@ponytail": true` under `enabledPlugins` in `settings.json`. Update path from install guides, unverified in the README: `/plugin marketplace update ponytail`, then `/reload-plugins`.
   - Never install or update either one. Ponytail is always on by decision (2026-10-09): it is expected to be installed and enabled, so "not installed" or "disabled" is reported as unhealthy. Archify is installed only when the user asks for a diagram, after reading its SKILL.md; "not installed, latest x.y.z" is normal for it. Report the changelog entries since the last run that matter to us.
7. Tool health, read-only:
   - Config drift: `diff -r` of `claude/{CLAUDE.md,RTK.md,settings.json,agents,routines}` against the Claude config directory (`CLAUDE_CONFIG_DIR` or `~/.claude`). Compare `settings.json` as parsed JSON, so key order alone is not drift. Any difference is reported, not fixed.
   - Rule hygiene: `bash scripts/qa-deny.sh --static` must print PASS (read-only, no CLI), and `claude/CLAUDE.md` must be 200 lines or fewer.
   - RTK on PATH: `command -v rtk`. Missing means the hook is a no-op and Bash output is not filtered.
   - Ponytail: installed and enabled (see step 6). Its hooks write a `.ponytail-active` flag in the config directory; that is the plugin's own write, not an edit by this routine.
   - RTK in use: `rtk gain` total commands against `rtk_total_commands` in `state/last-seen.json`. An unchanged count since the last run is a signal, not proof, because no Bash may have run. Say which it is when unknown.
8. Docs watch (best practices). Run `bash scripts/docs-watch.sh --update`. It fetches eight official pages (best-practices, memory, sub-agents, permissions, costs, model-config, hooks-guide, settings) and prints NEW (baseline on this machine, no analysis), SAME, or CHANGED with a short line diff. For every CHANGED page, read the diff; fetch the page only if the diff is not enough. Classify each change as relevant (affects `claude/settings.json`, `claude/CLAUDE.md`, an agent or this routine), informational, or ignore.
9. Model fit. Write the current assignment table: `model`, `advisorModel`, `effortLevel` in `claude/settings.json`, and `model:` and `effort:` in each `claude/agents/*.md`. Compare it with the `model-config` diff and with Anthropic news (new, retired or re-priced models, new defaults, effort guidance). Propose a change only when a source says it, and cite that source.
10. Usage fit. Run `bash scripts/usage-digest.sh --days 7`. It prints aggregates only. Never open the session log files yourself and never quote their contents. Compare with the digest in the previous report when there is one, then apply these heuristics:
    - H1 permission friction: a Bash command word with 10 or more uses in 7 days that is read-only and routine becomes a proposed `allow` rule, always together with its `rtk ` twin. Never propose an allow rule for a destructive command (`rm`, `git push`, `git reset`, `git clean`, `git branch -D`, anything piped into a shell).
    - H2 delegation: an agent type unused for three consecutive reports while sessions did multi-step work becomes a proposal to fix its description or drop it. A `general-purpose` agent used often becomes a proposal for a purpose-built agent.
    - H3 context: more than one session with a peak above 500k tokens becomes a proposal about the handoff or `/clear` habit or the compaction instruction.
    - H4 errors: `tool_errors` up by more than 50% over the previous report is reported as a signal. The digest has no error text, so ask the user what failed instead of guessing a cause.
    - H5 model mix: a shift in turns or output tokens between models is compared with `effortLevel` and the agent models. Propose only with numbers.
    - The digest may not include advisor usage, so do not infer Opus cost from it.
11. Setup review, on Mondays only (local date). Read `claude/CLAUDE.md` line by line. For each line ask the official test: would removing it cause a mistake? Check for duplicates and contradictions with `claude/settings.json` and the project `CLAUDE.md`, and check that agent descriptions stay short. Propose cuts or merges.
12. Proposals. Write at most 5 numbered proposals P1, P2, ... ranked by value. Each has: Evidence (digest numbers or a source URL), Change (a unified diff against files in `claude/` or this routine, ready to apply), Risk, Verify (the command that proves it works, usually `bash scripts/qa-deny.sh --static` or the full `qa-deny.sh`), and Rollback. Skip an item marked rejected in `reports/proposals-log.md`. Raise an open item again only when its evidence changed. A proposal may change this routine, for example to drop a check that was identical in the last 7 reports or to tighten a heuristic.
13. Write `reports/YYYY-MM-DD.md` in this repository with: tool versions, new items, tool health, docs watch, model fit, the usage digest, proposals with their diffs, and what was not verified.
14. Append one line per new proposal to `reports/proposals-log.md` (local, create it if missing): `YYYY-MM-DD | P# | title | open`. The user marks a proposal applied or rejected in chat and a later session updates the line.
15. Update `state/last-seen.json` with the latest changelog version, `installed_rtk`, `latest_rtk_version`, `rtk_total_commands`, `latest_archify_version` and `latest_ponytail_version`. Write a value only if it was read this run.
16. Limits: do not edit the Claude config directory (the Ponytail flag file above is exempt), do not install anything, do not push or commit, and never apply a proposal. This routine writes only `reports/` and `state/last-seen.json`. A proposed change is applied only after the user approves it in chat.

## Output format

```
Date: YYYY-MM-DD
Claude Code: installed x.y.z | latest x.y.z | update command (if outdated)
RTK: installed x.y.z | latest x.y.z | update command (if outdated)
Archify: not installed or x.y.z | latest x.y.z | changes since last run
Ponytail: installed x.y.z, enabled yes/no (or NOT INSTALLED, unhealthy) | latest x.y.z | changes since last run
Docs watch:
- page | NEW, SAME or CHANGED | relevance to us
Model fit:
- current: main, advisor, effort, agents | finding | source URL | proposed change or none
Usage digest (7 days): sessions, turns, models, subagents, tool errors, peak context
Tool health:
- config drift | none or list of files
- rule hygiene | qa-deny --static pass/fail | CLAUDE.md line count
- rtk on PATH | yes/no
- rtk in use | commands today vs last run | signal or unknown
Relevant:
- item | affected file | proposed change | source URL
Informational:
- item | source URL
Proposals:
- P# | title | evidence | files | risk | verify | rollback (diff below)
Not verified:
- item | reason
```

## Scheduling

Created on the first machine on 2026-10-09. On a new machine, create it in the app's scheduled tasks from `claude/scheduled-tasks/daily-claude-update/SKILL.md` after replacing `<repo>`, and enable it on every machine that should be checked. Each machine writes its own local `reports/`; `state/last-seen.json` is shared through git, so see the pull note in the project `CLAUDE.md`.
