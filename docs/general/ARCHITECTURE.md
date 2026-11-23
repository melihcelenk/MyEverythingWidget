# Architecture

## Layers

```
MyEverythingWidget.App  ──>  MyEverythingWidget.Presentation  ──>  MyEverythingWidget.Core
   (WinUI, windowing)          (ViewModels, MVVM)                    (models, rules, storage, service interfaces)
          │                                                                  ▲
          └──────────>  MyEverythingWidget.Infrastructure  ──────────────────┘
                          (Windows shell: installed apps, icons, launching)
```

| Project | May reference | Must not reference |
|---------|---------------|--------------------|
| Core | .NET base library, `Microsoft.Extensions.Logging.Abstractions`, `WidgetFamily` | WinUI, Windows APIs, Presentation, App |
| Presentation | Core, CommunityToolkit.Mvvm | WinUI, Windows APIs, App |
| Infrastructure | Core, Windows SDK projections (COM, WinRT) | WinUI, Presentation, App |
| App | Core, Presentation, Infrastructure, Windows App SDK | — |

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

## Widget family

My Everything Widget is the hub of a family of widgets (MEW-5). The shared contract and its library live in the
[WidgetFamily](https://github.com/melihcelenk/WidgetFamily) repository, included as the `external/WidgetFamily`
git submodule (`docs/CONTRACT.md` there).

| Part | Where | What it does |
|------|-------|--------------|
| Hub pipe | `App.StartFamilyHub` (`HubServer`) | Runs while the app runs; members leave the taskbar while they are connected |
| Members | `Infrastructure/Family/AppExtensionFamilyCatalog` | Finds installed members through the app extension `com.melihcelenk.widgetfamily` (packaged app only) |
| Edges | `Core/Family/EdgeAssignment` | Preferred edge; a taken edge passes to the next free one clockwise, first installed first |
| Menu | `Presentation/FamilyMenuViewModel`, `MainWindow.Family.cs` | Right-click on the compact icon shows the members on its four sides; a click opens one there |
| Opening | `Infrastructure/Family/UriFamilyLauncher` | Launches the member's `open` URI with the icon's bounds |
| Following | `FamilyMenuViewModel.FollowAsync` / `SetHiddenAsync` | Opened members move with the dragged icon and hide with it for full-screen apps |

## Data folder

| How the app runs | Folder |
|------------------|--------|
| MSIX (Store) | Package `LocalState` |
| Unpackaged | `%LOCALAPPDATA%\MyEverythingWidget.WinUI` |
| Tests | `MEW_DATA_DIR` environment variable |

| File | Content |
|------|---------|
| `settings.json` | Window position, always-on-top, theme, grid size, compact mode |
| `state.json` | Categories and items (versioned; corrupt files kept as `state.corrupt-*.json`) |
| `icons\*.png` | App card icons (64 px) |
| `logs\crash.log` | Unhandled exceptions |
