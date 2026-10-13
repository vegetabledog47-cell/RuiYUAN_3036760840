param([string]$InputCsv = '')
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$oldPythonPath = $env:PYTHONPATH
try {
    $venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venvPython) { $pythonCommand = $venvPython }
    else {
        $pythonCommand = 'python'
        # Optional isolated dependencies installed in this Codex workspace.
        $workspacePackages = Join-Path (Split-Path (Split-Path $projectRoot -Parent) -Parent) 'work\python_packages'
        if (Test-Path -LiteralPath $workspacePackages) {
            $env:PYTHONPATH = $workspacePackages + [IO.Path]::PathSeparator + $oldPythonPath
        }
    }
    $replicationScript = Join-Path $projectRoot 'src\replicate.py'
    if ($InputCsv) { & $pythonCommand $replicationScript --input $InputCsv }
    else { & $pythonCommand $replicationScript }
    if ($LASTEXITCODE -ne 0) { throw "Replication failed (exit $LASTEXITCODE)." }
} finally {
    $env:PYTHONPATH = $oldPythonPath
}
