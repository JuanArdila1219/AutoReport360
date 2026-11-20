param(
    [Parameter(Mandatory=$true)][string]$Batch,
    [Parameter(Mandatory=$true)][string]$Workspace,
    [switch]$RecoverCorrupt
)
$ErrorActionPreference = 'Stop'
try {
    $projectRoot = Split-Path -Parent $PSScriptRoot
    $python = Join-Path $projectRoot '.venv\Scripts\python.exe'
    $entry = Join-Path $projectRoot 'scripts\run_automation.py'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Project Python interpreter unavailable' }
    $pythonArgs = @($entry, $Batch, '--workspace', $Workspace)
    if ($RecoverCorrupt) { $pythonArgs += '--recover-corrupt' }
    $output = & $python @pythonArgs
    $code = $LASTEXITCODE
    if (-not $output) { throw 'Orchestrator returned no JSON' }
    $parsed = ($output -join "`n") | ConvertFrom-Json
    [pscustomobject]@{ exit_code = $code; result = $parsed } | ConvertTo-Json -Depth 40 -Compress
    exit $code
} catch {
    [pscustomobject]@{ exit_code = 1; result = @{ status = 'FAILED'; distribution_status = 'NOT_PREPARED'; errors = @($_.Exception.Message) } } | ConvertTo-Json -Depth 8 -Compress
    exit 1
}
