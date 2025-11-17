import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/models/app_shortcut.dart';
import 'package:my_everything_widget/widgets/app_card.dart';

void main() {
  group('AppCard Visual Alignment Tests', () {
    testWidgets(
        'Card content (icons) should align at top regardless of text length',
        (WidgetTester tester) async {
      // Create apps with different name lengths to test alignment
      final shortNameApp = AppShortcut(
        id: '1',
        name: 'Git', // Short, single line
        iconPath: '',
        target: '',
        category: 'Dev',
        type: LaunchType.exe,
      );

      final longNameApp = AppShortcut(
        id: '2',
        name: 'Stack Overflow', // Long, wraps to 2 lines
        iconPath: '',
        target: '',
        category: 'Dev',
        type: LaunchType.url,
      );

      final mediumNameApp = AppShortcut(
        id: '3',
        name: 'VS Code', // Medium length
        iconPath: '',
        target: '',
        category: 'Dev',
        type: LaunchType.exe,
      );

      // Build a grid with all cards in one row
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: GridView.count(
                crossAxisCount: 3,
                childAspectRatio: 1.0,
                children: [
                  AppCard(app: shortNameApp, onTap: () {}),
                  AppCard(app: longNameApp, onTap: () {}),
                  AppCard(app: mediumNameApp, onTap: () {}),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Find all icons - these should be at the same Y position
      final icons = tester.widgetList<Icon>(find.byType(Icon)).toList();
      expect(icons.length, 3, reason: 'Should find 3 icons');

      // Get icon Y positions (distance from top of screen)
      final icon1Y = tester.getTopLeft(find.byWidget(icons[0])).dy;
      final icon2Y = tester.getTopLeft(find.byWidget(icons[1])).dy;
      final icon3Y = tester.getTopLeft(find.byWidget(icons[2])).dy;

      // All icons MUST be at same vertical position
      expect(
        (icon1Y - icon2Y).abs(),
        lessThan(2.0),
        reason:
            'Icon in card 1 (short name "$shortNameApp.name") and card 2 (long name "${longNameApp.name}") '
            'must be at the same Y position. Icon1 Y=$icon1Y, Icon2 Y=$icon2Y. '
            'Difference: ${(icon1Y - icon2Y).abs()}px. '
            'If icons are not aligned, the card content is not top-aligned.',
      );

      expect(
        (icon2Y - icon3Y).abs(),
        lessThan(2.0),
        reason:
            'Icon in card 2 (long name "${longNameApp.name}") and card 3 (medium name "${mediumNameApp.name}") '
            'must be at the same Y position. Icon2 Y=$icon2Y, Icon3 Y=$icon3Y. '
            'Difference: ${(icon2Y - icon3Y).abs()}px. '
            'If icons are not aligned, the card content is not top-aligned.',
      );

      expect(
        (icon1Y - icon3Y).abs(),
        lessThan(2.0),
        reason:
            'Icon in card 1 (short name "${shortNameApp.name}") and card 3 (medium name "${mediumNameApp.name}") '
            'must be at the same Y position. Icon1 Y=$icon1Y, Icon3 Y=$icon3Y. '
            'Difference: ${(icon1Y - icon3Y).abs()}px. '
            'If icons are not aligned, the card content is not top-aligned.',
      );
    });

    testWidgets('Multi-row grid icons should be aligned within each row',
        (WidgetTester tester) async {
      // Create 6 apps with varying name lengths
      final apps = [
        AppShortcut(
          id: '1',
          name: 'Git', // Row 1: Very short
          iconPath: '',
          target: '',
          category: 'Dev',
          type: LaunchType.exe,
        ),
        AppShortcut(
          id: '2',
          name: 'Stack Overflow Community', // Row 1: Long, wraps to 2 lines
          iconPath: '',
          target: '',
          category: 'Dev',
          type: LaunchType.url,
        ),
        AppShortcut(
          id: '3',
          name: 'VS Code', // Row 1: Medium
          iconPath: '',
          target: '',
          category: 'Dev',
          type: LaunchType.exe,
        ),
        AppShortcut(
          id: '4',
          name: 'npm', // Row 2: Very short
          iconPath: '',
          target: '',
          category: 'Dev',
          type: LaunchType.exe,
        ),
        AppShortcut(
          id: '5',
          name: 'Docker Desktop Application', // Row 2: Long
          iconPath: '',
          target: '',
          category: 'Dev',
          type: LaunchType.exe,
        ),
        AppShortcut(
          id: '6',
          name: 'GitHub', // Row 2: Short
          iconPath: '',
          target: '',
          category: 'Dev',
          type: LaunchType.exe,
        ),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: GridView.count(
                crossAxisCount: 3,
                childAspectRatio: 1.0,
                children:
                    apps.map((app) => AppCard(app: app, onTap: () {})).toList(),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Find all icons
      final icons = tester.widgetList<Icon>(find.byType(Icon)).toList();
      expect(icons.length, 6, reason: 'Should find 6 icons (one per card)');

      // Get Y positions of icons in first row (indices 0, 1, 2)
      final row1Icon1Y = tester.getTopLeft(find.byWidget(icons[0])).dy;
      final row1Icon2Y = tester.getTopLeft(find.byWidget(icons[1])).dy;
      final row1Icon3Y = tester.getTopLeft(find.byWidget(icons[2])).dy;

      // First row: all icons must be at same Y position
      expect(
        (row1Icon1Y - row1Icon2Y).abs(),
        lessThan(2.0),
        reason:
            'Row 1: Icons 1 and 2 must be at same Y position. '
            'Icon1 Y=$row1Icon1Y, Icon2 Y=$row1Icon2Y. '
            'App names: "${apps[0].name}" vs "${apps[1].name}"',
      );

      expect(
        (row1Icon2Y - row1Icon3Y).abs(),
        lessThan(2.0),
        reason:
            'Row 1: Icons 2 and 3 must be at same Y position. '
            'Icon2 Y=$row1Icon2Y, Icon3 Y=$row1Icon3Y. '
            'App names: "${apps[1].name}" vs "${apps[2].name}"',
      );

      // Get Y positions of icons in second row (indices 3, 4, 5)
      final row2Icon1Y = tester.getTopLeft(find.byWidget(icons[3])).dy;
      final row2Icon2Y = tester.getTopLeft(find.byWidget(icons[4])).dy;
      final row2Icon3Y = tester.getTopLeft(find.byWidget(icons[5])).dy;

      // Second row: all icons must be at same Y position
      expect(
        (row2Icon1Y - row2Icon2Y).abs(),
        lessThan(2.0),
        reason:
            'Row 2: Icons 1 and 2 must be at same Y position. '
            'Icon1 Y=$row2Icon1Y, Icon2 Y=$row2Icon2Y. '
            'App names: "${apps[3].name}" vs "${apps[4].name}"',
      );

      expect(
        (row2Icon2Y - row2Icon3Y).abs(),
        lessThan(2.0),
        reason:
            'Row 2: Icons 2 and 3 must be at same Y position. '
            'Icon2 Y=$row2Icon2Y, Icon3 Y=$row2Icon3Y. '
            'App names: "${apps[4].name}" vs "${apps[5].name}"',
      );
    });
  });
}
