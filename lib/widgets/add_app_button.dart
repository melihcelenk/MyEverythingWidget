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
    return Material(
      elevation: 6,
      shape: const CircleBorder(),
      color: Theme.of(context).colorScheme.primaryContainer,
      child: InkWell(
        onTap: onTap,
        customBorder: const CircleBorder(),
        child: Container(
          constraints: const BoxConstraints(
            minWidth: 56,
            minHeight: 56,
          ),
          decoration: const BoxDecoration(
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.add,
            size: 28,
            color: Theme.of(context).colorScheme.onPrimaryContainer,
          ),
        ),
      ),
    );
  }
}

