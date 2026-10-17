param([Parameter(Mandatory = $true)][string]$Event)

$ErrorActionPreference = 'Stop'
try {
    $pluginRoot = $env:PLUGIN_ROOT
    if (-not $pluginRoot) { $pluginRoot = $env:CLAUDE_PLUGIN_ROOT }
    if (-not $pluginRoot) { throw 'Plugin root is unavailable' }
    $entry = Join-Path $pluginRoot 'hooks\plugin_entry.py'
    foreach ($candidate in @('python', 'python3', 'py')) {
        $executable = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $executable) { continue }
        $prefix = @()
        if ($candidate -eq 'py') { $prefix = @('-3') }
        & $executable.Source @prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' *> $null
        if ($LASTEXITCODE -ne 0) { continue }
        & $executable.Source @prefix -B $entry $Event
        exit 0
    }
    [Console]::Out.WriteLine('{"systemMessage":"[KnowTether PYTHON_REQUIRED] Install Python 3.10+ on PATH, then start a new session. Hook skipped."}')
} catch {
    [Console]::Out.WriteLine('{"systemMessage":"[KnowTether CHECK_SKIPPED] Plugin environment is unavailable; hook skipped."}')
}
exit 0
