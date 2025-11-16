import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';
import 'app.dart';

/// Application entry point
/// Initializes window manager and launches app
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await _initializeWindow();
  runApp(const MyApp());
}

/// Initialize and configure window
Future<void> _initializeWindow() async {
  await windowManager.ensureInitialized();

  const windowOptions = WindowOptions(
    size: Size(320, 500),
    center: true,
    backgroundColor: Colors.transparent,
    skipTaskbar: false,
    titleBarStyle: TitleBarStyle.hidden,
  );

  await windowManager.waitUntilReadyToShow(windowOptions, () async {
    await windowManager.show();
    await windowManager.focus();
  });
}
