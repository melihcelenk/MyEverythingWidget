import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/app_picker_dialog.dart';

void main() {
  group('AppPickerDialog Browse Feature Tests', () {
    testWidgets('should have Browse button for target field', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (context) => const AppPickerDialog(),
                    );
                  },
                  child: const Text('Open'),
                );
              },
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Should have a Browse button
      expect(find.widgetWithIcon(IconButton, Icons.folder_open), findsOneWidget);
    });

    testWidgets('Browse button should be next to URL/Path field', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (context) => const AppPickerDialog(),
                    );
                  },
                  child: const Text('Open'),
                );
              },
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Browse button should exist
      final browseButton = find.widgetWithIcon(IconButton, Icons.folder_open);
      expect(browseButton, findsOneWidget);
    });

    testWidgets('should have tooltip on Browse button', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (context) => const AppPickerDialog(),
                    );
                  },
                  child: const Text('Open'),
                );
              },
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Find browse button
      final browseButton = find.widgetWithIcon(IconButton, Icons.folder_open);
      expect(browseButton, findsOneWidget);

      // Hover to show tooltip
      await tester.longPress(browseButton);
      await tester.pumpAndSettle();

      // Tooltip should appear
      expect(find.text('Browse'), findsOneWidget);
    });
  });
}

