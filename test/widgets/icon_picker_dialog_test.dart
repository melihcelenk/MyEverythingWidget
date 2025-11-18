import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/icon_picker_dialog.dart';

void main() {
  group('IconPickerDialog', () {
    testWidgets('should display dialog with title and tabs', (tester) async {
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

      expect(find.text('Select Icon'), findsOneWidget);
      expect(find.text('Emoji'), findsOneWidget);
      expect(find.text('Icons'), findsOneWidget);
      expect(find.text('Upload'), findsOneWidget);
    });

    testWidgets('should display search bar', (tester) async {
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

      expect(find.byType(TextField), findsOneWidget);
      expect(find.byIcon(Icons.search), findsOneWidget);
    });

    testWidgets('should display emoji grid', (tester) async {
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

      // Wait for TabBarView to fully render
      await tester.pump(const Duration(milliseconds: 100));
      await tester.pumpAndSettle();

      // Verify GridView exists (we're using GridView with shrinkWrap now)
      expect(find.byType(GridView), findsWidgets);

      // Emoji tab should be selected by default
      // Check if emoji text widgets are actually rendered and visible
      final emojiTexts = find.byWidgetPredicate(
        (widget) => widget is Text && 
            widget.data != null && 
            widget.data!.length <= 2 &&
            widget.data!.runes.length > 0,
      );
      
      // Verify at least some emojis are rendered
      expect(emojiTexts, findsWidgets);
      
      // Verify specific emoji is present
      final firstEmoji = find.text('📱', findRichText: true);
      expect(firstEmoji, findsWidgets);
    });

    testWidgets('should display icon grid in Icons tab', (tester) async {
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

      // Should display material icons
      expect(find.byIcon(Icons.apps), findsWidgets);
    });

    testWidgets('should display upload view in Upload tab', (tester) async {
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

      expect(find.text('Upload Custom Icon'), findsOneWidget);
      expect(find.text('Choose File'), findsOneWidget);
      expect(find.byIcon(Icons.cloud_upload), findsOneWidget);
    });

    testWidgets('should return result when emoji selected', (tester) async {
      IconPickerResult? result;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () async {
                  result = await showDialog<IconPickerResult>(
                    context: context,
                    builder: (context) => const IconPickerDialog(),
                  );
                },
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Open'));
      await tester.pumpAndSettle();

      // Tap on first emoji
      await tester.tap(find.text('📱', findRichText: true).first);
      await tester.pumpAndSettle();

      expect(result, isNotNull);
      expect(result!.type, IconType.emoji);
      expect(result!.value, '📱');
    });

    testWidgets('should close dialog when close button clicked', (tester) async {
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

      await tester.tap(find.byIcon(Icons.close));
      await tester.pumpAndSettle();

      expect(find.text('Select Icon'), findsNothing);
    });
  });
}

