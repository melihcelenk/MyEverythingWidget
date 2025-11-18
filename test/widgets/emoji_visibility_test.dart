import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/icon_picker_dialog.dart';

void main() {
  group('Emoji Visibility Tests', () {
    testWidgets('all emojis should be visible and numbered', (tester) async {
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

      // Verify emoji tab is active
      expect(find.text('Emoji'), findsOneWidget);

      // Find all emoji containers
      final emojiContainers = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byWidgetPredicate(
          (widget) => widget is Container &&
              widget.decoration is BoxDecoration &&
              (widget.decoration as BoxDecoration).border != null,
        ),
      );

      // Find all emoji texts
      final emojiTexts = find.descendant(
        of: find.byType(GridView).first,
        matching: find.byType(Text),
      );

      final containerCount = tester.widgetList(emojiContainers).length;
      final emojiCount = tester.widgetList(emojiTexts).length;

      print('\n=== EMOJI VISIBILITY TEST ===');
      print('Red-bordered containers found: $containerCount');
      print('Emoji text widgets found: $emojiCount');

      // Each emoji should have a container
      expect(containerCount, greaterThan(0), reason: 'Should have emoji containers');
      expect(emojiCount, greaterThan(0), reason: 'Should have emoji texts');

      // List each emoji with its position and size
      print('\n=== INDIVIDUAL EMOJI DETAILS ===');
      for (int i = 0; i < emojiCount && i < 50; i++) {
        final containerRect = tester.getRect(emojiContainers.at(i));
        final emojiRect = tester.getRect(emojiTexts.at(i));
        final emojiWidget = tester.widget<Text>(emojiTexts.at(i));
        final emojiChar = emojiWidget.data ?? '';

        // Check if emoji is visible (has positive size)
        final isVisible = emojiRect.width > 0 && emojiRect.height > 0;

        // Check if emoji is inside container
        final isInsideContainer =
            containerRect.contains(emojiRect.topLeft) &&
            containerRect.contains(emojiRect.bottomRight);

        print('Emoji #${i + 1}: "$emojiChar"');
        print('  Container: ${containerRect.toString()} (${containerRect.width.toStringAsFixed(1)}x${containerRect.height.toStringAsFixed(1)})');
        print('  Emoji:     ${emojiRect.toString()} (${emojiRect.width.toStringAsFixed(1)}x${emojiRect.height.toStringAsFixed(1)})');
        print('  Visible:   $isVisible');
        print('  Inside:    $isInsideContainer');

        // Verify emoji is visible
        expect(isVisible, true, reason: 'Emoji #${i + 1} "$emojiChar" should be visible');

        // Verify emoji is inside its red border
        expect(isInsideContainer, true,
          reason: 'Emoji #${i + 1} "$emojiChar" should be inside red border.\n'
                  'Container: $containerRect\n'
                  'Emoji: $emojiRect');
      }

      // Take screenshot with numbered emojis
      print('\n=== TAKING NUMBERED SCREENSHOT ===');
      await _takeNumberedScreenshot(tester, 'emoji_grid_numbered.png');

      print('\n=== TEST COMPLETE ===');
      print('Screenshot saved to: test/widgets/emoji_grid_numbered.png');
      print('Please check the screenshot to verify all emojis are visible.\n');
    });
  });
}

Future<void> _takeNumberedScreenshot(WidgetTester tester, String filename) async {
  final RenderObject? renderObject = tester.renderObject(find.byType(MaterialApp));
  if (renderObject == null) return;

  final RenderRepaintBoundary boundary = renderObject as RenderRepaintBoundary;
  final ui.Image image = await boundary.toImage(pixelRatio: 1.0);

  // Convert to byte data
  final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
  if (byteData == null) return;

  // Save to file
  final file = File('test/widgets/$filename');
  await file.writeAsBytes(byteData.buffer.asUint8List());

  print('Screenshot saved: ${file.absolute.path}');
}
