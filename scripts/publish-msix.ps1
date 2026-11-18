<#
.SYNOPSIS
    Builds the MSIX package of the app.

.DESCRIPTION
    Produces one unsigned .msix (all icon scales inside) that installs locally with Add-AppxPackage -AllowUnsigned.
    Store submission is described in docs/general/STORE_SUBMISSION.md.

.PARAMETER Platform
    x64 or ARM64.

.PARAMETER OutputDirectory
    Where the package folder is written; defaults to tmp\msix.

.EXAMPLE
    pwsh scripts/publish-msix.ps1 -Platform x64
    pwsh scripts/publish-msix.ps1 -Platform ARM64 -OutputDirectory tmp\msix-arm64
#>
[CmdletBinding()]
param(
    [ValidateSet("x64", "ARM64")]
    [string] $Platform = "x64",
    [string] $OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$project = Join-Path $repoRoot "src\MyEverythingWidget.App"
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $repoRoot "tmp\msix" }
$runtime = "win-$($Platform.ToLowerInvariant())"

Remove-Item -Recurse -Force $OutputDirectory -ErrorAction SilentlyContinue
$env:DOTNET_CLI_UI_LANGUAGE = "en"

# Clean first: an incremental build may consider the package up to date and skip writing it to the new folder.
dotnet clean $project -c Release -r $runtime -p:Platform=$Platform -p:WindowsPackageType=MSIX --nologo -v quiet
if ($LASTEXITCODE -ne 0) { throw "Clean failed with exit code $LASTEXITCODE" }

dotnet publish $project `
    -c Release -r $runtime -p:Platform=$Platform `
    -p:WindowsPackageType=MSIX `
    -p:GenerateAppxPackageOnBuild=true `
    -p:AppxBundle=Never `
    -p:AppxPackageSigningEnabled=false `
    -p:AppxSymbolPackageEnabled=false `
    -p:AppxPackageDir="$OutputDirectory\" `
    --nologo -v quiet
if ($LASTEXITCODE -ne 0) { throw "MSIX publish failed with exit code $LASTEXITCODE" }

$package = Get-ChildItem -Path $OutputDirectory -Recurse -Filter "*.msix" | Select-Object -First 1
if (-not $package) { throw "No .msix produced under $OutputDirectory" }
Write-Host "==> Package: $($package.FullName)"
$package.FullName
