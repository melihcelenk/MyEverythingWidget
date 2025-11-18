import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/icon_picker_dialog.dart';

void main() {
  group('IconPickerDialog Overlap Tests', () {
    testWidgets('emoji grid items should not overlap', (tester) async {
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

      // Open dialog
      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Find all emoji grid items (InkWell containers)
      final gridItems = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byType(InkWell),
      );

      final itemCount = tester.widgetList(gridItems).length;
      expect(itemCount, greaterThan(0), reason: 'Should have emoji items');

      // Check first 20 items for overlaps (testing all pairs would be O(n²))
      final testCount = itemCount < 20 ? itemCount : 20;

      for (int i = 0; i < testCount; i++) {
        for (int j = i + 1; j < testCount; j++) {
          final rect1 = tester.getRect(gridItems.at(i));
          final rect2 = tester.getRect(gridItems.at(j));

          expect(
            rect1.overlaps(rect2),
            false,
            reason: 'Emoji item $i (${rect1.toString()}) '
                'should not overlap with item $j (${rect2.toString()})',
          );
        }
      }
    });

    testWidgets('icon grid items should not overlap', (tester) async {
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

      // Open dialog
      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Switch to Icons tab
      await tester.tap(find.text('Icons'));
      await tester.pumpAndSettle();

      // Find all icon grid items
      final gridItems = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byType(InkWell),
      );

      final itemCount = tester.widgetList(gridItems).length;
      expect(itemCount, greaterThan(0), reason: 'Should have icon items');

      // Check first 20 items for overlaps
      final testCount = itemCount < 20 ? itemCount : 20;

      for (int i = 0; i < testCount; i++) {
        for (int j = i + 1; j < testCount; j++) {
          final rect1 = tester.getRect(gridItems.at(i));
          final rect2 = tester.getRect(gridItems.at(j));

          expect(
            rect1.overlaps(rect2),
            false,
            reason: 'Icon item $i (${rect1.toString()}) '
                'should not overlap with item $j (${rect2.toString()})',
          );
        }
      }
    });

    testWidgets('emoji grid should have adequate spacing between items', (tester) async {
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

      // Find first two items in same row
      final gridItems = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byType(InkWell),
      );

      expect(gridItems, findsWidgets);

      final rect1 = tester.getRect(gridItems.at(0));
      final rect2 = tester.getRect(gridItems.at(1));

      // Calculate horizontal spacing
      final spacing = rect2.left - rect1.right;

      // Verify spacing is at least 12px (our configured crossAxisSpacing)
      expect(
        spacing,
        greaterThanOrEqualTo(12.0),
        reason: 'Horizontal spacing should be at least 12px, got $spacing',
      );
    });

    testWidgets('icon grid should have adequate spacing between items', (tester) async {
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

      // Find first two items
      final gridItems = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byType(InkWell),
      );

      expect(gridItems, findsWidgets);

      final rect1 = tester.getRect(gridItems.at(0));
      final rect2 = tester.getRect(gridItems.at(1));

      // Calculate horizontal spacing
      final spacing = rect2.left - rect1.right;

      // Verify spacing is at least 12px
      expect(
        spacing,
        greaterThanOrEqualTo(12.0),
        reason: 'Horizontal spacing should be at least 12px, got $spacing',
      );
    });
  });
}
