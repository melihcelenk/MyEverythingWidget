# Architecture

## Layers

```
MyEverythingWidget.App  ──>  MyEverythingWidget.Presentation  ──>  MyEverythingWidget.Core
   (WinUI, windowing)          (ViewModels, MVVM)                    (models, rules, storage)
```

| Project | May reference | Must not reference |
|---------|---------------|--------------------|
| Core | .NET base library, `Microsoft.Extensions.Logging.Abstractions` | WinUI, Windows APIs, Presentation, App |
| Presentation | Core, CommunityToolkit.Mvvm | WinUI, Windows APIs, App |
| App | Core, Presentation, Windows App SDK | — |

## Rules

- **Decisions live in Core; App only applies them.**
  - Example: `WindowPlacement.Resolve` decides where the window opens.
  - `MainWindow` reads the monitors and moves the window.
- **ViewModels expose state and commands only.**
  - Code-behind may subscribe to them to apply window-level state, such as always-on-top or bounds.
  - Code-behind holds no business logic.
- **Storage is atomic.**
  - Write a temporary file, then replace the real one.
  - A file that cannot be parsed is kept as `*.corrupt-{timestamp}.json`, never overwritten.
- **Single instance.**
  - `Program.Main` registers an `AppInstance` key.
  - A second launch redirects its activation to the running instance and exits.

## Data folder

| How the app runs | Folder |
|------------------|--------|
| MSIX (Store) | Package `LocalState` |
| Unpackaged | `%LOCALAPPDATA%\MyEverythingWidget.WinUI` |
| Tests | `MEW_DATA_DIR` environment variable |

| File | Content |
|------|---------|
| `settings.json` | Window bounds and always-on-top |
| `logs\crash.log` | Unhandled exceptions |
