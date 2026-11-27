# Refresh this repo from the current machine (skills, plugin list, vendored local plugins, memory).
# Copies INTO the repo only; never deletes anything outside it. Routines are exported by asking Claude
# ("export my routines into agent-kit/routines") because they live in the cloud, not on disk.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\sync.ps1
$ErrorActionPreference = 'Stop'
$repo   = Split-Path $PSScriptRoot -Parent
$claude = Join-Path $env:USERPROFILE '.claude'

function Copy-Clean($src, $dst) {
    # copy a folder, skipping caches, logs and VCS data that may hold private or bulky content
    if (-not (Test-Path $src)) { Write-Warning "missing: $src"; return }
    New-Item -ItemType Directory -Force $dst | Out-Null
    robocopy $src $dst /E /NFL /NDL /NJH /NJS /NP /XD .git node_modules __pycache__ mods-logs .claude /XF *.pyc *.zip | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed for $src" }
}

# 1. user skills (~/.claude/skills)
Get-ChildItem (Join-Path $claude 'skills') -Directory | ForEach-Object { Copy-Clean $_.FullName (Join-Path $repo "skills\$($_.Name)") }

# 2. project skills worth keeping (add more paths here)
$projectSkills = @{
    'self-evolve' = 'D:\Ph.D 2026-2027\Projects\AEV\MU_AutonomousGroundVehicle\.claude\skills\self-evolve'
}
foreach ($k in $projectSkills.Keys) { Copy-Clean $projectSkills[$k] (Join-Path $repo "skills\$k") }

# 3. ports for other tools (AGENTS.md / .agents layout)
Copy-Clean 'D:\Ph.D 2026-2027\Extra\Antigravity\self-evolve' (Join-Path $repo 'ports\agents-md\self-evolve')

# 4. plugins: enabled list + marketplaces from settings.json; vendor marketplaces that only exist on this disk
$settings = Get-Content (Join-Path $claude 'settings.json') -Raw | ConvertFrom-Json
$plugins = [ordered]@{
    enabledPlugins = $settings.enabledPlugins
    marketplaces   = $settings.extraKnownMarketplaces
}
$plugins | ConvertTo-Json -Depth 6 | Out-File (Join-Path $repo 'plugins\plugins.json') -Encoding utf8
foreach ($p in $settings.extraKnownMarketplaces.PSObject.Properties) {
    if ($p.Value.source.source -eq 'directory') { Copy-Clean $p.Value.source.path (Join-Path $repo "plugins\vendor\$($p.Name)") }
}

# 5. memory (who I am, projects, preferences) - private repo only
$mem = Join-Path $claude 'projects\D--Ph-D-2026-2027\memory'
Copy-Clean $mem (Join-Path $repo 'memory')

# 6. secret check: fail loudly if anything token-like slipped in
$hits = Get-ChildItem $repo -Recurse -File -Exclude *.png,*.jpg,*.pdf |
    Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.FullName -ne $PSCommandPath } |
    Select-String -Pattern 'sk-ant-[A-Za-z0-9_-]{10,}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|"refreshToken"|"accessToken"|-----BEGIN [A-Z ]*PRIVATE KEY'
if ($hits) { $hits | ForEach-Object { Write-Warning "$($_.Path):$($_.LineNumber) looks like a secret" }; throw 'secret check failed: fix before committing' }
Write-Host "sync done: $repo"
