import 'dart:io';
import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import 'package:file_picker/file_picker.dart';
import '../models/app_shortcut.dart';

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

  final List<String> _categories = ['Web', 'Dev', 'Media', 'All'];

  @override
  void initState() {
    super.initState();
    if (widget.editingApp != null) {
      _nameController.text = widget.editingApp!.name;
      _targetController.text = widget.editingApp!.target;
      _selectedCategory = widget.editingApp!.category;
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
        iconPath: widget.editingApp?.iconPath ?? '',
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

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.editingApp != null;
    
    return AlertDialog(
      title: Text(isEditing ? 'Edit Application' : 'Add Application'),
      content: Form(
        key: _formKey,
        child: SizedBox(
          width: 400,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
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

