import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/app_picker_dialog.dart';

void main() {
  group('AppPickerDialog Overflow Tests', () {
    testWidgets('should not have overflow in dialog content', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => const AppPickerDialog(),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Check for overflow errors
      expect(tester.takeException(), isNull);
    });

    testWidgets('should properly layout all form fields without overflow', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => const AppPickerDialog(),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Verify all fields are visible and properly laid out
      expect(find.text('Icon'), findsOneWidget);
      expect(find.text('App Name'), findsOneWidget);
      expect(find.text('URL or Path'), findsOneWidget);
      expect(find.text('Category'), findsOneWidget);
      expect(find.text('Add'), findsOneWidget);
      expect(find.text('Cancel'), findsOneWidget);
    });

    testWidgets('should handle long content without overflow', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => const AppPickerDialog(),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Enter long text in name field
      await tester.enterText(
        find.widgetWithText(TextFormField, 'App Name'),
        'Very Long Application Name That Might Cause Overflow',
      );
      await tester.pumpAndSettle();

      // Check for overflow errors
      expect(tester.takeException(), isNull);
    });
  });
}

