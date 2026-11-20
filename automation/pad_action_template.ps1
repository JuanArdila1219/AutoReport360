# Paste into PAD. PAD substitutes these trusted variables before PowerShell starts.
$ProgressPreference = 'SilentlyContinue'
$projectRoot = '%ProyectoRuta%'
$workspace = '%Workspace%'
$batch = '%Batch%'
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$response = $null
$pythonExitCode = $null

try {
    $python = Join-Path $projectRoot '.venv\Scripts\python.exe'
    $entry = Join-Path $projectRoot 'scripts\run_automation.py'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'PYTHON_NOT_FOUND' }
    if (-not (Test-Path -LiteralPath $entry -PathType Leaf)) { throw 'ORCHESTRATOR_NOT_FOUND' }

    # A nonzero Python exit code is business data, not a PowerShell exception.
    $previousPreference = $ErrorActionPreference
    $previousConsoleEncoding = [Console]::OutputEncoding
    $previousPythonEncoding = $env:PYTHONIOENCODING
    try {
        $ErrorActionPreference = 'Continue'
        [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
        $env:PYTHONIOENCODING = 'utf-8'
        $global:LASTEXITCODE = $null
        $raw = & $python $entry $batch '--workspace' $workspace 2>$null
        $pythonExitCode = $LASTEXITCODE
    } finally {
        [Console]::OutputEncoding = $previousConsoleEncoding
        $env:PYTHONIOENCODING = $previousPythonEncoding
        $ErrorActionPreference = $previousPreference
    }
    if ($null -eq $pythonExitCode) { throw 'PYTHON_START_FAILED' }
    $jsonText = ($raw -join "`n").Trim()
    if ([string]::IsNullOrWhiteSpace($jsonText)) { throw 'EMPTY_OUTPUT' }
    try { $result = ConvertFrom-Json -InputObject $jsonText -ErrorAction Stop }
    catch { throw 'INVALID_JSON' }

    if ($null -eq $result -or $result -is [array] -or
        $result.status -notin @('SUCCESS', 'SKIPPED', 'REJECTED', 'FAILED') -or
        $result.distribution_status -notin @('PREPARED', 'NOT_DUPLICATED', 'NOT_PREPARED') -or
        $null -eq $result.errors -or $result.errors -isnot [array]) {
        throw 'INVALID_CONTRACT'
    }
    $expectedCode = if ($result.status -in @('SUCCESS', 'SKIPPED')) { 0 } elseif ($result.status -eq 'REJECTED') { 2 } else { 1 }
    if ($pythonExitCode -ne $expectedCode) { throw 'EXIT_STATUS_MISMATCH' }
    if ($null -eq $result.PSObject.Properties['reason']) {
        $result | Add-Member -NotePropertyName 'reason' -NotePropertyValue $null
    }
    $response = [pscustomobject]@{ exit_code = [int]$pythonExitCode; result = $result }
} catch {
    $reason = $_.Exception.Message
    $known = @('PYTHON_NOT_FOUND', 'ORCHESTRATOR_NOT_FOUND', 'PYTHON_START_FAILED', 'EMPTY_OUTPUT', 'INVALID_JSON', 'INVALID_CONTRACT', 'EXIT_STATUS_MISMATCH')
    if ($reason -notin $known) { $reason = 'POWERSHELL_EXCEPTION' }
    $response = [pscustomobject]@{
        exit_code = 1
        python_exit_code = $pythonExitCode
        result = [pscustomobject]@{
            automation_id = 'NO_DISPONIBLE'
            status = 'FAILED'
            reason = $reason
            distribution_status = 'NOT_PREPARED'
            errors = @('No fue posible obtener una respuesta válida del orquestador.')
        }
    }
}

$response | ConvertTo-Json -Depth 40 -Compress
