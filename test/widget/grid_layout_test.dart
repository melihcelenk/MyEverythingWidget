import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/models/app_shortcut.dart';
import 'package:my_everything_widget/widgets/app_card.dart';

/// Tests for grid layout behavior
/// Ensures cards maintain fixed size regardless of window width
void main() {
  group('Grid Layout Tests', () {
    testWidgets('AppCard maintains fixed size with short name', (tester) async {
      const app = AppShortcut(
        id: '1',
        name: 'GitHub',
        iconPath: '',
        target: 'https://github.com',
        category: 'Dev',
        type: LaunchType.url,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 90,
              height: 100,
              child: AppCard(
                app: app,
                onTap: () {},
              ),
            ),
          ),
        ),
      );

      // Verify card renders without overflow
      expect(find.text('GitHub'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('AppCard handles long two-word name without overflow', (tester) async {
      const app = AppShortcut(
        id: '1',
        name: 'Stack Overflow',
        iconPath: '',
        target: 'https://stackoverflow.com',
        category: 'Dev',
        type: LaunchType.url,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 90,
              height: 100,
              child: AppCard(
                app: app,
                onTap: () {},
              ),
            ),
          ),
        ),
      );

      // Verify both words are visible
      final textFinder = find.text('Stack Overflow');
      expect(textFinder, findsOneWidget);

      // Verify no overflow errors
      expect(tester.takeException(), isNull);

      // Verify text widget is within bounds
      final textWidget = tester.widget<Text>(textFinder);
      expect(textWidget.maxLines, 2);
      expect(textWidget.overflow, TextOverflow.ellipsis);
    });

    testWidgets('Grid maintains fixed spacing when window width changes', (tester) async {
      const apps = [
        AppShortcut(id: '1', name: 'App1', iconPath: '', target: '', category: 'Dev', type: LaunchType.url),
        AppShortcut(id: '2', name: 'App2', iconPath: '', target: '', category: 'Dev', type: LaunchType.url),
        AppShortcut(id: '3', name: 'App3', iconPath: '', target: '', category: 'Dev', type: LaunchType.url),
      ];

      const cellWidth = 90.0;
      const cellHeight = 100.0;
      const spacing = 4.0;

      Widget buildGrid(double containerWidth) {
        return MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: containerWidth,
              child: SingleChildScrollView(
                child: Wrap(
                  spacing: spacing,
                  runSpacing: spacing,
                  children: apps.map((app) {
                    return SizedBox(
                      width: cellWidth,
                      height: cellHeight,
                      child: AppCard(app: app, onTap: () {}),
                    );
                  }).toList(),
                ),
              ),
            ),
          ),
        );
      }

      // Test with 320px width (3 columns fit)
      await tester.pumpWidget(buildGrid(320));
      await tester.pumpAndSettle();

      var cards = find.byType(AppCard);
      expect(cards, findsNWidgets(3));

      // Verify first card is at expected position (0, 0)
      final firstCardPos320 = tester.getTopLeft(cards.at(0));
      expect(firstCardPos320.dx, 0);
      expect(firstCardPos320.dy, 0);

      // Test with 400px width (4 columns could fit)
      await tester.pumpWidget(buildGrid(400));
      await tester.pumpAndSettle();

      cards = find.byType(AppCard);
      expect(cards, findsNWidgets(3));

      // Verify first card position hasn't changed (still at 0, 0)
      final firstCardPos400 = tester.getTopLeft(cards.at(0));
      expect(firstCardPos400.dx, 0);
      expect(firstCardPos400.dy, 0);

      // Verify cards maintain fixed size
      final firstCardSize = tester.getSize(cards.at(0));
      expect(firstCardSize.width, cellWidth);
      expect(firstCardSize.height, cellHeight);

      // Verify second card is at correct horizontal position (90 + 4 = 94)
      final secondCardPos = tester.getTopLeft(cards.at(1));
      expect(secondCardPos.dx, cellWidth + spacing);
      expect(secondCardPos.dy, 0); // Same row
    });

    testWidgets('AppCard text visibility with different names', (tester) async {
      final testCases = [
        ('GitHub', true),
        ('Stack Overflow', true),
        ('VS Code', true),
        ('Docker Hub', true),
        ('Very Long Application Name', false), // Should truncate
      ];

      for (final testCase in testCases) {
        final (name, shouldShowFull) = testCase;

        final app = AppShortcut(
          id: '1',
          name: name,
          iconPath: '',
          target: 'https://test.com',
          category: 'Dev',
          type: LaunchType.url,
        );

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: SizedBox(
                width: 90,
                height: 100,
                child: AppCard(app: app, onTap: () {}),
              ),
            ),
          ),
        );

        // Find the text widget
        final textFinder = find.text(name);
        expect(textFinder, findsOneWidget);

        // Verify no overflow
        expect(tester.takeException(), isNull, reason: 'Overflow with name: $name');
      }
    });
  });
}
