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
echo started > "$sandboxRoot\results\started.txt"
esults\started.txt"
set MEW_UI_TEST_SANDBOX=1
set MEW_UI_TEST_ARTIFACTS=$sandboxRoot\results\shots
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

Add-Type -Namespace SandboxRunner -Name Win32 -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr after, int x, int y, int cx, int cy, uint flags);
'@

# The window must stay open (not minimized): a minimized Sandbox window stops delivering mouse input to the
# guest, which breaks the drag tests. It is moved off-screen instead, so it never covers the user's work.
function Move-SandboxWindowOffScreen {
    $deadline = (Get-Date).AddSeconds(90)
    while ((Get-Date) -lt $deadline) {
        $client = Get-Process -Name "WindowsSandboxRemoteSession" -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero } | Select-Object -First 1
        if ($client) {
            # SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE
            [SandboxRunner.Win32]::SetWindowPos($client.MainWindowHandle, [IntPtr]::Zero, -20000, -20000, 0, 0, 0x0015) | Out-Null
            return
        }
        Start-Sleep -Milliseconds 250
    }
    Write-Warning "Sandbox window not found; it stays where Windows put it."
}

# Close the client window first and the server second; the other order makes the client show a
# "remote session is closing" error dialog that waits for the user.
function Stop-Sandbox {
    foreach ($name in "WindowsSandboxRemoteSession", "WindowsSandboxServer", "WindowsSandbox") {
        Get-Process -Name $name -ErrorAction SilentlyContinue | Stop-Process -Force
        $deadline = (Get-Date).AddSeconds(15)
        while ((Get-Process -Name $name -ErrorAction SilentlyContinue) -and (Get-Date) -lt $deadline) {
            Start-Sleep -Milliseconds 200
        }
    }
}

# Waits until no sandbox process is left, then a little longer: starting a new sandbox while the previous one
# is still tearing down makes Windows Sandbox fail with "remote session is closing".
function Wait-SandboxGone {
    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Process -Name "WindowsSandbox*" -ErrorAction SilentlyContinue) -and (Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 1
    }
    Start-Sleep -Seconds 15
}

# Runs the sandbox once; returns $true when results arrived, $false when the sandbox failed to start or closed early.
function Invoke-SandboxRun {
    Wait-SandboxGone
    Write-Host "==> Starting Windows Sandbox"
    Start-Process -FilePath "WindowsSandbox.exe" -ArgumentList "`"$wsbPath`""
    Move-SandboxWindowOffScreen

    $startedFile = Join-Path $results "started.txt"
    $exitCodeFile = Join-Path $results "exitcode.txt"
    $startDeadline = (Get-Date).AddMinutes(4)
    $deadline = (Get-Date).AddMinutes($TimeoutMinutes)
    while (-not (Test-Path $exitCodeFile) -and (Get-Date) -lt $deadline) {
        if (-not (Get-Process -Name "WindowsSandboxRemoteSession" -ErrorAction SilentlyContinue)) {
            Write-Warning "The sandbox closed before the tests reported results."
            Stop-Sandbox
            return $false
        }
        if (-not (Test-Path $startedFile) -and (Get-Date) -gt $startDeadline) {
            Write-Warning "The sandbox did not start the tests within 4 minutes."
            Stop-Sandbox
            return $false
        }
        Start-Sleep -Seconds 5
    }

    # Results exist (or time ran out): close the sandbox from the host; no user action is needed.
    Start-Sleep -Seconds 1
    Stop-Sandbox
    return (Test-Path $exitCodeFile)
}

$exitCodeFile = Join-Path $results "exitcode.txt"
if (-not (Invoke-SandboxRun)) {
    Write-Host "==> Retrying once"
    Get-ChildItem $results | Remove-Item -Force
    if (-not (Invoke-SandboxRun)) {
        throw "No result from the sandbox; partial output is in $results"
    }
}

$consoleFile = Join-Path $results "console.txt"
if (Test-Path $consoleFile) { Get-Content $consoleFile }
$testExitCode = [int](Get-Content $exitCodeFile).Trim()
Write-Host "==> UI tests exit code: $testExitCode (results: $results)"
exit $testExitCode
