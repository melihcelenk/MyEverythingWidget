# Development Guide

## Requirements

| Tool | Version | Note |
|------|---------|------|
| Windows | 10 (19041) or 11 | Windows 11 Pro or Enterprise for Windows Sandbox |
| .NET SDK | 10.0.400 or later | Pinned by `global.json` |
| Windows Sandbox | Optional feature | Needed only for UI tests |

Visual Studio is not required; everything below runs from the command line.

Enable Windows Sandbox once (administrator PowerShell, then restart):

```
Enable-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" -All
```

## Build and run

```
pwsh scripts/run.ps1
```

The script closes a running instance (its settings are saved as on Close), builds Debug x64 and starts the app.
`-NoBuild` starts the last build. By hand:

```
dotnet build src/MyEverythingWidget.App -r win-x64 -p:Platform=x64
src\MyEverythingWidget.App\bin\x64\Debug\net10.0-windows10.0.26100.0\win-x64\MyEverythingWidget.exe
```

- Development builds are unpackaged and self-contained.
- Data goes to `%LOCALAPPDATA%\MyEverythingWidget.WinUI`. Set `MEW_DATA_DIR` to use another folder.
- Unhandled exceptions are written to `logs\crash.log` in the data folder.

## Tests

### Unit tests

```
dotnet test
```

Runs `Core.Tests` and `Presentation.Tests` (xunit.v3 on Microsoft Testing Platform). They need no WinUI runtime.

### UI tests (Windows Sandbox)

```
pwsh scripts/test-ui.ps1
pwsh scripts/test-ui.ps1 -Filter "/*/*/MainWindowTests/*"
```

What the script does:

1. Publishes the app and the UI tests as self-contained folders, and builds the MSIX package.
2. Starts Windows Sandbox (window moved off-screen; a minimized window drops mouse input) with `tmp\sandbox` mapped to `C:\mew`.
3. Inside the sandbox: installs the MSIX unsigned, runs the FlaUI tests, writes results.
4. Closes the sandbox from the host as soon as results exist (no "Close" click needed), prints the summary and
   exits with the test exit code.

| File | Content |
|------|---------|
| `tmp\sandbox\results\console.txt` | Test console output |
| `tmp\sandbox\results\results.xml` | xunit XML results |
| `tmp\sandbox\results\install.txt` | MSIX install output |
| `tmp\sandbox\results\shots\*.png` | Screenshots for review (`ScreenshotTests`, theme tests) and of failures |
| `tmp\sandbox\results\shots\performance.txt` | Start time and idle memory (`PerformanceTests`) |

UI tests find elements by `AutomationProperties.AutomationId`; give every interactive element one.

### README and Store screenshots

```
pwsh scripts/capture-screenshots.ps1               # take them in the sandbox and lay them out (~3 min)
pwsh scripts/capture-screenshots.ps1 -SkipCapture  # lay out the last captures again
```

`ShowcaseScreenshots` (trait `Category=Showcase`, skipped by the normal UI test run) seeds realistic, made-up
content, switches the sandbox desktop to a plain colour and captures the windows. The script puts each capture on a
1366x768 page with its caption and writes `docs/images/showcase-<n>.png`. The pictures shown inside the widget (an
error screen, a chart) are in `tests/MyEverythingWidget.UiTests/Showcase/`.
Tests that rely on the system drag-and-drop loop (TabView reordering) carry `[Trait("Isolation", "OwnProcess")]`;
the runner executes them first, in their own test process (see `docs/tasks/MEW-4/PHASE7.md`, 7.6.2).
They wait by polling (`Wait.Until`), never with fixed sleeps.

## MSIX package

```
pwsh scripts/publish-msix.ps1 -Platform x64
```

- Produces an unsigned package under `tmp\msix`.
- Install it locally with `Add-AppxPackage -AllowUnsigned <path>`.
- The manifest publisher is the unsigned-package OID. Store association replaces it (MEW-4 Faz 8).
