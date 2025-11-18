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

    testWidgets('icons should not overflow their containers', (tester) async {
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

      // Find icon containers (they have padding and decoration)
      final iconContainers = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byWidgetPredicate(
          (widget) => widget is Container &&
              widget.decoration is BoxDecoration &&
              widget.padding != null,
        ),
      );

      // Find icons
      final icons = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byType(Icon),
      );

      expect(iconContainers, findsWidgets);
      expect(icons, findsWidgets);

      // Test first 5 items to ensure icons fit within their containers with proper padding
      final testCount = 5;
      for (int i = 0; i < testCount; i++) {
        final containerRect = tester.getRect(iconContainers.at(i));
        final iconRect = tester.getRect(icons.at(i));

        // Calculate padding
        final paddingLeft = iconRect.left - containerRect.left;
        final paddingRight = containerRect.right - iconRect.right;
        final paddingTop = iconRect.top - containerRect.top;
        final paddingBottom = containerRect.bottom - iconRect.bottom;

        // Icons should have at least 8px padding (our configured padding)
        const minPadding = 8.0;

        expect(
          paddingLeft >= minPadding - 1, // 1px tolerance
          true,
          reason: 'Icon $i needs ~${minPadding}px left padding, got ${paddingLeft.toStringAsFixed(1)}px\n'
              'Container: $containerRect\n'
              'Icon: $iconRect',
        );

        expect(
          paddingRight >= minPadding - 1,
          true,
          reason: 'Icon $i needs ~${minPadding}px right padding, got ${paddingRight.toStringAsFixed(1)}px\n'
              'Container: $containerRect\n'
              'Icon: $iconRect',
        );

        expect(
          paddingTop >= minPadding - 1,
          true,
          reason: 'Icon $i needs ~${minPadding}px top padding, got ${paddingTop.toStringAsFixed(1)}px\n'
              'Container: $containerRect\n'
              'Icon: $iconRect',
        );

        expect(
          paddingBottom >= minPadding - 1,
          true,
          reason: 'Icon $i needs ~${minPadding}px bottom padding, got ${paddingBottom.toStringAsFixed(1)}px\n'
              'Container: $containerRect\n'
              'Icon: $iconRect',
        );
      }
    });

    testWidgets('emojis should not overflow their containers', (tester) async {
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

      // Find emoji containers (they have padding and decoration)
      final emojiContainers = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byWidgetPredicate(
          (widget) => widget is Container &&
              widget.decoration is BoxDecoration &&
              widget.padding != null,
        ),
      );

      // Find emoji texts
      final emojiTexts = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byType(Text),
      );

      expect(emojiContainers, findsWidgets);
      expect(emojiTexts, findsWidgets);

      // Test first 5 items
      final testCount = 5;
      for (int i = 0; i < testCount; i++) {
        final containerRect = tester.getRect(emojiContainers.at(i));
        final emojiRect = tester.getRect(emojiTexts.at(i));

        // Calculate padding
        final paddingLeft = emojiRect.left - containerRect.left;
        final paddingRight = containerRect.right - emojiRect.right;
        final paddingTop = emojiRect.top - containerRect.top;
        final paddingBottom = containerRect.bottom - emojiRect.bottom;

        // Emojis should have at least 8px padding (our configured padding)
        const minPadding = 8.0;

        expect(
          paddingLeft >= minPadding - 1, // 1px tolerance
          true,
          reason: 'Emoji $i needs ~${minPadding}px left padding, got ${paddingLeft.toStringAsFixed(1)}px\n'
              'Container: $containerRect\n'
              'Emoji: $emojiRect',
        );

        expect(
          paddingRight >= minPadding - 1,
          true,
          reason: 'Emoji $i needs ~${minPadding}px right padding, got ${paddingRight.toStringAsFixed(1)}px\n'
              'Container: $containerRect\n'
              'Emoji: $emojiRect',
        );

        expect(
          paddingTop >= minPadding - 1,
          true,
          reason: 'Emoji $i needs ~${minPadding}px top padding, got ${paddingTop.toStringAsFixed(1)}px\n'
              'Container: $containerRect\n'
              'Emoji: $emojiRect',
        );

        expect(
          paddingBottom >= minPadding - 1,
          true,
          reason: 'Emoji $i needs ~${minPadding}px bottom padding, got ${paddingBottom.toStringAsFixed(1)}px\n'
              'Container: $containerRect\n'
              'Emoji: $emojiRect',
        );
      }
    });
  });
}
