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

## Localization

The app is in English and 14 other languages; it starts in the Windows display language, or English when that
language is not one of them, and Settings can choose another one (the app then restarts).

- **Texts:** every text the user sees lives in `src/MyEverythingWidget.Presentation/Localization/Strings.resx` (English,
  with a comment for translators) and in `Strings.<language>.resx`.
- **Using a text:** code reads it from `Strings` (`Strings.AddNote`, `Strings.AppNotFound(name)`); XAML uses
  `{l:Str Key=AddNote}` with `xmlns:l="using:MyEverythingWidget.App.Localization"`.
- **Adding a text:** add the key to `Strings.resx` and to every `Strings.<language>.resx`, then a property (or a
  method for texts with `{0}`) to `Strings.cs`.
- **The guard:** `LocalizationCoverageTests` fails `dotnet test` when a language misses a key or a placeholder, when
  `Strings.cs` and the resources differ, or when XAML or code shows a hard-coded text.
- **Adding a language:** add it to `AppLanguages.Supported`, add `Strings.<code>.resx`, and add it to
  `Package.appxmanifest` → `Resources`.
- **UI tests:** the sandbox has the host's display language, so `AppSession` sets `MEW_SYSTEM_LANGUAGE=en-US`, which
  stands in for the Windows display language.

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
pwsh scripts/capture-screenshots.ps1        # take the captures in the sandbox, then build the pages (~3 min)
python scripts/compose-store-images.py      # build the pages again from the existing captures (needs Pillow)
```

`ShowcaseScreenshots` (trait `Category=Showcase`, skipped by the normal UI test run) seeds made-up content,
switches the sandbox desktop to a plain colour and captures the windows into `docs/images/captures/`.
`compose-store-images.py` builds `docs/images/store-1.png` … `store-3.png` from them: the cards and windows come from
the captures; captions, callouts, the notes, the picture menu and the taskbar are drawn by the script. Photos and site
icons are in `docs/images/assets/`.

## MSIX package

```
pwsh scripts/publish-msix.ps1 -Platform x64
```

- Produces an unsigned package under `tmp\msix`.
- Install it locally with `Add-AppxPackage -AllowUnsigned <path>`.
- The manifest publisher is the unsigned-package OID. Store association replaces it (MEW-4 Faz 8).
