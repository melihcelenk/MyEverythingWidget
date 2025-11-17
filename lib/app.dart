import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/app_state.dart';
import 'screens/main_window.dart';

/// Root application widget
/// Configures MaterialApp with theme and routing
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppState(),
      child: MaterialApp(
        title: 'My Everything Widget',
        debugShowCheckedModeBanner: false,
        theme: _buildLightTheme(),
        darkTheme: _buildDarkTheme(),
        themeMode: ThemeMode.system,
        home: const MainWindow(),
      ),
    );
  }

  ThemeData _buildLightTheme() {
    final baseColorScheme = ColorScheme.fromSeed(seedColor: Colors.blue);
    return ThemeData(
      colorScheme: baseColorScheme.copyWith(
        tertiaryContainer: Colors.green.shade100,
        onTertiaryContainer: Colors.green.shade900,
      ),
      useMaterial3: true,
    );
  }

  ThemeData _buildDarkTheme() {
    final baseColorScheme = ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.dark,
    );
    return ThemeData(
      colorScheme: baseColorScheme.copyWith(
        tertiaryContainer: Colors.green.shade800,
        onTertiaryContainer: Colors.green.shade100,
      ),
      useMaterial3: true,
    );
  }
}
