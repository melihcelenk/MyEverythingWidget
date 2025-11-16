import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';

/// Custom draggable title bar with window controls
/// Features:
/// - Drag to move window
/// - Always-on-top toggle
/// - Close button
class CustomTitleBar extends StatelessWidget {
  final String title;
  final bool isAlwaysOnTop;
  final VoidCallback onAlwaysOnTopToggle;

  const CustomTitleBar({
    super.key,
    required this.title,
    required this.isAlwaysOnTop,
    required this.onAlwaysOnTopToggle,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanStart: (_) => windowManager.startDragging(),
      child: Container(
        height: 40,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.primaryContainer,
        ),
        child: Row(
          children: [
            const SizedBox(width: 12),
            _buildTitle(context),
            const Spacer(),
            _buildAlwaysOnTopButton(),
            _buildCloseButton(),
            const SizedBox(width: 4),
          ],
        ),
      ),
    );
  }

  Widget _buildTitle(BuildContext context) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
    );
  }

  Widget _buildAlwaysOnTopButton() {
    return IconButton(
      icon: Icon(
        isAlwaysOnTop ? Icons.push_pin : Icons.push_pin_outlined,
        size: 18,
      ),
      onPressed: onAlwaysOnTopToggle,
      tooltip: 'Always on top',
    );
  }

  Widget _buildCloseButton() {
    return IconButton(
      icon: const Icon(Icons.close, size: 18),
      onPressed: () => windowManager.close(),
      tooltip: 'Close',
    );
  }
}
