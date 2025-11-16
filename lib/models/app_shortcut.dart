/// Application shortcut model
/// Represents a launchable application or URL
class AppShortcut {
  final String id;
  final String name;
  final String iconPath;
  final String target;
  final String category;
  final LaunchType type;

  const AppShortcut({
    required this.id,
    required this.name,
    required this.iconPath,
    required this.target,
    required this.category,
    required this.type,
  });
}

/// Type of application launch
enum LaunchType {
  /// Windows executable
  exe,

  /// Web URL
  url,

  /// Folder path
  folder,
}
