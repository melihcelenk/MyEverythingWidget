import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/models/app_shortcut.dart';
import 'package:my_everything_widget/widgets/app_card.dart';

void main() {
  group('AppCard Tooltip Tests', () {
    testWidgets('Tooltip should show full app name on hover',
        (WidgetTester tester) async {
      final app = AppShortcut(
        id: '1',
        name: 'Stack Overflow Community Platform',
        iconPath: '',
        target: '',
        category: 'Dev',
        type: LaunchType.url,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 120, // Narrow to force truncation
              height: 120,
              child: AppCard(app: app, onTap: () {}),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Find the tooltip widget
      final tooltipFinder = find.byType(Tooltip);
      expect(tooltipFinder, findsOneWidget,
          reason: 'Should find one Tooltip widget');

      // Verify tooltip message is the full app name
      final tooltip = tester.widget<Tooltip>(tooltipFinder);
      expect(
        tooltip.message,
        app.name,
        reason: 'Tooltip message should be the full app name',
      );

      // Trigger tooltip by long press (hover simulation)
      await tester.longPress(tooltipFinder);
      await tester.pumpAndSettle();

      // Find the tooltip overlay text
      expect(
        find.text(app.name),
        findsWidgets,
        reason:
            'After triggering tooltip, full app name should be visible in overlay',
      );
    });

    testWidgets('Tooltip should have 500ms wait duration',
        (WidgetTester tester) async {
      final app = AppShortcut(
        id: '1',
        name: 'Very Long Application Name That Needs Tooltip',
        iconPath: '',
        target: '',
        category: 'Dev',
        type: LaunchType.exe,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppCard(app: app, onTap: () {}),
          ),
        ),
      );

      await tester.pumpAndSettle();

      final tooltip = tester.widget<Tooltip>(find.byType(Tooltip));
      expect(
        tooltip.waitDuration,
        const Duration(milliseconds: 500),
        reason:
            'Tooltip should wait 500ms before showing (like Windows behavior)',
      );
    });

    testWidgets('Only truncated cards should have tooltips',
        (WidgetTester tester) async {
      final apps = [
        AppShortcut(
          id: '1',
          name: 'First App With Very Long Name That Truncates',
          iconPath: '',
          target: '',
          category: 'Dev',
          type: LaunchType.exe,
        ),
        AppShortcut(
          id: '2',
          name: 'Second App With Even Longer Name That Definitely Wraps Multiple Times',
          iconPath: '',
          target: '',
          category: 'Dev',
          type: LaunchType.url,
        ),
        AppShortcut(
          id: '3',
          name: 'Git', // Short - no tooltip
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
              width: 300,
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

      // Find all tooltips (should be 2, not 3)
      final tooltips = tester.widgetList<Tooltip>(find.byType(Tooltip)).toList();
      expect(
        tooltips.length,
        2,
        reason: 'Should find 2 tooltips (only for truncated text, not for "Git")',
      );

      // Verify tooltips are for the long names
      expect(
        tooltips[0].message,
        apps[0].name,
        reason: 'First tooltip should be for first long app name',
      );
      expect(
        tooltips[1].message,
        apps[1].name,
        reason: 'Second tooltip should be for second long app name',
      );
    });

    testWidgets('Short names should NOT have tooltip',
        (WidgetTester tester) async {
      final app = AppShortcut(
        id: '1',
        name: 'Git', // Short name, no truncation needed
        iconPath: '',
        target: '',
        category: 'Dev',
        type: LaunchType.exe,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 120,
              height: 120,
              child: AppCard(app: app, onTap: () {}),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Short names that don't truncate should NOT have tooltip
      expect(
        find.byType(Tooltip),
        findsNothing,
        reason:
            'Short names that fit in 2 lines should not have tooltip to avoid clutter',
      );
    });

    testWidgets('Tooltip should only appear on truncated text',
        (WidgetTester tester) async {
      final shortApp = AppShortcut(
        id: '1',
        name: 'VSC', // Very short
        iconPath: '',
        target: '',
        category: 'Dev',
        type: LaunchType.exe,
      );

      final longApp = AppShortcut(
        id: '2',
        name: 'Very Long Application Name That Will Truncate',
        iconPath: '',
        target: '',
        category: 'Dev',
        type: LaunchType.url,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 200,
              child: Row(
                children: [
                  SizedBox(
                    width: 90,
                    height: 100,
                    child: AppCard(app: shortApp, onTap: () {}),
                  ),
                  SizedBox(
                    width: 90,
                    height: 100,
                    child: AppCard(app: longApp, onTap: () {}),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Should find exactly 1 tooltip (only for the long name)
      final tooltips = tester.widgetList<Tooltip>(find.byType(Tooltip));
      expect(
        tooltips.length,
        1,
        reason: 'Only the truncated text should have tooltip',
      );

      // Verify it's the long app's tooltip
      final tooltip = tooltips.first;
      expect(
        tooltip.message,
        longApp.name,
        reason: 'Tooltip should be for the long app name',
      );
    });
  });
}
