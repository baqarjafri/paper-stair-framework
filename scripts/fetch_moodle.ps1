# fetch_moodle.ps1 — clone Moodle at the exact commit analysed by the paper.
#
# Pinned to commit: 213a869e7ffd48d3a5679818bcddbb22dbc31aa5
# Date:             2026-03-20
# Branch at pin:    main
# Build label:      Moodle 5.2dev+ (on-demand release)
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_moodle.ps1

$ErrorActionPreference = "Stop"

$PinnedSha = "213a869e7ffd48d3a5679818bcddbb22dbc31aa5"
$RepoUrl   = "https://github.com/moodle/moodle.git"
$Target    = "moodle_src"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

Write-Host "Fetching Moodle source at pinned commit $PinnedSha"
Write-Host "Target directory: $RepoRoot\$Target"
Write-Host ""

if (Test-Path "$Target\.git") {
    Write-Host "Existing clone found. Fetching and checking out pinned commit..."
    Set-Location $Target
    git fetch --depth 1 origin $PinnedSha
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    git checkout $PinnedSha
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "No existing clone. Cloning Moodle..."
    git clone $RepoUrl $Target
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Set-Location $Target
    git checkout $PinnedSha
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host ""
Write-Host "Moodle is now at commit:"
git log -1 --format='  %H%n  %ci%n  %s'
Write-Host ""
Write-Host "Done. Moodle source ready at: $RepoRoot\$Target"
