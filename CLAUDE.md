# Development Guidelines for AI Assistant

My Everything Widget is a Windows desktop widget written with WinUI (Windows App SDK 2.x) and .NET 10, published
to the Microsoft Store. The original Python/PySide6 version lives in `legacy/` with its own `CLAUDE.md`; it is
reference material only.

## Documentation

- **[Development Guide](docs/general/DEVELOPMENT.md)** - Build, run, test (unit and sandbox UI tests), MSIX
- **[Architecture](docs/general/ARCHITECTURE.md)** - Projects, layers and their rules
- **Current task:** `docs/tasks/MEW-4/MAIN_TODO.md` (WinUI rewrite) and its `PHASE{n}.md` files

## Key Principles

### Testing

- **DO NOT** ask the user to test manually; write automated tests and run them.
- Unit tests: `dotnet test` (Core and Presentation; no WinUI runtime needed).
- UI tests: `pwsh scripts/test-ui.ps1` runs them in **Windows Sandbox**.
  - Never run UI tests on the user's desktop.
  - Never drive the user's mouse or keyboard.
- Grid behaviour is specified by `.dsl` files (from `legacy/tests/humanized/`); they are the source of truth.

### Code

- All code, comments, XML docs, log messages and commit messages are in English.
- Build with zero warnings: `TreatWarningsAsErrors` is on for every project.
- Core has no WinUI or Windows dependency.
- ViewModels live in Presentation and do not reference WinUI.
- Code-behind only applies window-level state.
- Colours come from WinUI theme resources only; never hard-code colours.
- Package versions are central in `Directory.Packages.props`.

### Project Structure

| Path | Content |
|------|---------|
| `src/MyEverythingWidget.Core` | Models, grid rules, settings and storage (`net10.0`) |
| `src/MyEverythingWidget.Presentation` | ViewModels (`net10.0`, CommunityToolkit.Mvvm) |
| `src/MyEverythingWidget.Infrastructure` | Windows shell services: installed apps, icons, launching |
| `src/MyEverythingWidget.App` | WinUI app, views, MSIX manifest |
| `tests/` | `Core.Tests`, `Presentation.Tests`, `Infrastructure.Tests`, `UiTests` (FlaUI), `Grid/*.dsl` |
| `scripts/` | `run.ps1` (build and start for manual testing), `test-ui.ps1` (sandbox UI tests), `publish-msix.ps1` |
| `tmp/` | Temporary output (gitignored) |

## Important Notes

1. **Never commit or push** - the user commits.
2. **Test-driven development** - write the test, see it fail, then write the code.
3. App data folder: package `LocalState` (MSIX), `%LOCALAPPDATA%\MyEverythingWidget.WinUI` (unpackaged), or
   `MEW_DATA_DIR` (tests).
