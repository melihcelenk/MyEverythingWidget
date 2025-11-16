/// Category model for organizing apps and notes
class AppCategory {
  final String id;
  final String name;
  final String icon;

  const AppCategory({
    required this.id,
    required this.name,
    required this.icon,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AppCategory && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
}
