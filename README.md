# MyEverythingWidget

A lightweight desktop widget for Windows and Ubuntu that provides quick access to applications and note-taking functionality.

## 🎯 Features (v1.0 MVP - In Development)

- 📱 **Application Launcher** - Quick access to your favorite apps with icon grid
- 📝 **Note-taking** - Create and manage notes with copy-to-clipboard functionality
- 📋 **Clipboard Paste** - Paste text and images directly with Ctrl+V
- 🏷️ **Category Tabs** - Organize apps and notes into categories (Music, Notes, AI)
- 🪟 **Always-on-top** - Keep the widget visible while working
- 🎨 **Modern UI** - Clean Material Design interface

## 🚀 Getting Started

### Prerequisites

- Flutter 3.x or higher
- Windows 10/11 or Ubuntu (Linux)
- Visual Studio 2022 (for Windows development)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/MyEverythingWidget.git
   cd MyEverythingWidget
   ```

2. **Install dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run the app:**
   ```bash
   flutter run -d windows
   # or
   flutter run -d linux
   ```

## 🛠️ Technology Stack

- **Framework:** Flutter 3.x Desktop
- **Language:** Dart
- **State Management:** Provider
- **Packages:**
  - `window_manager` - Window management
  - `provider` - State management
  - `clipboard_watcher` - Clipboard functionality
  - `url_launcher` - Open URLs
  - `path_provider` - Local storage

## 📦 Building for Distribution

### Windows (MSIX)
```bash
flutter build windows --release
flutter pub run msix:create
```

### Linux (Snap)
```bash
snapcraft
```

## 🗺️ Roadmap

- [x] **v1.0 (Current)** - MVP with core features
- [ ] **v1.1** - Application picker, settings page, system tray
- [ ] **v1.2** - Command runner, global hotkeys, search
- [ ] **v2.0** - Cloud sync, AI integration, plugins

## 🤝 Contributing

Contributions are welcome!

**Development Guidelines:**
- Follow Flutter/Dart style guidelines
- Write clean, self-documenting code
- Add tests for new features
- Update documentation for API changes

**Commit Format:** `[MEW-X] Description`
**Example:** `[MEW-1] Setup Flutter project structure`

## 📝 License

This project is open source and available under the MIT License.

## 📚 Documentation

- [Technical Analysis](docs/tasks/MEW-1/ANALYSIS.md) - Platform selection and architecture
- [Development Tasks](docs/tasks/MEW-1/TODO.md) - Current development progress

## 🙏 Acknowledgments

Built with [Flutter](https://flutter.dev/) - Google's UI toolkit for beautiful, natively compiled applications.

---

**Status:** 🚧 Active Development
**Platform:** Flutter Desktop
**Package Name:** `my_everything_widget`
