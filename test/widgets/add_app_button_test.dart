import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/add_app_button.dart';

void main() {
  group('AddAppButton Widget - Floating FAB Style', () {
    testWidgets('should render circular floating button with + icon', (tester) async {
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

    testWidgets('should be circular with fixed size', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AddAppButton(
              onTap: () {},
            ),
          ),
        ),
      );

      final container = tester.widget<Container>(
        find.descendant(
          of: find.byType(AddAppButton),
          matching: find.byType(Container),
        ),
      );
      
      expect(container.constraints?.minWidth, 56);
      expect(container.constraints?.minHeight, 56);
    });

    testWidgets('should have circular shape', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AddAppButton(
              onTap: () {},
            ),
          ),
        ),
      );

      final decoration = tester.widget<Container>(
        find.descendant(
          of: find.byType(AddAppButton),
          matching: find.byType(Container),
        ),
      ).decoration as BoxDecoration?;

      expect(decoration?.shape, BoxShape.circle);
    });

    testWidgets('should have elevation/shadow effect', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AddAppButton(
              onTap: () {},
            ),
          ),
        ),
      );

      // Should have Material widget for elevation
      expect(find.descendant(
        of: find.byType(AddAppButton),
        matching: find.byType(Material),
      ), findsOneWidget);
    });
  });
}

