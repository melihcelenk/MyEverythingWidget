<#
.SYNOPSIS
    Builds the app and starts it for manual testing.

.DESCRIPTION
    1. Closes a running instance (as if its Close button were pressed, so it saves its settings).
    2. Builds the Debug x64 app.
    3. Starts it unpackaged; data goes to %LOCALAPPDATA%\MyEverythingWidget.WinUI.

.PARAMETER NoBuild
    Starts the last build without building first.

.EXAMPLE
    pwsh scripts/run.ps1
    pwsh scripts/run.ps1 -NoBuild
#>
[CmdletBinding()]
param(
    [switch] $NoBuild
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$project = Join-Path $repoRoot "src\MyEverythingWidget.App"
$exe = Join-Path $project "bin\x64\Debug\net10.0-windows10.0.26100.0\win-x64\MyEverythingWidget.exe"
$closeTimeoutMs = 10000

Get-Process MyEverythingWidget -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "==> Closing the running app (process $($_.Id))"
    [void]$_.CloseMainWindow()
    if (-not $_.WaitForExit($closeTimeoutMs)) { Stop-Process -Id $_.Id -Force }
}

if (-not $NoBuild) {
    Write-Host "==> Build"
    $env:DOTNET_CLI_UI_LANGUAGE = "en"
    dotnet build $project -p:Platform=x64 -v q --nologo
    if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }
}

if (-not (Test-Path $exe)) { throw "No build found at $exe; run without -NoBuild." }

Write-Host "==> Start"
Start-Process $exe
