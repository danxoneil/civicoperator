# Nightly: parse the newest Substack export on Google Drive -> dispatch_index.json,
# and push it to main if it changed. The push triggers build-state-pages.yml,
# which rebuilds the per-state "Activity log" sections on /work/rht/states/.
#
# Runs on this PC (the GitHub runner can't see Drive) from Task Scheduler task
# "RHT Dispatch Index Refresh". Works in a dedicated clone so it never touches
# a working checkout. Log: %LOCALAPPDATA%\civicoperator-dispatch\refresh.log

$ErrorActionPreference = 'Stop'
$Work   = Join-Path $env:LOCALAPPDATA 'civicoperator-dispatch'
$Clone  = Join-Path $Work 'repo'
$Log    = Join-Path $Work 'refresh.log'
$Remote = 'https://github.com/danxoneil/civicoperator.git'
$Rel    = 'state-spending-monitor/state_pages/dispatch_index.json'
$env:EXPORT_ROOT = 'G:/My Drive/RHT/Substack Exports'

New-Item -ItemType Directory -Force $Work | Out-Null
function Log($m) { "$(Get-Date -Format s)  $m" | Add-Content $Log }

try {
    if (-not (Test-Path (Join-Path $Clone '.git'))) {
        git clone --quiet --depth 50 $Remote $Clone
    }
    Set-Location $Clone
    git fetch --quiet origin main
    git checkout --quiet -B main origin/main
    git reset --quiet --hard origin/main

    $out = python state-spending-monitor/state_pages/parse_dispatches.py 2>&1
    if ($LASTEXITCODE -ne 0) { throw "parse failed: $out" }
    Log "$out"

    git diff --quiet -- $Rel
    if ($LASTEXITCODE -eq 0) { Log 'no change'; exit 0 }

    git add -- $Rel
    git commit --quiet -m "RHT: refresh dispatch index from Substack export $(Get-Date -Format yyyy-MM-dd)"
    git push --quiet origin main
    if ($LASTEXITCODE -ne 0) { throw 'push failed' }
    Log 'pushed'
} catch {
    Log "ERROR: $_"
    exit 1
}
