import 'dart:io';
import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import 'package:file_picker/file_picker.dart';
import '../models/app_shortcut.dart';
import 'icon_picker_dialog.dart';

/// App picker dialog
/// Allows user to add or edit an application with name, URL/path, and category
class AppPickerDialog extends StatefulWidget {
  final AppShortcut? editingApp;

  const AppPickerDialog({super.key, this.editingApp});

  @override
  State<AppPickerDialog> createState() => _AppPickerDialogState();
}

class _AppPickerDialogState extends State<AppPickerDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _targetController = TextEditingController();
  String _selectedCategory = 'Web';
  String? _selectedIcon;
  IconType? _selectedIconType;

  final List<String> _categories = ['Web', 'Dev', 'Media', 'All'];

  @override
  void initState() {
    super.initState();
    if (widget.editingApp != null) {
      _nameController.text = widget.editingApp!.name;
      _targetController.text = widget.editingApp!.target;
      _selectedCategory = widget.editingApp!.category;
      _selectedIcon = widget.editingApp!.iconPath;
      // Try to detect icon type from existing icon
      if (_selectedIcon != null && _selectedIcon!.isNotEmpty) {
        if (_selectedIcon!.contains('.') && File(_selectedIcon!).existsSync()) {
          _selectedIconType = IconType.image;
        } else if (int.tryParse(_selectedIcon!) != null) {
          _selectedIconType = IconType.materialIcon;
        } else if (_selectedIcon!.length <= 2) {
          _selectedIconType = IconType.emoji;
        }
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _targetController.dispose();
    super.dispose();
  }

  void _submit() {
    if (_formKey.currentState?.validate() ?? false) {
      final name = _nameController.text.trim();
      final target = _targetController.text.trim();

      if (name.isEmpty || target.isEmpty) {
        return;
      }

      final app = AppShortcut(
        id: widget.editingApp?.id ?? const Uuid().v4(),
        name: name,
        iconPath: _selectedIcon ?? widget.editingApp?.iconPath ?? '',
        target: target,
        category: _selectedCategory,
        type: _detectLaunchType(target),
      );

      Navigator.of(context).pop(app);
    }
  }

  LaunchType _detectLaunchType(String target) {
    if (target.startsWith('http://') || target.startsWith('https://')) {
      return LaunchType.url;
    }
    return LaunchType.exe;
  }

  /// Browse and select an executable file
  Future<void> _browseFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['exe', 'lnk', 'bat', 'cmd'],
        dialogTitle: 'Select Application',
      );

      if (result != null && result.files.isNotEmpty) {
        final filePath = result.files.first.path;
        if (filePath != null) {
          _populateFieldsFromFile(filePath);
        }
      }
    } catch (e) {
      _showError('Failed to browse file: $e');
    }
  }

  /// Populate form fields from selected file
  void _populateFieldsFromFile(String filePath) {
    _targetController.text = filePath;

    // Auto-fill app name from file name if empty
    if (_nameController.text.isEmpty) {
      final fileName = _extractFileName(filePath);
      _nameController.text = fileName;
    }

    // Note: Icon extraction will be added in future enhancement
    // For now, we store the exe path which can be used for icon extraction later
  }

  /// Extract clean file name from path
  String _extractFileName(String filePath) {
    final file = File(filePath);
    final fileName = file.uri.pathSegments.last;
    
    // Remove extension
    final nameWithoutExt = fileName.replaceAll(RegExp(r'\.(exe|lnk|bat|cmd)$'), '');
    
    // Clean up common patterns
    return _cleanFileName(nameWithoutExt);
  }

  /// Clean up file name for display
  String _cleanFileName(String name) {
    // Remove version numbers, underscores, etc.
    return name
        .replaceAll('_', ' ')
        .replaceAll('-', ' ')
        .trim()
        .split(' ')
        .map((word) => word.isEmpty ? '' : word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }

  /// Show error message
  void _showError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    }
  }

  /// Show icon picker dialog
  Future<void> _selectIcon() async {
    final result = await showDialog<IconPickerResult>(
      context: context,
      builder: (context) => IconPickerDialog(
        currentIcon: _selectedIcon,
        currentType: _selectedIconType,
      ),
    );

    if (result != null) {
      setState(() {
        _selectedIcon = result.value;
        _selectedIconType = result.type;
      });
    }
  }

  /// Build icon preview widget
  Widget _buildIconPreview() {
    if (_selectedIcon == null || _selectedIconType == null) {
      return Icon(
        Icons.apps,
        size: 24,
        color: Theme.of(context).colorScheme.primary,
      );
    }

    switch (_selectedIconType!) {
      case IconType.emoji:
        return Text(
          _selectedIcon!,
          style: const TextStyle(fontSize: 24),
        );
      case IconType.materialIcon:
        final codePoint = int.tryParse(_selectedIcon!);
        if (codePoint != null) {
          return Icon(
            IconData(codePoint, fontFamily: 'MaterialIcons'),
            size: 24,
            color: Theme.of(context).colorScheme.primary,
          );
        }
        return Icon(
          Icons.apps,
          size: 24,
          color: Theme.of(context).colorScheme.primary,
        );
      case IconType.image:
        final file = File(_selectedIcon!);
        if (file.existsSync()) {
          return ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: Image.file(
              file,
              width: 32,
              height: 32,
              fit: BoxFit.cover,
            ),
          );
        }
        return Icon(
          Icons.image,
          size: 24,
          color: Theme.of(context).colorScheme.primary,
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.editingApp != null;
    
    return AlertDialog(
      title: Text(isEditing ? 'Edit Application' : 'Add Application'),
      content: Form(
        key: _formKey,
        child: SizedBox(
          width: 400,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
              // Icon selector
              InkWell(
                onTap: _selectIcon,
                borderRadius: BorderRadius.circular(8),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
                    ),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Center(child: _buildIconPreview()),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Icon',
                              style: Theme.of(context).textTheme.titleSmall,
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Click to change',
                              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Theme.of(context).colorScheme.outline,
                                  ),
                            ),
                          ],
                        ),
                      ),
                      Icon(
                        Icons.edit,
                        size: 20,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'App Name',
                  hintText: 'e.g., Visual Studio Code',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Please enter app name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _targetController,
                      decoration: const InputDecoration(
                        labelText: 'URL or Path',
                        hintText: 'https://example.com or C:\\App.exe',
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Please enter URL or path';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  Tooltip(
                    message: 'Browse',
                    child: IconButton(
                      icon: const Icon(Icons.folder_open),
                      onPressed: _browseFile,
                      style: IconButton.styleFrom(
                        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                        foregroundColor: Theme.of(context).colorScheme.onPrimaryContainer,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedCategory,
                decoration: const InputDecoration(
                  labelText: 'Category',
                  border: OutlineInputBorder(),
                ),
                items: _categories.map((category) {
                  return DropdownMenuItem(
                    value: category,
                    child: Text(category),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _selectedCategory = value;
                    });
                  }
                },
              ),
            ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        TextButton(
          onPressed: _submit,
          child: Text(isEditing ? 'Save' : 'Add'),
        ),
      ],
    );
  }
}

