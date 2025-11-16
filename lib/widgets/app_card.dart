import 'package:flutter/material.dart';
import '../models/app_shortcut.dart';

/// Application card widget
/// Displays app icon and name in a clickable card
class AppCard extends StatelessWidget {
  final AppShortcut app;
  final VoidCallback onTap;

  const AppCard({
    super.key,
    required this.app,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(8),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildIcon(context),
            const SizedBox(height: 8),
            _buildLabel(context),
          ],
        ),
      ),
    );
  }

  Widget _buildIcon(BuildContext context) {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Icon(
        _getIconForType(),
        size: 24,
        color: Theme.of(context).colorScheme.primary,
      ),
    );
  }

  Widget _buildLabel(BuildContext context) {
    return Flexible(
      child: Text(
        app.name,
        style: Theme.of(context).textTheme.bodySmall,
        textAlign: TextAlign.center,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
      ),
    );
  }

  IconData _getIconForType() {
    switch (app.type) {
      case LaunchType.exe:
        return Icons.apps;
      case LaunchType.url:
        return Icons.language;
      case LaunchType.folder:
        return Icons.folder;
    }
  }
}
