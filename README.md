# My Everything Widget

A small Windows widget that keeps your apps, notes and images one click away.

> **Status:** being rewritten with WinUI and .NET 10 for the Microsoft Store (MEW-4).
> The original Python/PySide6 version is in [`legacy/`](legacy/README.md).

## Features (planned for the first Store release)

- Fixed grid of apps, notes and images that stays exactly where you put it
- Add apps from the list of installed apps, with their own icons
- Paste anything with Ctrl+V: screenshots, image files, links, text
- Category tabs
- Always on top
- Follows the Windows light/dark theme

## Development

See the [Development Guide](docs/general/DEVELOPMENT.md).

```
dotnet test                    # unit tests
pwsh scripts/test-ui.ps1       # UI tests in Windows Sandbox
```

## License

MIT, see [LICENSE](LICENSE).
