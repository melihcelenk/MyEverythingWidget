<#
.SYNOPSIS
    Signs a copy of the Store package with a local test certificate, so it can be installed and tried on this PC.

.DESCRIPTION
    Windows does not install an unsigned package that runs a full-trust .exe, and the Store signs the real package
    only during certification. This script:
    1. Creates (once) a self-signed code-signing certificate in CurrentUser\My whose subject is the Store publisher
       from src\MyEverythingWidget.App\StoreIdentity.json, so the package identity stays exactly the Store one.
    2. Copies the Store package to tmp\local-signed and signs the copy; the original stays unsigned for the Store.
    3. Exports the certificate to tmp\local-signed\local-test.cer and prints the two commands to run as administrator.
    The certificate only works on this PC and only for local testing.

.PARAMETER Package
    The Store .msix to sign; defaults to the x64 package under tmp\store-x64.

.EXAMPLE
    pwsh scripts/publish-msix.ps1 -Platform x64 -Store -OutputDirectory tmp\store-x64
    pwsh scripts/sign-local-test.ps1
#>
[CmdletBinding()]
param(
    [string] $Package = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$identity = Get-Content (Join-Path $repoRoot "src\MyEverythingWidget.App\StoreIdentity.json") -Raw | ConvertFrom-Json

if (-not $Package) {
    $Package = Get-ChildItem (Join-Path $repoRoot "tmp\store-x64") -Recurse -Filter "*.msix" | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $Package -or -not (Test-Path $Package)) {
    throw "No Store package found; build it first: pwsh scripts/publish-msix.ps1 -Platform x64 -Store -OutputDirectory tmp\store-x64"
}

$signTool = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin\*\x64\signtool.exe" -ErrorAction SilentlyContinue |
    Sort-Object FullName | Select-Object -Last 1 -ExpandProperty FullName
if (-not $signTool) { throw "signtool.exe not found; install the Windows SDK." }

$certificate = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq $identity.publisher -and $_.HasPrivateKey } |
    Select-Object -First 1
if (-not $certificate) {
    Write-Host "==> Creating the local test certificate $($identity.publisher)"
    $certificate = New-SelfSignedCertificate -Type Custom -Subject $identity.publisher `
        -KeyUsage DigitalSignature -FriendlyName "My Everything Widget local test" `
        -CertStoreLocation Cert:\CurrentUser\My `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
}

$output = Join-Path $repoRoot "tmp\local-signed"
New-Item -ItemType Directory -Force $output | Out-Null
$signed = Join-Path $output (Split-Path $Package -Leaf)
Copy-Item $Package $signed -Force
& $signTool sign /fd SHA256 /sha1 $certificate.Thumbprint $signed | Out-Null
if ($LASTEXITCODE -ne 0) { throw "signtool failed with exit code $LASTEXITCODE" }

$cer = Join-Path $output "local-test.cer"
Export-Certificate -Cert $certificate -FilePath $cer | Out-Null

Write-Host "==> Signed copy: $signed"
Write-Host "==> Run these in a PowerShell window opened as administrator:"
Write-Host "    Import-Certificate -FilePath `"$cer`" -CertStoreLocation Cert:\LocalMachine\TrustedPeople"
Write-Host "    Add-AppxPackage `"$signed`""
