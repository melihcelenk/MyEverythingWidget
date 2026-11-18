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

.PARAMETER Store
    Builds the package for the Microsoft Store: the manifest gets the product identity and version from
    src\MyEverythingWidget.App\StoreIdentity.json for this build only and is restored afterwards. Without it the
    package keeps the unsigned test identity that local and sandbox builds install.

.EXAMPLE
    pwsh scripts/publish-msix.ps1 -Platform x64
    pwsh scripts/publish-msix.ps1 -Platform ARM64 -OutputDirectory tmp\msix-arm64
    pwsh scripts/publish-msix.ps1 -Platform x64 -Store -OutputDirectory tmp\store-x64
#>
[CmdletBinding()]
param(
    [ValidateSet("x64", "ARM64")]
    [string] $Platform = "x64",
    [string] $OutputDirectory = "",
    [switch] $Store
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$project = Join-Path $repoRoot "src\MyEverythingWidget.App"
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $repoRoot "tmp\msix" }
# dotnet publish resolves a relative AppxPackageDir against the project folder, so make it absolute first.
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory, (Get-Location).Path)
$runtime = "win-$($Platform.ToLowerInvariant())"

Remove-Item -Recurse -Force $OutputDirectory -ErrorAction SilentlyContinue
$env:DOTNET_CLI_UI_LANGUAGE = "en"

$manifestPath = Join-Path $project "Package.appxmanifest"
$originalManifest = [System.IO.File]::ReadAllText($manifestPath)
if ($Store) {
    $identity = Get-Content (Join-Path $project "StoreIdentity.json") -Raw | ConvertFrom-Json
    [xml] $manifest = $originalManifest
    $manifest.Package.Identity.Name = $identity.name
    $manifest.Package.Identity.Publisher = $identity.publisher
    $manifest.Package.Identity.Version = $identity.version
    $manifest.Package.Properties.PublisherDisplayName = $identity.publisherDisplayName
    $manifest.Save($manifestPath)
    Write-Host "==> Store identity: $($identity.name), $($identity.publisher), $($identity.version)"
}

try {
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
}
finally {
    # The manifest in the repository always keeps the test identity.
    [System.IO.File]::WriteAllText($manifestPath, $originalManifest)
}

$package = Get-ChildItem -Path $OutputDirectory -Recurse -Filter "*.msix" | Select-Object -First 1
if (-not $package) { throw "No .msix produced under $OutputDirectory" }
Write-Host "==> Package: $($package.FullName)"
$package.FullName
