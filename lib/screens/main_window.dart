import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:window_manager/window_manager.dart';
import '../models/app_shortcut.dart';
import '../providers/app_state.dart';
import '../services/app_launcher_service.dart';
import '../widgets/custom_title_bar.dart';
import '../widgets/app_card.dart';
import '../widgets/add_app_button.dart';
import '../widgets/app_picker_dialog.dart';

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

  Future<void> _launchApp(AppShortcut app) async {
    final success = await _launcherService.launch(app);
    if (!success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to launch ${app.name}')),
      );
    }
  }

  Future<void> _showAddAppDialog() async {
    final app = await showDialog<AppShortcut>(
      context: context,
      builder: (context) => const AppPickerDialog(),
    );

    if (app != null && mounted) {
      Provider.of<AppState>(context, listen: false).addApp(app);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${app.name} added successfully')),
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
          _buildTabBar(),
          Expanded(
            child: _buildContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Consumer<AppState>(
      builder: (context, state, child) {
        return Container(
          height: 50,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
            border: Border(
              bottom: BorderSide(
                color: Theme.of(context).colorScheme.outline.withOpacity(0.2),
              ),
            ),
          ),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: Row(
              children: state.categories.map((category) {
                final isSelected = category == state.selectedCategory;
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: ChoiceChip(
                    label: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(category.icon),
                        const SizedBox(width: 6),
                        Text(category.name),
                      ],
                    ),
                    selected: isSelected,
                    onSelected: (_) => state.selectCategory(category),
                    showCheckmark: false,
                  ),
                );
              }).toList(),
            ),
          ),
        );
      },
    );
  }

  Widget _buildContent() {
    return Consumer<AppState>(
      builder: (context, state, child) {
        final apps = state.filteredApps;

        if (apps.isEmpty) {
          return _buildEmptyStateWithFAB();
        }

        // Fixed-size grid configuration (like Windows Explorer/Android launcher)
        // Cards maintain fixed size, window resize only affects how many fit horizontally
        const cellWidth = 90.0;
        const cellHeight = 100.0;
        const horizontalPadding = 10.0;
        const verticalPadding = 10.0;
        const spacing = 4.0;

        return Stack(
          children: [
            Container(
              color: Theme.of(context).colorScheme.surface,
              padding: const EdgeInsets.only(
                left: horizontalPadding,
                right: horizontalPadding,
                top: verticalPadding,
                bottom: verticalPadding,
              ),
              child: SingleChildScrollView(
                child: Align(
                  alignment: Alignment.topLeft,
                  child: Wrap(
                    alignment: WrapAlignment.start,
                    spacing: spacing,
                    runSpacing: spacing,
                    children: apps.map((app) {
                      return SizedBox(
                        width: cellWidth,
                        height: cellHeight,
                        child: AppCard(
                          app: app,
                          onTap: () => _launchApp(app),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
            ),
            Positioned(
              right: 16,
              bottom: 16,
              child: AddAppButton(
                onTap: _showAddAppDialog,
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.inbox_outlined,
            size: 64,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No apps in this category',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyStateWithFAB() {
    return Stack(
      children: [
        _buildEmptyState(),
        Positioned(
          right: 16,
          bottom: 16,
          child: AddAppButton(
            onTap: _showAddAppDialog,
          ),
        ),
      ],
    );
  }
}
