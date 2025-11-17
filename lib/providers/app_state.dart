import 'package:flutter/foundation.dart';
import '../models/app_shortcut.dart';
import '../models/category.dart';

/// Global application state
/// Manages categories, apps, and selected category
class AppState extends ChangeNotifier {
  final List<AppCategory> _categories = [];
  final List<AppShortcut> _apps = [];
  AppCategory? _selectedCategory;

  List<AppCategory> get categories => List.unmodifiable(_categories);
  List<AppShortcut> get apps => List.unmodifiable(_apps);
  AppCategory? get selectedCategory => _selectedCategory;

  /// Get apps filtered by selected category
  List<AppShortcut> get filteredApps {
    if (_selectedCategory == null || _selectedCategory!.name == 'All') {
      return apps;
    }
    return _apps.where((app) => app.category == _selectedCategory!.name).toList();
  }

  AppState() {
    _loadInitialData();
  }

  void _loadInitialData() {
    // Load categories
    _categories.addAll([
      const AppCategory(id: '1', name: 'All', icon: '📱'),
      const AppCategory(id: '2', name: 'Web', icon: '🌐'),
      const AppCategory(id: '3', name: 'Dev', icon: '💻'),
      const AppCategory(id: '4', name: 'Media', icon: '🎵'),
    ]);

    // Load apps (with various name lengths to test tooltip and truncation)
    _apps.addAll([
      const AppShortcut(
        id: '1',
        name: 'Google Chrome',
        iconPath: '',
        target: 'https://google.com',
        category: 'Web',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '2',
        name: 'GitHub Desktop',
        iconPath: '',
        target: 'https://github.com',
        category: 'Dev',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '3',
        name: 'YouTube Music',
        iconPath: '',
        target: 'https://music.youtube.com',
        category: 'Media',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '4',
        name: 'Spotify Premium',
        iconPath: '',
        target: 'https://spotify.com',
        category: 'Media',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '5',
        name: 'Stack Overflow Community',
        iconPath: '',
        target: 'https://stackoverflow.com',
        category: 'Dev',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '6',
        name: 'Gmail',
        iconPath: '',
        target: 'https://gmail.com',
        category: 'Web',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '7',
        name: 'Visual Studio Code',
        iconPath: '',
        target: 'https://code.visualstudio.com',
        category: 'Dev',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '8',
        name: 'CodePen Playground',
        iconPath: '',
        target: 'https://codepen.io',
        category: 'Dev',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '9',
        name: 'MDN Web Docs',
        iconPath: '',
        target: 'https://developer.mozilla.org',
        category: 'Dev',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '10',
        name: 'Docker Hub Registry',
        iconPath: '',
        target: 'https://hub.docker.com',
        category: 'Dev',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '11',
        name: 'NPM Package Manager',
        iconPath: '',
        target: 'https://npmjs.com',
        category: 'Dev',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '12',
        name: 'Git Version Control',
        iconPath: '',
        target: 'https://git-scm.com',
        category: 'Dev',
        type: LaunchType.url,
      ),
    ]);

    // Set default category
    _selectedCategory = _categories.first;
  }

  void selectCategory(AppCategory category) {
    _selectedCategory = category;
    notifyListeners();
  }

  /// Add a new app to the list
  void addApp(AppShortcut app) {
    _apps.add(app);
    notifyListeners();
  }

  /// Remove an app from the list
  void removeApp(String appId) {
    _apps.removeWhere((app) => app.id == appId);
    notifyListeners();
  }
}
