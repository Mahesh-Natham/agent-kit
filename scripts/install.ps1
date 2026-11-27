# Install this kit into Claude Code on this machine. Never overwrites: existing skills are skipped.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\install.ps1
$ErrorActionPreference = 'Stop'
$repo   = Split-Path $PSScriptRoot -Parent
$skills = Join-Path $env:USERPROFILE '.claude\skills'
New-Item -ItemType Directory -Force $skills | Out-Null

Get-ChildItem (Join-Path $repo 'skills') -Directory | ForEach-Object {
    $dst = Join-Path $skills $_.Name
    if (Test-Path $dst) { Write-Host "skip skill (exists): $($_.Name)" }
    else { Copy-Item $_.FullName $dst -Recurse; Write-Host "installed skill: $($_.Name)" }
}

$cfg = Get-Content (Join-Path $repo 'plugins\plugins.json') -Raw | ConvertFrom-Json
$cli = Get-Command claude -ErrorAction SilentlyContinue
$cmds = @()
foreach ($m in $cfg.marketplaces.PSObject.Properties) {
    $s = $m.Value.source
    $src = switch ($s.source) {
        'github'    { $s.repo }
        'git'       { $s.url }
        'directory' { Join-Path $repo "plugins\vendor\$($m.Name)" }
    }
    $cmds += "claude plugin marketplace add `"$src`""
}
foreach ($p in $cfg.enabledPlugins.PSObject.Properties) {
    if ($p.Value -and $p.Name -notlike '*@builtin') { $cmds += "claude plugin install $($p.Name)" }
}
if ($cli) {
    foreach ($c in $cmds) { Write-Host "> $c"; Invoke-Expression $c }
} else {
    Write-Warning "'claude' CLI not on PATH. Run these in a terminal where it is:"
    $cmds | ForEach-Object { Write-Host "  $_" }
}
Write-Host "`nStill to do by you: connect Gmail / Google Calendar / Google Sheets in the new account, then ask Claude to recreate routines from routines\routines.json."
