import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';

void main() async {
  // Ensure Flutter binding is initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize window manager
  await windowManager.ensureInitialized();

  // Configure window options
  WindowOptions windowOptions = const WindowOptions(
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

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My Everything Widget',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      home: const MainWindow(),
    );
  }
}

class MainWindow extends StatefulWidget {
  const MainWindow({super.key});

  @override
  State<MainWindow> createState() => _MainWindowState();
}

class _MainWindowState extends State<MainWindow> with WindowListener {
  bool _isAlwaysOnTop = true;

  @override
  void initState() {
    super.initState();
    windowManager.addListener(this);
    _initWindow();
  }

  @override
  void dispose() {
    windowManager.removeListener(this);
    super.dispose();
  }

  Future<void> _initWindow() async {
    await windowManager.setAlwaysOnTop(_isAlwaysOnTop);
  }

  Future<void> _toggleAlwaysOnTop() async {
    setState(() {
      _isAlwaysOnTop = !_isAlwaysOnTop;
    });
    await windowManager.setAlwaysOnTop(_isAlwaysOnTop);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Custom title bar
          GestureDetector(
            onPanStart: (details) {
              windowManager.startDragging();
            },
            child: Container(
              height: 40,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer,
              ),
              child: Row(
                children: [
                  const SizedBox(width: 12),
                  Text(
                    'My Everything',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const Spacer(),
                  // Always on top toggle
                  IconButton(
                    icon: Icon(
                      _isAlwaysOnTop ? Icons.push_pin : Icons.push_pin_outlined,
                      size: 18,
                    ),
                    onPressed: _toggleAlwaysOnTop,
                    tooltip: 'Always on top',
                  ),
                  // Close button
                  IconButton(
                    icon: const Icon(Icons.close, size: 18),
                    onPressed: () async {
                      await windowManager.close();
                    },
                    tooltip: 'Close',
                  ),
                  const SizedBox(width: 4),
                ],
              ),
            ),
          ),
          // Content area
          Expanded(
            child: Container(
              color: Theme.of(context).colorScheme.surface,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.widgets_outlined,
                      size: 64,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'MyEverythingWidget',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'v1.0 MVP - In Development',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
