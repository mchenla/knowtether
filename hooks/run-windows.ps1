param([Parameter(Mandatory = $true)][string]$Event)

$ErrorActionPreference = 'Stop'
try {
    $pluginRoot = $env:PLUGIN_ROOT
    if (-not $pluginRoot) { $pluginRoot = $env:CLAUDE_PLUGIN_ROOT }
    if (-not $pluginRoot) { throw 'Plugin root is unavailable' }
    $entry = Join-Path $pluginRoot 'hooks\plugin_entry.py'
    # Legacy fallback; the generated host command uses run-windows.cmd.
    # Check exact executable names in PATH order; no command text is constructed.
    $searchDirectories = $env:PATH -split [IO.Path]::PathSeparator
    foreach ($candidate in @('python.exe', 'python3.exe', 'py.exe')) {
        foreach ($directory in $searchDirectories) {
            if (-not $directory) { continue }
            $executable = [IO.Path]::Combine($directory.Trim('"'), $candidate)
            if (-not [IO.File]::Exists($executable)) { continue }
            $prefix = @()
            if ($candidate -eq 'py.exe') { $prefix = @('-3') }
            & $executable @prefix -B $entry $Event
            if ($LASTEXITCODE -eq 3) { continue } # Version rejected before stdin reads.
            exit 0
        }
    }
    [Console]::Out.WriteLine('{"systemMessage":"[KnowTether PYTHON_REQUIRED] Install Python 3.10+ on PATH, then start a new session. Hook skipped."}')
} catch {
    [Console]::Out.WriteLine('{"systemMessage":"[KnowTether CHECK_SKIPPED] Plugin environment is unavailable; hook skipped."}')
}
exit 0
