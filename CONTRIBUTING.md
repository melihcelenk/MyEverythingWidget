# Contributing

Thanks for helping to improve My Everything Widget. Bug reports, ideas and pull requests are all welcome.

## Before you start

- **Bugs and ideas:** open an issue with the [bug report or feature request form](../../issues/new/choose).
- **Larger changes:** open an issue first, so we can agree on the approach before you write the code.
- **Security problems:** do not open a public issue; see [SECURITY.md](SECURITY.md).
- Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Build and run

You need Windows 10 (1809) or later, the .NET 10 SDK and PowerShell 7.

```
pwsh scripts/run.ps1           # build and start the widget
dotnet test                    # unit tests (Core, Presentation, Infrastructure)
pwsh scripts/test-ui.ps1       # UI tests, run inside Windows Sandbox
```

The UI tests need the Windows Sandbox feature; they never drive your own mouse or keyboard. The
[Development Guide](docs/general/DEVELOPMENT.md) explains the scripts, and [Architecture](docs/general/ARCHITECTURE.md)
explains the projects and their rules.

## Code

- **Tests first:** write a test that shows the bug or the new behaviour, see it fail, then change the code.
  Grid behaviour is specified by the `.dsl` files in `tests/Grid/`.
- **Zero warnings:** every project builds with `TreatWarningsAsErrors`.
- **Layers:** Core has no WinUI or Windows dependency; ViewModels live in Presentation and do not reference WinUI;
  code-behind only applies window-level state.
- **Look:** colours come from WinUI theme resources only; never hard-code colours.
- **Language:** code, comments, XML docs, log messages and commit messages are in English.
- **Packages:** versions are set centrally in `Directory.Packages.props`.

## Pull requests

1. Fork the repository and create a branch from `master`.
2. Keep the change focused on one issue, and mention it in the description (`Fixes #123`).
3. Make sure `dotnet test` passes and, for UI changes, `pwsh scripts/test-ui.ps1` too.
4. Fill in the pull request template; the CI build runs the unit tests on every pull request.

By contributing you agree that your contribution is licensed under the [MIT License](LICENSE).
