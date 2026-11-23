<#
.SYNOPSIS
    Builds an unsigned MSIX of a widget family member (Task Timer Widget) for the sandbox UI tests (MEW-5).

.DESCRIPTION
    The member's manifest gets the "unsigned package" publisher for this build only (restored afterwards), so the
    package installs in Windows Sandbox with Add-AppxPackage -AllowUnsigned. The package is self-contained (.NET and
    Windows App SDK inside) because the sandbox has no network to install frameworks.

.PARAMETER MemberRepository
    The member's repository; defaults to TaskTimerWidget next to this repository.

.PARAMETER OutputDirectory
    Where the package folder is written; defaults to tmp\member-msix.

.EXAMPLE
    pwsh scripts/build-member-msix.ps1
    pwsh scripts/build-member-msix.ps1 -MemberRepository C:\Kodlar\TaskTimerWidget
#>
[CmdletBinding()]
param(
    [string] $MemberRepository = "",
    [string] $OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $MemberRepository) { $MemberRepository = Join-Path (Split-Path -Parent $repoRoot) "TaskTimerWidget" }
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $repoRoot "tmp\member-msix" }
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory, (Get-Location).Path)
$project = Join-Path $MemberRepository "src\TaskTimerWidget\TaskTimerWidget.csproj"
if (-not (Test-Path $project)) { throw "Family member project not found: $project" }

# The same unsigned-package publisher as this app's development manifest.
$unsignedPublisher = "CN=TaskTimerWidget, OID.2.25.311729368913984317654407730594956997722=1"

Remove-Item -Recurse -Force $OutputDirectory -ErrorAction SilentlyContinue
$env:DOTNET_CLI_UI_LANGUAGE = "en"
$manifestPath = Join-Path (Split-Path -Parent $project) "Package.appxmanifest"
# Kept as bytes so the restore keeps the file exactly as it was (byte order mark included).
$originalManifest = [System.IO.File]::ReadAllBytes($manifestPath)
try {
    [xml] $manifest = [System.IO.File]::ReadAllText($manifestPath)
    $manifest.Package.Identity.Publisher = $unsignedPublisher
    $manifest.Save($manifestPath)

    dotnet publish $project `
        -c Release -r win-x64 -p:Platform=x64 `
        -p:SelfContained=true `
        -p:WindowsAppSDKSelfContained=true `
        -p:GenerateAppxPackageOnBuild=true `
        -p:AppxBundle=Never `
        -p:AppxPackageSigningEnabled=false `
        -p:AppxSymbolPackageEnabled=false `
        -p:AppxPackageDir="$OutputDirectory\" `
        --nologo -v quiet
    if ($LASTEXITCODE -ne 0) { throw "Member MSIX publish failed with exit code $LASTEXITCODE" }
}
finally {
    [System.IO.File]::WriteAllBytes($manifestPath, $originalManifest)
}

$package = Get-ChildItem -Path $OutputDirectory -Recurse -Filter "*.msix" | Select-Object -First 1
if (-not $package) { throw "No .msix produced under $OutputDirectory" }
Write-Host "==> Member package: $($package.FullName)"
$package.FullName
