import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/icon_picker_dialog.dart';

void main() {
  testWidgets('Take screenshot of emoji grid', (tester) async {
    // Set larger test size
    tester.view.physicalSize = const Size(800, 1200);
    tester.view.devicePixelRatio = 1.0;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Builder(
            builder: (context) => Center(
              child: ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => const IconPickerDialog(),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      ),
    );

    // Open dialog
    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    print('Taking screenshot...');

    // Find the dialog
    final dialogFinder = find.byType(Dialog);
    expect(dialogFinder, findsOneWidget);

    // Take screenshot
    await expectLater(
      dialogFinder,
      matchesGoldenFile('test_emoji_screenshot.png'),
    );

    print('Screenshot saved to: test/widgets/goldens/test_emoji_screenshot.png');
  });
}
