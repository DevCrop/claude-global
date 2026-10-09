# Review: obra/superpowers v6.4.2

Source: https://github.com/obra/superpowers @ 8ca22db (2026-09-25).
Read: README, `using-superpowers`, `brainstorming`, `test-driven-development`, `hooks/session-start`, `AGENTS.md`.
Not read: remaining skills, `tests/` execution results. The external eval harness (`superpowers-evals`) was not inspected, so effectiveness claims are unverified.

## Verdict

Ship with fixes. For this setup (vanilla compliance): do not install the full plugin; cherry-pick selectively.

## Strongest counter-case

Official marketplace listing, `tests/`, an external eval harness, and design history under `docs/superpowers/specs` show this is not an unverified prompt pile. Eval results are not in the repo, so they could not be checked.

## Issues

- [risk] Constant context cost: the SessionStart hook (`startup|clear|compact`) injects `using-superpowers` (~490 words) every time; 15 skill descriptions are always loaded. Bodies total ~25k words; triggered skills load whole (`subagent-driven-development` 4.8k, `writing-skills` 3.8k, `executing-plans` 3.2k).
- [risk] Over-triggering by design: `EXTREMELY-IMPORTANT`, "1% chance -> MUST invoke", skill check before clarifying questions; `brainstorming` description says "You MUST use this before any creative work". Conflicts with a "skip for trivial edits" policy.
- [risk] TDD iron law ("NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST", delete code written first) is unenforceable in infra, config, or legacy PHP without a test harness; invites workarounds or token tests. Exceptions require asking the human.
- [smell] Skill text is adversarial prompting (rationalization tables, "violating the letter is violating the spirit"). Behavior is likely model-version sensitive; regression coverage depends on the author's private evals.
- [smell] `AGENTS.md` rejects Anthropic's published skill-writing guidance in favor of unpublished internal evals. Opposite of working from official docs.
- [smell] 16 harness adapters (`.cursor-plugin`, `.kimi-plugin`, `.hermes-plugin`, `.muse-plugin`, ...) and env-var branching in `hooks/session-start`. Dead surface for a Claude-Code-only user; workaround for bash 5.3 heredoc hang (#571) remains in code.
- [risk] Telemetry: brainstorming's visual companion loads a logo from the vendor site with the Superpowers version (default on). Opt-outs: `SUPERPOWERS_DISABLE_TELEMETRY`, `DISABLE_TELEMETRY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. Per the README it sends no project data; not verified in code.
- [taste] `writing-plans` assumes a "junior engineer with no judgement"; plans and per-task subagent reviews are token-heavy by default (v6.4.2 trimmed plans).

## What works

- `brainstorming` HARD-GATE: approval applies only to the stage actually presented; idea approval does not imply spec or plan approval.
- `verification-before-completion` (556 words) and `requesting-code-review` (422 words) are small and overlap the existing "real check before done" preference.
- `systematic-debugging`: no fix before root cause; matches "failing test first".

## Recommendation for claude-global

The three small skills above duplicate what user preferences already enforce, so marginal gain is low. Full install adds hook-injected context and an unverified interaction with RTK/deny-rule evaluation (`scripts/qa-deny.sh` not run against it). If adopted, copy individual skills into `claude/` instead of installing the plugin, and re-run `bash scripts/qa-deny.sh`.

## Open

Which skills (if any) to adopt, after reading their bodies in full.
