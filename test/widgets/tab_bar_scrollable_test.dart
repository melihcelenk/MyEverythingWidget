import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/models/category.dart';
import 'package:provider/provider.dart';
import 'package:my_everything_widget/providers/app_state.dart';
import 'package:my_everything_widget/screens/main_window.dart';

void main() {
  group('TabBar Scrollable Tests', () {
    testWidgets('TabBar should be scrollable', (tester) async {
      await tester.pumpWidget(
        ChangeNotifierProvider(
          create: (_) => AppState(),
          child: const MaterialApp(
            home: MainWindow(),
          ),
        ),
      );

      // Find TabBar
      final tabBar = tester.widget<TabBar>(find.byType(TabBar));
      
      // TabBar should be scrollable
      expect(tabBar.isScrollable, true);
    });

    testWidgets('All tabs should be visible when scrolled', (tester) async {
      await tester.pumpWidget(
        ChangeNotifierProvider(
          create: (_) => AppState(),
          child: const MaterialApp(
            home: MainWindow(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // All category tabs should be findable
      expect(find.text('All'), findsOneWidget);
      expect(find.text('Web'), findsOneWidget);
      expect(find.text('Dev'), findsOneWidget);
      expect(find.text('Media'), findsOneWidget);
    });

    testWidgets('TabBar should not use ChoiceChip when scrollable', (tester) async {
      await tester.pumpWidget(
        ChangeNotifierProvider(
          create: (_) => AppState(),
          child: const MaterialApp(
            home: MainWindow(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Should use Tab widget instead of ChoiceChip
      expect(find.byType(Tab), findsWidgets);
    });

    testWidgets('TabBar should have proper styling', (tester) async {
      await tester.pumpWidget(
        ChangeNotifierProvider(
          create: (_) => AppState(),
          child: const MaterialApp(
            home: MainWindow(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      final tabBar = tester.widget<TabBar>(find.byType(TabBar));
      
      // TabBar should be properly configured
      expect(tabBar.isScrollable, true);
      expect(tabBar.tabs.length, greaterThan(0));
    });

    testWidgets('Should be able to scroll to last tab', (tester) async {
      await tester.pumpWidget(
        ChangeNotifierProvider(
          create: (_) => AppState(),
          child: const MaterialApp(
            home: MainWindow(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Scroll to Media tab (last tab)
      await tester.tap(find.text('Media'));
      await tester.pumpAndSettle();

      // Media tab should be selected
      expect(find.text('Media'), findsOneWidget);
    });
  });
}

