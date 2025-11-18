import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

/// Icon selection result
class IconPickerResult {
  final IconType type;
  final String value;

  const IconPickerResult({
    required this.type,
    required this.value,
  });
}

enum IconType {
  emoji,
  materialIcon,
  image,
}

/// Notion-style icon picker dialog
/// Allows selecting emoji, material icons, or uploading custom images
class IconPickerDialog extends StatefulWidget {
  final String? currentIcon;
  final IconType? currentType;

  const IconPickerDialog({
    super.key,
    this.currentIcon,
    this.currentType,
  });

  @override
  State<IconPickerDialog> createState() => _IconPickerDialogState();
}

class _IconPickerDialogState extends State<IconPickerDialog>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _searchQuery = '';

  // Emoji list - commonly used emojis
  final List<String> _emojis = [
    '📱', '💻', '🌐', '📁', '📝', '📊', '📈', '📉',
    '🎵', '🎮', '🎨', '🎬', '📷', '📹', '🎤', '🎧',
    '⚙️', '🔧', '🔨', '🛠️', '⚡', '🔥', '💡', '🔒',
    '📧', '💬', '📞', '📱', '🌟', '⭐', '❤️', '💚',
    '🚀', '✈️', '🚗', '🚲', '⚽', '🏀', '🎯', '🎲',
    '☀️', '🌙', '⭐', '🌈', '🔔', '🎁', '🏆', '👍',
  ];

  // Material icons - commonly used icons
  final List<IconData> _materialIcons = [
    Icons.apps, Icons.language, Icons.folder, Icons.description,
    Icons.settings, Icons.home, Icons.work, Icons.school,
    Icons.music_note, Icons.movie, Icons.image, Icons.camera,
    Icons.email, Icons.message, Icons.phone, Icons.call,
    Icons.favorite, Icons.star, Icons.shopping_cart, Icons.payment,
    Icons.dashboard, Icons.analytics, Icons.trending_up, Icons.trending_down,
    Icons.calendar_today, Icons.schedule, Icons.alarm, Icons.timer,
    Icons.cloud, Icons.download, Icons.upload, Icons.share,
    Icons.edit, Icons.delete, Icons.add, Icons.remove,
    Icons.search, Icons.filter_list, Icons.sort, Icons.view_list,
    Icons.notifications, Icons.bookmark, Icons.flag, Icons.label,
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  /// Filter emojis based on search query
  List<String> get _filteredEmojis {
    if (_searchQuery.isEmpty) return _emojis;
    return _emojis;
  }

  /// Filter icons based on search query
  List<IconData> get _filteredIcons {
    if (_searchQuery.isEmpty) return _materialIcons;
    return _materialIcons;
  }

  /// Handle emoji selection
  void _selectEmoji(String emoji) {
    Navigator.of(context).pop(
      IconPickerResult(type: IconType.emoji, value: emoji),
    );
  }

  /// Handle material icon selection
  void _selectMaterialIcon(IconData icon) {
    Navigator.of(context).pop(
      IconPickerResult(
        type: IconType.materialIcon,
        value: icon.codePoint.toString(),
      ),
    );
  }

  /// Handle image upload
  Future<void> _uploadImage() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        dialogTitle: 'Select Icon Image',
      );

      if (result != null && result.files.isNotEmpty) {
        final filePath = result.files.first.path;
        if (filePath != null && mounted) {
          Navigator.of(context).pop(
            IconPickerResult(type: IconType.image, value: filePath),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to upload image: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        width: 650,
        height: 600,
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildHeader(),
            const SizedBox(height: 16),
            _buildSearchBar(),
            const SizedBox(height: 16),
            _buildTabBar(),
            const SizedBox(height: 16),
            Expanded(child: _buildTabView()),
          ],
        ),
      ),
    );
  }

  /// Build header with title and close button
  Widget _buildHeader() {
    return Row(
      children: [
        const Text(
          'Select Icon',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const Spacer(),
        IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ],
    );
  }

  /// Build search bar
  Widget _buildSearchBar() {
    return TextField(
      decoration: InputDecoration(
        hintText: 'Filter...',
        prefixIcon: const Icon(Icons.search),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16),
      ),
      onChanged: (value) {
        setState(() {
          _searchQuery = value.toLowerCase();
        });
      },
    );
  }

  /// Build tab bar
  Widget _buildTabBar() {
    return TabBar(
      controller: _tabController,
      tabs: const [
        Tab(text: 'Emoji'),
        Tab(text: 'Icons'),
        Tab(text: 'Upload'),
      ],
    );
  }

  /// Build tab view
  Widget _buildTabView() {
    return TabBarView(
      controller: _tabController,
      children: [
        _buildEmojiGrid(),
        _buildIconGrid(),
        _buildUploadView(),
      ],
    );
  }

  /// Build emoji grid
  Widget _buildEmojiGrid() {
    // Use Expanded with Column to ensure GridView gets proper constraints
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: GridView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 6,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.0,
        ),
        itemCount: _filteredEmojis.length,
        itemBuilder: (context, index) {
          final emoji = _filteredEmojis[index];
          if (index < 10) {
            debugPrint('Building emoji $index: $emoji');
          }
          return InkWell(
            onTap: () => _selectEmoji(emoji),
            borderRadius: BorderRadius.circular(6),
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest.withOpacity(0.3),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                  color: Colors.red,
                  width: 1,
                ),
              ),
              child: Center(
                child: Text(
                  emoji,
                  style: const TextStyle(fontSize: 32),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  /// Build material icon grid
  Widget _buildIconGrid() {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: GridView.builder(
        physics: const AlwaysScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 6,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.0,
        ),
        itemCount: _filteredIcons.length,
        itemBuilder: (context, index) {
          final icon = _filteredIcons[index];
          return InkWell(
            onTap: () => _selectMaterialIcon(icon),
            borderRadius: BorderRadius.circular(6),
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest.withOpacity(0.3),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                  color: Colors.red,
                  width: 1,
                ),
              ),
              child: Center(
                child: Icon(icon, size: 24),
              ),
            ),
          );
        },
      ),
    );
  }

  /// Build upload view
  Widget _buildUploadView() {
    return SingleChildScrollView(
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: DragTarget<String>(
            onAcceptWithDetails: (details) {
              // Handle drag & drop
              final path = details.data;
              if (path.endsWith('.png') ||
                  path.endsWith('.jpg') ||
                  path.endsWith('.jpeg') ||
                  path.endsWith('.gif') ||
                  path.endsWith('.webp')) {
                Navigator.of(context).pop(
                  IconPickerResult(type: IconType.image, value: path),
                );
              }
            },
            builder: (context, candidateData, rejectedData) {
              final isDragging = candidateData.isNotEmpty;
              return Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  border: Border.all(
                    color: isDragging
                        ? Theme.of(context).colorScheme.primary
                        : Theme.of(context).colorScheme.outline.withOpacity(0.3),
                    width: isDragging ? 2 : 1,
                    style: BorderStyle.solid,
                  ),
                  borderRadius: BorderRadius.circular(12),
                  color: isDragging
                      ? Theme.of(context).colorScheme.primaryContainer.withOpacity(0.1)
                      : null,
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      isDragging ? Icons.download : Icons.cloud_upload,
                      size: 48,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      isDragging ? 'Drop to Upload' : 'Upload Custom Icon',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      isDragging
                          ? 'Release to select this image'
                          : 'Drag & drop an image or click to browse',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Theme.of(context).colorScheme.outline,
                          ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _uploadImage,
                      icon: const Icon(Icons.upload_file),
                      label: const Text('Choose File'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 10,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

