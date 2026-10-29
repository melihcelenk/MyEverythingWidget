<#
.SYNOPSIS
    Runs the UI tests inside Windows Sandbox so they never touch the developer's mouse, keyboard or windows.

.DESCRIPTION
    1. Publishes the app and the UI tests as self-contained x64 folders (no runtime install needed in the sandbox).
    2. Writes a .wsb configuration that maps tmp\sandbox to C:\mew and runs the tests at logon.
    3. Starts Windows Sandbox, waits for the result files, then prints the summary.
    The script closes the sandbox itself as soon as the results are written; no user action is needed.

.PARAMETER Filter
    Optional xunit query filter, for example "/*/*/MainWindowTests/*".

.PARAMETER TimeoutMinutes
    How long to wait for the sandbox to report results.

.EXAMPLE
    pwsh scripts/test-ui.ps1
#>
[CmdletBinding()]
param(
    [string] $Filter = "",
    [int] $TimeoutMinutes = 15
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$work = Join-Path $repoRoot "tmp\sandbox"
$appOut = Join-Path $work "app"
$testsOut = Join-Path $work "tests"
$results = Join-Path $work "results"
$runner = Join-Path $work "runner"
$msixOut = Join-Path $work "msix"
$sandboxRoot = "C:\mew"

function Invoke-Checked([string] $description, [scriptblock] $command) {
    Write-Host "==> $description"
    & $command
    if ($LASTEXITCODE -ne 0) { throw "$description failed with exit code $LASTEXITCODE" }
}

if (Get-Process -Name "WindowsSandbox*" -ErrorAction SilentlyContinue) {
    throw "Windows Sandbox is already running; close it first (only one sandbox can run at a time)."
}

Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $appOut, $testsOut, $results, $runner | Out-Null

$env:DOTNET_CLI_UI_LANGUAGE = "en"
Invoke-Checked "Publish app" {
    dotnet publish (Join-Path $repoRoot "src\MyEverythingWidget.App") -c Release -r win-x64 -p:Platform=x64 -o $appOut --nologo -v quiet
}
Invoke-Checked "Publish UI tests" {
    dotnet publish (Join-Path $repoRoot "tests\MyEverythingWidget.UiTests") -c Release -r win-x64 -p:Platform=x64 --self-contained -o $testsOut --nologo -v quiet
}

Write-Host "==> Build MSIX"
& (Join-Path $PSScriptRoot "publish-msix.ps1") -Platform x64 -OutputDirectory $msixOut | Out-Null

# Installs the unsigned package inside the sandbox and writes its Application User Model ID for the tests.
@'
$package = Get-ChildItem -Path "C:\mew\msix" -Recurse -Filter "*.msix" | Select-Object -First 1
Add-AppxPackage -AllowUnsigned -Path $package.FullName
$installed = Get-AppxPackage -Name "MyEverythingWidget"
"$($installed.PackageFamilyName)!App" | Set-Content -Encoding ascii "C:\mew\results\aumid.txt"
'@ | Set-Content -Encoding utf8 (Join-Path $runner "install-msix.ps1")

$filterArgument = if ($Filter) { "-filter `"$Filter`"" } else { "" }
@"
@echo off
set MEW_UI_TEST_SANDBOX=1
set MEW_APP_EXE=$sandboxRoot\app\MyEverythingWidget.exe
powershell -NoProfile -ExecutionPolicy Bypass -File "$sandboxRoot\runner\install-msix.ps1" > "$sandboxRoot\results\install.txt" 2>&1
if not exist "$sandboxRoot\results\aumid.txt" (
  echo MSIX install failed; see install.txt > "$sandboxRoot\results\console.txt"
  echo 2 > "$sandboxRoot\results\exitcode.txt"
  exit /b 2
)
set /p MEW_APP_AUMID=<"$sandboxRoot\results\aumid.txt"
"$sandboxRoot\tests\MyEverythingWidget.UiTests.exe" -noColor -result-xml "$sandboxRoot\results\results.xml" $filterArgument > "$sandboxRoot\results\console.txt" 2>&1
echo %ERRORLEVEL% > "$sandboxRoot\results\exitcode.txt"
"@ | Set-Content -Encoding ascii (Join-Path $runner "run.cmd")

$wsbPath = Join-Path $work "ui-tests.wsb"
@"
<Configuration>
  <Networking>Disable</Networking>
  <vGPU>Enable</vGPU>
  <ClipboardRedirection>Disable</ClipboardRedirection>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>$work</HostFolder>
      <SandboxFolder>$sandboxRoot</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>cmd.exe /c $sandboxRoot\runner\run.cmd</Command>
  </LogonCommand>
</Configuration>
"@ | Set-Content -Encoding utf8 $wsbPath

Write-Host "==> Starting Windows Sandbox"
Start-Process -FilePath "WindowsSandbox.exe" -ArgumentList "`"$wsbPath`"" -WindowStyle Minimized

$exitCodeFile = Join-Path $results "exitcode.txt"
$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
while (-not (Test-Path $exitCodeFile) -and (Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 5
}

if (-not (Test-Path $exitCodeFile)) {
    Get-Process -Name "WindowsSandbox*" -ErrorAction SilentlyContinue | Stop-Process -Force
    throw "No result from the sandbox within $TimeoutMinutes minutes; partial output is in $results"
}

# Close the sandbox from the host as soon as results exist. Shutting the guest down from inside would leave
# the Sandbox window on a "closed" screen that waits for the user to click Close.
Start-Sleep -Seconds 1
Get-Process -Name "WindowsSandbox*" -ErrorAction SilentlyContinue | Stop-Process -Force

$consoleFile = Join-Path $results "console.txt"
if (Test-Path $consoleFile) { Get-Content $consoleFile }
$testExitCode = [int](Get-Content $exitCodeFile).Trim()
Write-Host "==> UI tests exit code: $testExitCode (results: $results)"
exit $testExitCode
