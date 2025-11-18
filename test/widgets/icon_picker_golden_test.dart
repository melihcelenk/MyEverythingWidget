import 'package:alchemist/alchemist.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_everything_widget/widgets/icon_picker_dialog.dart';

void main() {
  group('Icon Picker Golden Tests', () {
    goldenTest(
      'Emoji grid layout - spacing and overlap check',
      fileName: 'icon_picker_emoji_grid',
      builder: () => GoldenTestGroup(
        scenarioConstraints: const BoxConstraints(maxWidth: 700, maxHeight: 500),
        children: [
          GoldenTestScenario(
            name: 'emoji grid with proper spacing',
            child: MaterialApp(
              theme: ThemeData.light(),
              home: Scaffold(
                body: SizedBox(
                  width: 650,
                  height: 450,
                  child: _EmojiGridTest(),
                ),
              ),
            ),
          ),
        ],
      ),
    );

    goldenTest(
      'Material icon grid layout - spacing and overlap check',
      fileName: 'icon_picker_material_grid',
      builder: () => GoldenTestGroup(
        scenarioConstraints: const BoxConstraints(maxWidth: 700, maxHeight: 500),
        children: [
          GoldenTestScenario(
            name: 'material icon grid with proper spacing',
            child: MaterialApp(
              theme: ThemeData.light(),
              home: Scaffold(
                body: SizedBox(
                  width: 650,
                  height: 450,
                  child: _IconGridTest(),
                ),
              ),
            ),
          ),
        ],
      ),
    );

    goldenTest(
      'Upload area layout',
      fileName: 'icon_picker_upload_area',
      builder: () => GoldenTestGroup(
        scenarioConstraints: const BoxConstraints(maxWidth: 700, maxHeight: 500),
        children: [
          GoldenTestScenario(
            name: 'upload area centered and compact',
            child: MaterialApp(
              theme: ThemeData.light(),
              home: Scaffold(
                body: SizedBox(
                  width: 650,
                  height: 450,
                  child: _UploadViewTest(),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  });
}

/// Isolated emoji grid for testing
class _EmojiGridTest extends StatelessWidget {
  final List<String> _emojis = [
    '📱', '💻', '🌐', '📁', '📝', '📊', '📈', '📉',
    '🎵', '🎮', '🎨', '🎬', '📷', '📹', '🎤', '🎧',
    '⚙️', '🔧', '🔨', '🛠️', '⚡', '🔥', '💡', '🔒',
    '📧', '💬', '📞', '📱', '🌟', '⭐', '❤️', '💚',
    '🚀', '✈️', '🚗', '🚲', '⚽', '🏀', '🎯', '🎲',
    '☀️', '🌙', '⭐', '🌈', '🔔', '🎁', '🏆', '👍',
  ];

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: GridView.builder(
        padding: EdgeInsets.zero,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 6,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.0,
        ),
        itemCount: _emojis.length,
        itemBuilder: (context, index) {
          final emoji = _emojis[index];
          return InkWell(
            onTap: () {},
            borderRadius: BorderRadius.circular(6),
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest.withOpacity(0.3),
                borderRadius: BorderRadius.circular(6),
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
}

/// Isolated material icon grid for testing
class _IconGridTest extends StatelessWidget {
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
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: GridView.builder(
        padding: EdgeInsets.zero,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 6,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.0,
        ),
        itemCount: _materialIcons.length,
        itemBuilder: (context, index) {
          final icon = _materialIcons[index];
          return InkWell(
            onTap: () {},
            borderRadius: BorderRadius.circular(6),
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest.withOpacity(0.3),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Icon(icon, size: 24),
            ),
          );
        },
      ),
    );
  }
}

/// Isolated upload view for testing
class _UploadViewTest extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: DragTarget<String>(
          onAcceptWithDetails: (details) {},
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
                    onPressed: () {},
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
    );
  }
}
