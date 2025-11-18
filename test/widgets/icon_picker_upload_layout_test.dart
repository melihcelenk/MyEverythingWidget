import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/icon_picker_dialog.dart';

void main() {
  group('Icon Picker Upload Layout Tests', () {
    testWidgets('Upload area should fit in dialog without scrolling',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: IconPickerDialog(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Switch to Upload tab
      await tester.tap(find.text('Upload'));
      await tester.pumpAndSettle();

      // Find the upload container
      final uploadContainer = find.byType(Container).evaluate().firstWhere(
            (element) {
              final widget = element.widget as Container;
              return widget.decoration is BoxDecoration &&
                  (widget.decoration as BoxDecoration).border != null;
            },
          );

      // Get container bounds
      final containerBox = tester.getRect(find.byWidget(uploadContainer.widget));

      // Find all text widgets in upload area
      final customIconText = find.text('Upload Custom Icon');
      final dragDropText = find.text('Drag & drop an image or click to browse');
      final chooseFileButton = find.text('Choose File');

      // All elements should exist
      expect(customIconText, findsOneWidget);
      expect(dragDropText, findsOneWidget);
      expect(chooseFileButton, findsOneWidget);

      // Get text positions
      final customIconBox = tester.getRect(customIconText);
      final dragDropBox = tester.getRect(dragDropText);
      final buttonBox = tester.getRect(chooseFileButton);

      // All text should be inside container bounds
      expect(
        containerBox.contains(customIconBox.topLeft) &&
            containerBox.contains(customIconBox.bottomRight),
        true,
        reason:
            'Custom Icon text should be fully inside container. Container: $containerBox, Text: $customIconBox',
      );

      expect(
        containerBox.contains(dragDropBox.topLeft) &&
            containerBox.contains(dragDropBox.bottomRight),
        true,
        reason:
            'Drag & drop text should be fully inside container. Container: $containerBox, Text: $dragDropBox',
      );

      expect(
        containerBox.contains(buttonBox.topLeft) &&
            containerBox.contains(buttonBox.bottomRight),
        true,
        reason:
            'Button should be fully inside container. Container: $containerBox, Button: $buttonBox',
      );
    });

    testWidgets('Upload area should not require scrolling',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: IconPickerDialog(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Switch to Upload tab
      await tester.tap(find.text('Upload'));
      await tester.pumpAndSettle();

      // Upload tab should not have scrollable content
      final scrollables = find.descendant(
        of: find.byType(TabBarView),
        matching: find.byType(Scrollable),
      );

      // Should find GridView in emoji/icons tabs but upload should be simple
      expect(
        scrollables.evaluate().length,
        lessThanOrEqualTo(2),
        reason: 'Upload tab should not need scrolling',
      );
    });

    testWidgets('Choose File button should be horizontally centered',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: IconPickerDialog(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Switch to Upload tab
      await tester.tap(find.text('Upload'));
      await tester.pumpAndSettle();

      // Find button and container (wrapped in Center widget)
      final buttonFinder = find.ancestor(
        of: find.text('Choose File'),
        matching: find.byType(Center),
      ).last;
      final buttonBox = tester.getRect(buttonFinder);

      final container = find.byType(Container).evaluate().firstWhere(
            (element) {
              final widget = element.widget as Container;
              return widget.decoration is BoxDecoration &&
                  (widget.decoration as BoxDecoration).border != null;
            },
          );
      final containerBox = tester.getRect(find.byWidget(container.widget));

      // Button should be centered horizontally
      final buttonCenterX = buttonBox.center.dx;
      final containerCenterX = containerBox.center.dx;

      expect(
        (buttonCenterX - containerCenterX).abs(),
        lessThan(5.0),
        reason:
            'Button should be horizontally centered. Button center: $buttonCenterX, Container center: $containerCenterX',
      );
    });

    testWidgets('Icon and text should be vertically stacked properly',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: IconPickerDialog(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Switch to Upload tab
      await tester.tap(find.text('Upload'));
      await tester.pumpAndSettle();

      // Find elements
      final cloudIcon = find.byIcon(Icons.cloud_upload);
      final customIconText = find.text('Upload Custom Icon');
      final dragDropText = find.text('Drag & drop an image or click to browse');
      final button = find.text('Choose File');

      // Get Y positions
      final iconY = tester.getBottomLeft(cloudIcon).dy;
      final titleY = tester.getTopLeft(customIconText).dy;
      final descY = tester.getTopLeft(dragDropText).dy;
      final buttonY = tester.getTopLeft(button).dy;

      // Verify vertical order: icon -> title -> description -> button
      expect(
        iconY < titleY,
        true,
        reason: 'Icon should be above title. Icon bottom: $iconY, Title top: $titleY',
      );

      expect(
        titleY < descY,
        true,
        reason: 'Title should be above description. Title top: $titleY, Desc top: $descY',
      );

      expect(
        descY < buttonY,
        true,
        reason:
            'Description should be above button. Desc top: $descY, Button top: $buttonY',
      );
    });

    testWidgets('Upload container should have visible border',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.light(),
          home: const Scaffold(
            body: IconPickerDialog(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Switch to Upload tab
      await tester.tap(find.text('Upload'));
      await tester.pumpAndSettle();

      // Find container with border
      final container = find.byType(Container).evaluate().firstWhere(
            (element) {
              final widget = element.widget as Container;
              return widget.decoration is BoxDecoration &&
                  (widget.decoration as BoxDecoration).border != null;
            },
          );

      final widget = container.widget as Container;
      final decoration = widget.decoration as BoxDecoration;

      expect(
        decoration.border,
        isNotNull,
        reason: 'Container should have a border',
      );

      expect(
        decoration.borderRadius,
        isNotNull,
        reason: 'Container should have rounded corners',
      );
    });
  });
}
