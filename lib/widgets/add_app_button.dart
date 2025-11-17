import 'package:flutter/material.dart';

/// Add app button widget
/// Displays a circular floating button with + icon for adding new apps
class AddAppButton extends StatelessWidget {
  final VoidCallback onTap;

  const AddAppButton({
    super.key,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return Material(
      elevation: 4,
      shape: const CircleBorder(),
      color: colorScheme.tertiaryContainer,
      child: InkWell(
        onTap: onTap,
        customBorder: const CircleBorder(),
        child: Container(
          constraints: const BoxConstraints(
            minWidth: 48,
            minHeight: 48,
          ),
          decoration: const BoxDecoration(
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.add,
            size: 24,
            color: colorScheme.onTertiaryContainer,
          ),
        ),
      ),
    );
  }
}

