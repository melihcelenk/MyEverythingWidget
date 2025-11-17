import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/icon_picker_dialog.dart';

void main() {
  group('IconPickerDialog Overflow Tests', () {
    testWidgets('should not have overflow in Emoji tab', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => const IconPickerDialog(),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Check for overflow errors in Emoji tab
      expect(tester.takeException(), isNull);
    });

    testWidgets('should not have overflow in Icons tab', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => const IconPickerDialog(),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Switch to Icons tab
      await tester.tap(find.text('Icons'));
      await tester.pumpAndSettle();

      // Check for overflow errors
      expect(tester.takeException(), isNull);
    });

    testWidgets('should not have overflow in Upload tab', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => const IconPickerDialog(),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Switch to Upload tab
      await tester.tap(find.text('Upload'));
      await tester.pumpAndSettle();

      // Check for overflow errors
      expect(tester.takeException(), isNull);
    });

    testWidgets('should properly layout all components', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => const IconPickerDialog(),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Verify all components are visible
      expect(find.text('Select Icon'), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget); // Search bar
      expect(find.byType(TabBar), findsOneWidget);
      expect(find.byIcon(Icons.close), findsOneWidget);
    });
  });
}

