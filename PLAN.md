# Global Claude Setup Plan

Scope: `~/.claude` (global Claude Code). Codex is out of scope.
Source of truth: this repository. `~/.claude` is rebuilt from `claude/` after a clean reset.

## Decisions (defaults applied, change any of them here)

| Item | Decision |
|---|---|
| Reset scope | Full: delete all of `~/.claude` and `~/.claude.json`. Backup at `D:\backup\claude-20261008` (includes `.claude.json`). |
| RTK | Adopt. Install with `winget install rtk-ai.rtk`, then `rtk init -g`. |
| Archify | Install globally later, use only when a diagram is requested. Review `SKILL.md` before install. |
| Ponytail | Skip for now. It changes behavior in every session. Revisit per project. |
| Routine model | Sonnet for the daily update routine. |
| PR automation | Branch, commit, PR with `gh`. Merge is done by a person. Auto-merge only on request. |
| Git remote | `DevCrop/claude-global`. Push only after the user approves. |

## Phases

0. **Backup** (done): `~/.claude` and `~/.claude.json` copied to `D:\backup\claude-20261008`.
1. **Repository files** (done in this commit): `claude/CLAUDE.md`, `claude/settings.json`, `claude/agents/`, `claude/routines/daily-update.md`.
2. **Clean reset** (requires the Claude app closed): rename `~/.claude` and `~/.claude.json` to `*-old-20261008`, then delete them after verification.
3. **Install**: copy `claude/` into `~/.claude/`, log in again, install plugins only when needed.
4. **Tools**: `winget install rtk-ai.rtk`, `rtk init -g`, verify with `rtk gain`.
5. **Verification**: each item has a check listed below.
6. **Routine**: schedule `claude/routines/daily-update.md`. It reports and proposes changes. It never applies them.
7. **Project setup and optimization**: later, out of scope for this plan.

## Verification checks

- `claude --version` is at or above the latest version in the official changelog.
- `/agents` lists `reviewer` and `explorer`.
- `settings.json` parses, and `deny` blocks `rm -rf` and force push in a dry run.
- `rtk gain` shows a count after a few Bash commands.
- The daily routine writes `reports/YYYY-MM-DD.md` and leaves `~/.claude` unchanged.

## Known limits

- x.com returns HTTP 402 to automated fetches. X is used only as a search signal. Official sources are the authority: `code.claude.com/docs/en/changelog` and `anthropic.com/news`.
- RTK hooks only Bash tool calls. Read, Grep, and Glob are not filtered.
