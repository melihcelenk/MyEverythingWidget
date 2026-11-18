# My Everything Widget

[![CI](https://github.com/melihcelenk/MyEverythingWidget/actions/workflows/ci.yml/badge.svg)](https://github.com/melihcelenk/MyEverythingWidget/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A small Windows widget that keeps your apps, websites, notes and pictures one click away.

![Everything you love, one click away: apps, websites, notes and photos on your desktop](docs/images/store-1.png)

![Copy it. Ctrl+V. Saved in a second: pictures, text and web links](docs/images/store-2.png)

![Always at hand, always on top: a small icon that opens the widget](docs/images/store-3.png)

## Features

- **A grid that stays put.** Drag cards anywhere on a fixed 5x5 grid; nothing slides around on its own. Dropping on
  another card swaps them; notes and images can span up to 3x3 cells.
- **Apps with their own icons.** Pick from the installed apps (desktop and Store), type a path or web address, or drop
  a file, folder or link on the widget. Change or reset a card's icon from its menu.
- **Notes and images.** Write a note, paste text or a screenshot with Ctrl+V, copy a note back with one click.
- **Categories.** Tabs you can add, rename, delete and reorder; move cards between them.
- **Windows 11 look.** Light and dark theme (or follow Windows), Mica, always on top.
- **Private.** Everything stays on your PC ([privacy policy](docs/general/PRIVACY_POLICY.md)).

## Development

Built with WinUI 3 and .NET 10. See the [Development Guide](docs/general/DEVELOPMENT.md) and
[Architecture](docs/general/ARCHITECTURE.md).

```
dotnet test                    # unit tests (Core, Presentation, Infrastructure)
pwsh scripts/test-ui.ps1       # UI tests in Windows Sandbox
pwsh scripts/publish-msix.ps1  # MSIX package
```

Publishing: [Store Submission](docs/general/STORE_SUBMISSION.md).

### Previous version

The original Python/PySide6 version is in [`legacy/`](legacy/README.md). Its data is imported automatically the first
time this version starts.

## Contributing

Bug reports, ideas and pull requests are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md). Please report security
problems privately as described in [SECURITY.md](SECURITY.md).

## License

MIT, see [LICENSE](LICENSE).
