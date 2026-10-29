<#
.SYNOPSIS
    Builds the MSIX package of the app.

.DESCRIPTION
    Produces an unsigned package that installs locally with Add-AppxPackage -AllowUnsigned.
    Store submission (signing by the Store, Partner Center publisher identity) is set up in MEW-4 Faz 8.

.PARAMETER Platform
    x64 or ARM64.

.PARAMETER OutputDirectory
    Where the package folder is written; defaults to tmp\msix.

.EXAMPLE
    pwsh scripts/publish-msix.ps1 -Platform x64
#>
[CmdletBinding()]
param(
    [ValidateSet("x64", "ARM64")]
    [string] $Platform = "x64",
    [string] $OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $repoRoot "tmp\msix" }
$runtime = "win-$($Platform.ToLowerInvariant())"

Remove-Item -Recurse -Force $OutputDirectory -ErrorAction SilentlyContinue
$env:DOTNET_CLI_UI_LANGUAGE = "en"
dotnet publish (Join-Path $repoRoot "src\MyEverythingWidget.App") `
    -c Release -r $runtime -p:Platform=$Platform `
    -p:WindowsPackageType=MSIX `
    -p:GenerateAppxPackageOnBuild=true `
    -p:AppxPackageSigningEnabled=false `
    -p:AppxSymbolPackageEnabled=false `
    -p:AppxPackageDir="$OutputDirectory\" `
    --nologo -v quiet
if ($LASTEXITCODE -ne 0) { throw "MSIX publish failed with exit code $LASTEXITCODE" }

$package = Get-ChildItem -Path $OutputDirectory -Recurse -Filter "*.msix" | Select-Object -First 1
if (-not $package) { throw "No .msix produced under $OutputDirectory" }
Write-Host "==> Package: $($package.FullName)"
$package.FullName
