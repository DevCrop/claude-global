#!/usr/bin/env python3
"""Local live dashboard for the global Claude setup. Read-only, stdlib only, 127.0.0.1 only.

Run: python3 scripts/dashboard/server.py [--port 8787]
Reads: git history, gh PR list, scripts/verify.sh --live, reports/*.md, claude/settings.json,
and the tool-call names and timestamps of the newest session log in ~/.claude/projects.
It never reads message text, tool inputs beyond a file's basename, or credentials.
"""
import json, os, re, subprocess, sys, threading, time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONFIG = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
PROJECTS = CONFIG / "projects"
CACHE = {}  # key -> (time, value)
REFRESHING = set()
LOCK = threading.Lock()


def find_bash():
    # On Windows, `bash` on PATH can be WSL's with another HOME; verify.sh needs Git Bash.
    for c in (os.environ.get("BASH"), "C:/Program Files/Git/bin/bash.exe", "C:/Program Files (x86)/Git/bin/bash.exe"):
        if c and Path(c).exists():
            return c
    return "bash"


BASH = find_bash()
ENV = {**os.environ, "HOME": os.environ.get("USERPROFILE", os.environ.get("HOME", ""))} if os.name == "nt" else None


def run(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return p.stdout
    except Exception:
        return ""


def cached(key, ttl, fn, slow=False, placeholder=None):
    """Return the cached value. A slow source (verify.sh, gh) refreshes in a thread, so a request never waits on it."""
    now = time.time()
    with LOCK:
        hit = CACHE.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1]
        if slow:
            if key not in REFRESHING:
                REFRESHING.add(key)
                threading.Thread(target=refresh, args=(key, fn), daemon=True).start()
            return hit[1] if hit else placeholder
    return refresh(key, fn)


def refresh(key, fn):
    try:
        val = fn()
        with LOCK:
            CACHE[key] = (time.time(), val)
        return val
    finally:
        with LOCK:
            REFRESHING.discard(key)


def git_history():
    out = run(["git", "log", "-60", "--date=iso-strict", "--pretty=format:%h\x1f%ad\x1f%s\x1f%an"])
    commits = []
    for line in out.splitlines():
        h, ad, s, an = (line.split("\x1f") + ["", "", "", ""])[:4]
        merge = re.match(r"Merge pull request #(\d+) from \S+", s)
        commits.append({"hash": h, "at": ad, "subject": s, "author": an, "pr": int(merge.group(1)) if merge else None})
    return {"commits": commits, "branch": run(["git", "branch", "--show-current"]).strip(),
            "dirty": len([l for l in run(["git", "status", "--short"]).splitlines() if l.strip()])}


def pull_requests():
    out = run(["gh", "pr", "list", "--state", "all", "--limit", "30", "--json", "number,title,state,createdAt,mergedAt,additions,deletions,changedFiles"])
    try:
        return json.loads(out)
    except Exception:
        return []


def verify():
    out = run([BASH, "-l", "scripts/verify.sh", "--live"], timeout=120)
    lines = [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in out.splitlines() if l.strip()]
    counts = {"PASS": 0, "FAIL": 0, "WARN": 0}
    for l in lines:
        k = l.split(" ", 1)[0]
        if k in counts:
            counts[k] += 1
    return {"at": datetime.now(timezone.utc).isoformat(), "counts": counts, "lines": lines[-80:]}


def settings():
    try:
        s = json.loads((ROOT / "claude" / "settings.json").read_text(encoding="utf-8"))
        p = s.get("permissions", {})
        live = json.loads((CONFIG / "settings.json").read_text(encoding="utf-8")).get("permissions", {})
        return {"mode": p.get("defaultMode"), "deny": len(p.get("deny", [])), "ask": len(p.get("ask", [])),
                "liveMode": live.get("defaultMode"), "liveDeny": len(live.get("deny", [])), "liveAsk": len(live.get("ask", [])),
                "model": s.get("model"), "advisor": s.get("advisorModel")}
    except Exception:
        return {}


def reports():
    d = ROOT / "reports"
    items = []
    if d.is_dir():
        for f in sorted(d.glob("20*.md"), reverse=True)[:7]:
            items.append({"name": f.name, "mtime": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(),
                          "text": f.read_text(encoding="utf-8", errors="replace")[:4000]})
    return items


def session_events(limit=120):
    """Tool-call name, time and a safe target (file basename or command head) from the newest session log."""
    files = list(PROJECTS.glob("*/*.jsonl")) if PROJECTS.is_dir() else []
    if not files:
        return {"session": None, "events": []}
    f = max(files, key=lambda p: p.stat().st_mtime)
    try:
        with open(f, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - 1_500_000))
            raw = fh.read().decode("utf-8", errors="replace").splitlines()
    except Exception:
        return {"session": None, "events": []}
    events = []
    for line in raw:
        try:
            d = json.loads(line)
        except Exception:
            continue
        ts = d.get("timestamp")
        if not ts:
            continue
        t = d.get("type")
        c = (d.get("message") or {}).get("content")
        if t == "assistant" and isinstance(c, list):
            for x in c:
                if x.get("type") == "tool_use":
                    inp = x.get("input") or {}
                    target = ""
                    if inp.get("file_path"):
                        target = os.path.basename(str(inp["file_path"]))
                    elif inp.get("command"):
                        target = " ".join(str(inp["command"]).split()[:2])[:40]
                    elif inp.get("pattern"):
                        target = "search"
                    events.append({"at": ts, "kind": "tool", "name": str(x.get("name", "?")).split("__")[-1], "target": target})
        elif t == "user" and isinstance(c, str) and not c.startswith("<"):
            events.append({"at": ts, "kind": "user", "name": "user message", "target": ""})
    return {"session": f.stem[:8], "mtime": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(), "events": events[-limit:]}


def state():
    return {
        "now": datetime.now(timezone.utc).isoformat(),
        "git": cached("git", 5, git_history),
        "prs": cached("prs", 60, pull_requests, slow=True, placeholder=[]),
        "verify": cached("verify", 60, verify, slow=True, placeholder={"at": datetime.now(timezone.utc).isoformat(), "counts": {"PASS": 0, "FAIL": 0, "WARN": 0}, "lines": ["검증 실행 중..."]}),
        "settings": cached("settings", 5, settings),
        "reports": cached("reports", 30, reports),
        "activity": session_events(),
    }


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/state"):
            body, ctype = json.dumps(state()).encode(), "application/json"
        elif self.path in ("/", "/index.html"):
            body, ctype = (HERE / "index.html").read_bytes(), "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8787
    print(f"dashboard on http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
