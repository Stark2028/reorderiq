$ErrorActionPreference = 'Stop'
$reorderProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Set-Location -LiteralPath $reorderProjectRoot
$reorderBuildTarget = [System.IO.Path]::GetFullPath((Join-Path $reorderProjectRoot 'build'))
if (Test-Path -LiteralPath $reorderBuildTarget) {
    $reorderResolvedBuild = (Resolve-Path -LiteralPath $reorderBuildTarget).ProviderPath
    $reorderBuildItem = Get-Item -LiteralPath $reorderResolvedBuild
    if ($reorderResolvedBuild -ne $reorderBuildTarget -or
        -not $reorderResolvedBuild.StartsWith($reorderProjectRoot + [System.IO.Path]::DirectorySeparatorChar) -or
        ($reorderBuildItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw 'Refusing to clean an unexpected build path.'
    }
    # Only generated setuptools output, verified inside this project, is removed.
    Remove-Item -LiteralPath $reorderResolvedBuild -Recurse -Force
}
$reorderBuildPython = Join-Path $reorderProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $reorderBuildPython)) { $reorderBuildPython = 'python' }
& $reorderBuildPython -m pip wheel --no-deps --no-cache-dir --disable-pip-version-check --wheel-dir .local/wheels .
if ($LASTEXITCODE -ne 0) { throw 'Distribution build failed.' }
