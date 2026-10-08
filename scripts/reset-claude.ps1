# Partial clean reset of the global Claude config (legacy removal).
# Keeps login, conversation history, auto-memory and runtime data.
# Run AFTER closing the Claude desktop app and CLI.
# Backup must exist at D:\backup\claude-20261008 (created on 2026-10-08).

$ErrorActionPreference = "Stop"

$homeDir    = $env:USERPROFILE
$claudeDir  = Join-Path $homeDir ".claude"
$claudeJson = Join-Path $homeDir ".claude.json"
$backupDir  = "D:\backup\claude-20261008"

# Config-layer items to remove (legacy). Everything else in ~/.claude is kept.
$removeItems = @(
    "CLAUDE.md", "settings.json", "settings.json.bak-20260628-162002",
    "skills", "agents", "hooks", "state", "routines", "templates", "chrome",
    "statusline.ps1", "cleanup.ps1",
    "ARCHITECTURE.md", "AUTOMATION.md", "HARNESS_ARCHITECTURE.md",
    "PROMPT_ALGO.md", "README.md", "RTK.md",
    ".gitignore", ".git", ".last-update-result.json", ".last-cleanup",
    ".drift-queue", "reports", "backups", "active-projects.json"
)

# 1. Refuse to run while Claude is still running.
$running = Get-Process -Name "claude*" -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "Claude is still running (PIDs: $($running.Id -join ', ')). Close the app and CLI first." -ForegroundColor Red
    exit 1
}

# 2. Verify the backup holds the critical items before anything is deleted.
$required = @(
    (Join-Path $backupDir ".claude.json"),
    (Join-Path $backupDir ".credentials.json"),
    (Join-Path $backupDir ".git"),
    (Join-Path $backupDir "projects"),
    (Join-Path $backupDir "CLAUDE.md")
)
$missing = $required | Where-Object { -not (Test-Path $_) }
if ($missing) {
    Write-Host "Backup is incomplete. Missing:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  $_" }
    exit 1
}

# 3. Show exactly what will be removed.
$targets = @()
foreach ($name in $removeItems) {
    $p = Join-Path $claudeDir $name
    if (Test-Path -LiteralPath $p) { $targets += $p }
}
if (Test-Path $claudeJson) { $targets += $claudeJson }

Write-Host "Will delete (legacy config):" -ForegroundColor Yellow
$targets | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "Will keep: .credentials.json, projects/, sessions/, session-env/, plugins/, cache/, ide/, shell-snapshots/, history.jsonl" -ForegroundColor Cyan
Write-Host "Backup: $backupDir (intact)"
Write-Host ""

# 4. Final confirmation.
$answer = Read-Host "Type DELETE to continue"
if ($answer -ne "DELETE") {
    Write-Host "Cancelled. Nothing was deleted."
    exit 0
}

# 5. Delete.
foreach ($t in $targets) {
    Remove-Item -LiteralPath $t -Recurse -Force
}

# 6. Verify.
$left = @()
foreach ($name in $removeItems) {
    $p = Join-Path $claudeDir $name
    if (Test-Path -LiteralPath $p) { $left += $p }
}
if ((Test-Path $claudeJson) -or $left) {
    Write-Host "Deletion incomplete:" -ForegroundColor Red
    $left | ForEach-Object { Write-Host "  $_" }
    exit 1
}
Write-Host "Legacy removed. Login and history kept. Next: install claude/ files." -ForegroundColor Green
