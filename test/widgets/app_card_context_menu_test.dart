import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/models/app_shortcut.dart';
import 'package:my_everything_widget/widgets/app_card.dart';

void main() {
  group('AppCard Context Menu Tests', () {
    const testApp = AppShortcut(
      id: '1',
      name: 'Test App',
      iconPath: '',
      target: 'https://test.com',
      category: 'Web',
      type: LaunchType.url,
    );

    testWidgets('should show context menu on right click', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppCard(
              app: testApp,
              onTap: () {},
              onEdit: (app) {},
              onRename: (app) {},
            ),
          ),
        ),
      );

      // Right click on the card
      final cardFinder = find.byType(AppCard);
      await tester.tap(cardFinder, buttons: kSecondaryButton);
      await tester.pumpAndSettle();

      // Context menu should appear
      expect(find.text('Open'), findsOneWidget);
      expect(find.text('Edit'), findsOneWidget);
      expect(find.text('Rename'), findsOneWidget);
    });

    testWidgets('should call onTap when Open is selected', (tester) async {
      var openCalled = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppCard(
              app: testApp,
              onTap: () {
                openCalled = true;
              },
              onEdit: (app) {},
              onRename: (app) {},
            ),
          ),
        ),
      );

      // Right click and select Open
      await tester.tap(find.byType(AppCard), buttons: kSecondaryButton);
      await tester.pumpAndSettle();

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      expect(openCalled, true);
    });

    testWidgets('should call onEdit when Edit is selected', (tester) async {
      AppShortcut? editedApp;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppCard(
              app: testApp,
              onTap: () {},
              onEdit: (app) {
                editedApp = app;
              },
              onRename: (app) {},
            ),
          ),
        ),
      );

      // Right click and select Edit
      await tester.tap(find.byType(AppCard), buttons: kSecondaryButton);
      await tester.pumpAndSettle();

      await tester.tap(find.text('Edit'));
      await tester.pumpAndSettle();

      expect(editedApp, testApp);
    });

    testWidgets('should call onRename when Rename is selected', (tester) async {
      AppShortcut? renamedApp;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppCard(
              app: testApp,
              onTap: () {},
              onEdit: (app) {},
              onRename: (app) {
                renamedApp = app;
              },
            ),
          ),
        ),
      );

      // Right click and select Rename
      await tester.tap(find.byType(AppCard), buttons: kSecondaryButton);
      await tester.pumpAndSettle();

      await tester.tap(find.text('Rename'));
      await tester.pumpAndSettle();

      expect(renamedApp, testApp);
    });

    testWidgets('should have icons in menu items', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppCard(
              app: testApp,
              onTap: () {},
              onEdit: (app) {},
              onRename: (app) {},
            ),
          ),
        ),
      );

      // Right click
      await tester.tap(find.byType(AppCard), buttons: kSecondaryButton);
      await tester.pumpAndSettle();

      // Icons should be present
      expect(find.byIcon(Icons.open_in_new), findsOneWidget);
      expect(find.byIcon(Icons.edit), findsOneWidget);
      expect(find.byIcon(Icons.drive_file_rename_outline), findsOneWidget);
    });
  });
}

