import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/models/app_shortcut.dart';
import 'package:my_everything_widget/providers/app_state.dart';

void main() {
  group('AppState - Dynamic App Management', () {
    late AppState appState;

    setUp(() {
      appState = AppState();
    });

    test('should add new app to the list', () {
      final initialCount = appState.apps.length;

      const newApp = AppShortcut(
        id: '999',
        name: 'New App',
        iconPath: '',
        target: 'https://example.com',
        category: 'Web',
        type: LaunchType.url,
      );

      appState.addApp(newApp);

      expect(appState.apps.length, initialCount + 1);
      expect(appState.apps.last, newApp);
    });

    test('should notify listeners when app is added', () {
      var notified = false;
      appState.addListener(() {
        notified = true;
      });

      const newApp = AppShortcut(
        id: '999',
        name: 'New App',
        iconPath: '',
        target: 'https://example.com',
        category: 'Web',
        type: LaunchType.url,
      );

      appState.addApp(newApp);

      expect(notified, true);
    });

    test('should filter newly added app by category', () {
      const newApp = AppShortcut(
        id: '999',
        name: 'New Dev Tool',
        iconPath: '',
        target: 'https://example.com',
        category: 'Dev',
        type: LaunchType.url,
      );

      // Select Dev category
      final devCategory = appState.categories.firstWhere((c) => c.name == 'Dev');
      appState.selectCategory(devCategory);

      final initialDevCount = appState.filteredApps.length;
      appState.addApp(newApp);

      expect(appState.filteredApps.length, initialDevCount + 1);
      expect(appState.filteredApps.contains(newApp), true);
    });

    test('should not show newly added app in different category filter', () {
      const newApp = AppShortcut(
        id: '999',
        name: 'New Web App',
        iconPath: '',
        target: 'https://example.com',
        category: 'Web',
        type: LaunchType.url,
      );

      // Select Media category
      final mediaCategory = appState.categories.firstWhere((c) => c.name == 'Media');
      appState.selectCategory(mediaCategory);

      final initialMediaCount = appState.filteredApps.length;
      appState.addApp(newApp);

      // Media count should not change
      expect(appState.filteredApps.length, initialMediaCount);
      expect(appState.filteredApps.contains(newApp), false);
    });

    test('should show newly added app in "All" category', () {
      const newApp = AppShortcut(
        id: '999',
        name: 'New App',
        iconPath: '',
        target: 'https://example.com',
        category: 'Web',
        type: LaunchType.url,
      );

      // Select All category
      final allCategory = appState.categories.firstWhere((c) => c.name == 'All');
      appState.selectCategory(allCategory);

      final initialCount = appState.filteredApps.length;
      appState.addApp(newApp);

      expect(appState.filteredApps.length, initialCount + 1);
      expect(appState.filteredApps.contains(newApp), true);
    });
  });
}

