# Daily update routine

Purpose: track Claude Code and Anthropic releases, report what matters, and propose setup changes. This routine never changes `~/.claude` on its own.

Model: Sonnet. Run once per day.

## Steps

1. Read the installed version: `claude --version`.
2. Read the official changelog with WebFetch: `https://code.claude.com/docs/en/changelog`. Extract entries newer than the version in `state/last-seen.json`. If the file is missing, use the 10 most recent entries.
3. Read `https://www.anthropic.com/news` and list posts from the last 24 hours that concern Claude Code, models, skills, hooks, or subagents.
4. Optional signal only: search X for Claude Code and Claude Dev posts. x.com returns HTTP 402 to automated fetches, so use search snippets and do not rely on them. Official sources decide.
5. For each new item, classify it as: relevant to our setup, informational, or ignore. For relevant items, state the affected file in `claude/` and the proposed change.
6. Write `reports/YYYY-MM-DD.md` in this repository with: installed version, latest official version, new items, proposed changes, and what was not verified.
7. Update `state/last-seen.json` with the latest changelog version read.
8. Do not edit `~/.claude`, do not install anything, and do not push. A proposed change is applied only after the user approves it in chat.

## Output format

```
Date: YYYY-MM-DD
Installed: x.y.z   Latest official: x.y.z
Relevant:
- item | affected file | proposed change | source URL
Informational:
- item | source URL
Not verified:
- item | reason
```

## Scheduling

Create with the scheduled-task tool after the install phase is verified. Do not schedule before that.
