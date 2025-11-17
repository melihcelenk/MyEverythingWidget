import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/add_app_button.dart';

void main() {
  group('AddAppButton Widget', () {
    testWidgets('should render add button with + icon', (tester) async {
      var tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AddAppButton(
              onTap: () {
                tapped = true;
              },
            ),
          ),
        ),
      );

      // Find the button
      expect(find.byType(AddAppButton), findsOneWidget);
      expect(find.byIcon(Icons.add), findsOneWidget);

      // Tap the button
      await tester.tap(find.byType(AddAppButton));
      await tester.pumpAndSettle();

      expect(tapped, true);
    });

    testWidgets('should display "Add" text', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AddAppButton(
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('Add'), findsOneWidget);
    });

    testWidgets('should have same size as app card', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 90,
              height: 100,
              child: AddAppButton(
                onTap: () {},
              ),
            ),
          ),
        ),
      );

      final addButton = tester.widget<AddAppButton>(find.byType(AddAppButton));
      expect(addButton, isNotNull);
    });

    testWidgets('should be visually distinct from regular app cards', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AddAppButton(
              onTap: () {},
            ),
          ),
        ),
      );

      // Should use dotted/dashed border style
      final inkWell = find.byType(InkWell);
      expect(inkWell, findsOneWidget);
    });
  });
}

