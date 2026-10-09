#!/usr/bin/env python3
"""Render the managed harness as one self-contained HTML page.

Reads claude/ and state/last-seen.json. Writes reports/dashboard.html (ignored by
git) or the path given as argv[1]. Read-only: touches nothing else. Stdlib only.
"""
import html
import json
import re
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
claude = repo / "claude"


def esc(s):
    return html.escape(str(s))


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    fm = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v))


settings = json.loads((claude / "settings.json").read_text(encoding="utf-8"))
state_path = repo / "state" / "last-seen.json"
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

# Deny rules: every Bash rule needs an rtk-prefixed twin (see CLAUDE.md rules).
deny = settings.get("permissions", {}).get("deny", [])
bash = [d[5:-1] for d in deny if d.startswith("Bash(") and d.endswith(")")]
plain = {b for b in bash if not b.startswith("rtk ")}
rtk = {b[4:] for b in bash if b.startswith("rtk ")}
missing_rtk = sorted(plain - rtk)
orphan_rtk = sorted(rtk - plain)
other_deny = [d for d in deny if not d.startswith("Bash(")]

agents = []
for p in sorted((claude / "agents").glob("*.md")):
    fm = frontmatter(p)
    agents.append((fm.get("name", p.stem), fm.get("model", "?"), fm.get("tools", "all"), fm.get("description", "")))

hooks = []
for event, entries in settings.get("hooks", {}).items():
    for e in entries:
        for h in e.get("hooks", []):
            hooks.append((event, e.get("matcher", "*"), h.get("command", "")))

routine = claude / "routines" / "daily-update.md"
steps = len(re.findall(r"^\d+\. ", routine.read_text(encoding="utf-8"), re.M)) if routine.exists() else 0

claude_md = claude / "CLAUDE.md"
md_lines = len(claude_md.read_text(encoding="utf-8").splitlines()) if claude_md.exists() else 0

checks = []  # (ok, label, detail)
checks.append((not missing_rtk, "Bash deny rules have an rtk twin", ", ".join(missing_rtk) or "all %d covered" % len(plain)))
checks.append((not orphan_rtk, "No rtk deny rule without a plain twin", ", ".join(orphan_rtk) or "none"))
checks.append((md_lines < 200, "claude/CLAUDE.md under 200 lines", "%d lines" % md_lines))
inst, latest = state.get("installed_cli"), state.get("latest_cli_npm") or state.get("latest_changelog_version")
if inst and latest:
    checks.append((vtuple(inst) >= vtuple(latest), "Claude Code up to date", "installed %s, latest %s" % (inst, latest)))
else:
    checks.append((None, "Claude Code up to date", "unknown: state has no version"))


def table(head, rows):
    th = "".join("<th>%s</th>" % esc(h) for h in head)
    body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r) for r in rows)
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, body)


def badge(ok):
    return {True: '<span class="b ok">ok</span>', False: '<span class="b bad">check</span>', None: '<span class="b na">unknown</span>'}[ok]


cards = [
    ("Main model", settings.get("model", "default")),
    ("Advisor", settings.get("advisorModel", "none")),
    ("Effort", settings.get("effortLevel", "default")),
    ("Deny rules", len(deny)),
    ("Subagents", len(agents)),
    ("Hooks", len(hooks)),
    ("Routine steps", steps),
]
cards_html = "".join('<div class="card"><div class="k">%s</div><div class="v">%s</div></div>' % (esc(k), esc(v)) for k, v in cards)
checks_html = "".join("<li>%s <strong>%s</strong> <span class=\"d\">%s</span></li>" % (badge(o), esc(l), esc(d)) for o, l, d in checks)
state_rows = [(k, v) for k, v in state.items()]

page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Harness Map</title>
<style>
:root{--bg:#fafaf9;--fg:#1c1917;--mut:#78716c;--card:#fff;--line:#e7e5e4;--ok:#15803d;--bad:#b91c1c;--na:#a16207}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1c1917;--fg:#f5f5f4;--mut:#a8a29e;--card:#292524;--line:#44403c;--ok:#4ade80;--bad:#f87171;--na:#facc15}}
:root[data-theme="dark"]{--bg:#1c1917;--fg:#f5f5f4;--mut:#a8a29e;--card:#292524;--line:#44403c;--ok:#4ade80;--bad:#f87171;--na:#facc15}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:960px;margin:0 auto;padding:24px 16px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 8px}
.sub{color:var(--mut);margin:0 0 16px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
.k{color:var(--mut);font-size:12px}.v{font-size:18px;font-weight:600;word-break:break-word}
table{width:100%%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:8px;display:block;overflow-x:auto}
th,td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top;font-size:13px}
th{color:var(--mut);font-weight:500}code,td{font-family:ui-monospace,monospace}
ul{list-style:none;padding:0;margin:0}li{padding:4px 0}.d{color:var(--mut)}
.b{display:inline-block;min-width:56px;text-align:center;border-radius:4px;padding:0 6px;font-size:12px;border:1px solid currentColor}
.ok{color:var(--ok)}.bad{color:var(--bad)}.na{color:var(--na)}
</style></head><body><main>
<h1>Harness Map</h1>
<p class="sub">Generated from <code>claude/</code> and <code>state/last-seen.json</code>. State checked on %(checked)s.</p>
<div class="cards">%(cards)s</div>
<h2>Checks</h2><ul>%(checks)s</ul>
<h2>Task routing: subagents</h2>%(agents)s
<h2>Hooks</h2>%(hooks)s
<h2>Deny rules outside Bash</h2>%(other)s
<h2>State (daily routine baseline)</h2>%(state)s
</main></body></html>
""" % {
    "checked": esc(state.get("checked_on", "never")),
    "cards": cards_html,
    "checks": checks_html,
    "agents": table(["name", "model", "tools", "description"], agents),
    "hooks": table(["event", "matcher", "command"], hooks) if hooks else "<p class=\"d\">none</p>",
    "other": table(["rule"], [(d,) for d in other_deny]) if other_deny else "<p class=\"d\">none</p>",
    "state": table(["key", "value"], state_rows) if state_rows else "<p class=\"d\">empty</p>",
}

out = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "reports" / "dashboard.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(page, encoding="utf-8")
print(out)
