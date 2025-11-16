import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';
import '../models/app_shortcut.dart';
import '../services/app_launcher_service.dart';
import '../widgets/custom_title_bar.dart';
import '../widgets/app_card.dart';

/// Main application window
/// Manages window state and displays primary content
class MainWindow extends StatefulWidget {
  const MainWindow({super.key});

  @override
  State<MainWindow> createState() => _MainWindowState();
}

class _MainWindowState extends State<MainWindow> with WindowListener {
  bool _isAlwaysOnTop = true;
  final _launcherService = AppLauncherService();
  late List<AppShortcut> _apps;

  @override
  void initState() {
    super.initState();
    windowManager.addListener(this);
    _initWindow();
    _loadApps();
  }

  @override
  void dispose() {
    windowManager.removeListener(this);
    super.dispose();
  }

  Future<void> _initWindow() async {
    await windowManager.setAlwaysOnTop(_isAlwaysOnTop);
  }

  void _loadApps() {
    // Hardcoded apps for MVP
    _apps = [
      const AppShortcut(
        id: '1',
        name: 'Chrome',
        iconPath: '',
        target: 'https://google.com',
        category: 'Web',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '2',
        name: 'GitHub',
        iconPath: '',
        target: 'https://github.com',
        category: 'Dev',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '3',
        name: 'YouTube',
        iconPath: '',
        target: 'https://youtube.com',
        category: 'Media',
        type: LaunchType.url,
      ),
      const AppShortcut(
        id: '4',
        name: 'Documents',
        iconPath: '',
        target: r'C:\Users',
        category: 'Files',
        type: LaunchType.folder,
      ),
    ];
  }

  Future<void> _toggleAlwaysOnTop() async {
    setState(() {
      _isAlwaysOnTop = !_isAlwaysOnTop;
    });
    await windowManager.setAlwaysOnTop(_isAlwaysOnTop);
  }

  Future<void> _launchApp(AppShortcut app) async {
    final success = await _launcherService.launch(app);
    if (!success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to launch ${app.name}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          CustomTitleBar(
            title: 'My Everything',
            isAlwaysOnTop: _isAlwaysOnTop,
            onAlwaysOnTopToggle: _toggleAlwaysOnTop,
          ),
          Expanded(
            child: _buildContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return Container(
      color: Theme.of(context).colorScheme.surface,
      padding: const EdgeInsets.all(16),
      child: GridView.builder(
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3,
          crossAxisSpacing: 8,
          mainAxisSpacing: 8,
          childAspectRatio: 1.0,
        ),
        itemCount: _apps.length,
        itemBuilder: (context, index) {
          return AppCard(
            app: _apps[index],
            onTap: () => _launchApp(_apps[index]),
          );
        },
      ),
    );
  }
}
