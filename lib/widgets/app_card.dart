import 'package:flutter/material.dart';
import '../models/app_shortcut.dart';

/// Application card widget
/// Displays app icon and name in a clickable card with context menu
class AppCard extends StatelessWidget {
  final AppShortcut app;
  final VoidCallback onTap;
  final void Function(AppShortcut)? onEdit;
  final void Function(AppShortcut)? onRename;

  const AppCard({
    super.key,
    required this.app,
    required this.onTap,
    this.onEdit,
    this.onRename,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onSecondaryTapDown: (details) => _showContextMenu(context, details),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(8),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              _buildIcon(context),
              const SizedBox(height: 8),
              _buildLabel(context),
            ],
          ),
        ),
      ),
    );
  }

  void _showContextMenu(BuildContext context, TapDownDetails details) {
    final overlay = Overlay.of(context).context.findRenderObject() as RenderBox;
    
    showMenu(
      context: context,
      position: RelativeRect.fromRect(
        details.globalPosition & const Size(40, 40),
        Offset.zero & overlay.size,
      ),
      items: [
        PopupMenuItem(
          value: 'open',
          child: const Row(
            children: [
              Icon(Icons.open_in_new, size: 18),
              SizedBox(width: 12),
              Text('Open'),
            ],
          ),
        ),
        PopupMenuItem(
          value: 'edit',
          child: const Row(
            children: [
              Icon(Icons.edit, size: 18),
              SizedBox(width: 12),
              Text('Edit'),
            ],
          ),
        ),
        PopupMenuItem(
          value: 'rename',
          child: const Row(
            children: [
              Icon(Icons.drive_file_rename_outline, size: 18),
              SizedBox(width: 12),
              Text('Rename'),
            ],
          ),
        ),
      ],
    ).then((value) {
      if (value == 'open') {
        onTap();
      } else if (value == 'edit' && onEdit != null) {
        onEdit!(app);
      } else if (value == 'rename' && onRename != null) {
        onRename!(app);
      }
    });
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
    // Calculate if text will overflow
    // We check if the text needs more than 2 lines to display fully
    final textPainter = TextPainter(
      text: TextSpan(
        text: app.name,
        style: Theme.of(context).textTheme.bodySmall,
      ),
      maxLines: 2,
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
    );

    // Layout with a reasonable max width (card width minus padding)
    textPainter.layout(maxWidth: 74); // 90px card - 16px padding
    final didExceedMaxLines = textPainter.didExceedMaxLines;

    return Flexible(
      child: didExceedMaxLines
          ? Tooltip(
              message: app.name,
              waitDuration: const Duration(milliseconds: 500),
              child: Text(
                app.name,
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            )
          : Text(
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
