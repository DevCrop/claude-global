---
name: daily-claude-update
description: Check Claude Code changelog and Anthropic news; write a report only. Never edits ~/.claude or pushes.
---

Reference copy of the scheduled task body. Adjust the absolute paths below to this machine before using it.

Run the daily update routine defined in D:\project\claude-global\claude\routines\daily-update.md.

Steps:
1. Run `claude --version` to get the installed version.
2. Fetch https://code.claude.com/docs/en/changelog and list only entries newer than the version recorded in D:\project\claude-global\state\last-seen.json (field latest_changelog_version). If the file is missing, use the 10 most recent entries.
3. Fetch https://www.anthropic.com/news and list posts from the last 24 hours about Claude Code, models, skills, hooks, subagents, or the API.
4. X is optional and returns HTTP 402 to automated fetches. Do not rely on it.
5. Classify each new item as relevant (with affected file under claude/ and proposed change), informational, or ignore.
6. Write D:\project\claude-global\reports\YYYY-MM-DD.md using the output format in the routine file (Date, Installed, Latest official, Relevant, Informational, Not verified). Each item must include its source URL.
7. Update D:\project\claude-global\state\last-seen.json with the latest changelog version read and today's date.

Hard limits:
- Do not edit anything under the user's .claude directory (C:\Users\edn_y\.claude on the first machine).
- Do not run npm install, winget, or rtk init.
- Do not git push or commit. Leave changes unstaged.
- Do not apply proposed config changes. Only propose them in the report.

Finish by stating the report path and the count of relevant items.
