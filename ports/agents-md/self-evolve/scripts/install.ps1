# Windows installer for self-evolve (copies, no symlinks). Run: powershell -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = "Stop"
$src  = Split-Path -Parent $PSScriptRoot
$name = "self-evolve"
$home_ = $env:USERPROFILE
$dirs = @("$home_\.agents\skills")
if (Test-Path "$home_\.gemini") {
  $dirs += "$home_\.gemini\antigravity\skills", "$home_\.gemini\antigravity-cli\skills", "$home_\.gemini\skills", "$home_\.gemini\config\skills"
} else { Write-Host "~/.gemini not found: run Antigravity once, then re-run this script." }
foreach ($d in $dirs) {
  New-Item -ItemType Directory -Force -Path $d | Out-Null
  if (Test-Path "$d\$name") { Remove-Item -Recurse -Force "$d\$name" }
  Copy-Item -Recurse $src "$d\$name"; Write-Host "installed -> $d\$name"
}
$rules = "$home_\.gemini\GEMINI.md"
New-Item -ItemType Directory -Force -Path (Split-Path $rules) | Out-Null
if (-not (Test-Path $rules)) { New-Item -ItemType File -Path $rules | Out-Null }
if (-not (Select-String -Path $rules -Pattern "self-evolve:begin" -Quiet)) {
  Add-Content -Path $rules -Value ("`n" + (Get-Content "$src\assets\agents-md-snippet.md" -Raw)); Write-Host "rule added to $rules"
} else { Write-Host "rule already present" }
Write-Host "Done. Restart Antigravity, then ask: 'list your available skills'."
