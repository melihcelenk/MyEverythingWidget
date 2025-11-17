import 'dart:io';
import 'dart:typed_data';
import 'package:path_provider/path_provider.dart';
import 'package:win32/win32.dart';

/// Service for extracting and managing application icons
class IconExtractionService {
  /// Extract icon from executable file and save it
  /// Returns the path to the saved icon file, or null if extraction fails
  Future<String?> extractAndSaveIcon(String exePath) async {
    try {
      if (!await _isValidExecutable(exePath)) {
        return null;
      }

      final iconData = await _extractIconFromExe(exePath);
      if (iconData == null) {
        return null;
      }

      final savedPath = await _saveIconToFile(iconData, exePath);
      return savedPath;
    } catch (e) {
      print('Failed to extract icon: $e');
      return null;
    }
  }

  /// Check if file is a valid executable
  Future<bool> _isValidExecutable(String path) async {
    final file = File(path);
    if (!await file.exists()) return false;

    final extension = path.toLowerCase().split('.').last;
    return ['exe', 'lnk'].contains(extension);
  }

  /// Extract icon data from executable using Win32 API
  Future<Uint8List?> _extractIconFromExe(String exePath) async {
    try {
      // Use Win32 API to extract icon
      final exePathPtr = exePath.toNativeUtf16();
      
      // Extract large icon (32x32)
      final hIcon = ExtractIcon(0, exePathPtr, 0);
      
      if (hIcon == 0 || hIcon == 1) {
        // No icon or error
        free(exePathPtr);
        return null;
      }

      // TODO: Convert HICON to bitmap data
      // For now, we'll use a placeholder approach
      // In production, you'd use GetIconInfo and GetBitmapBits
      
      DestroyIcon(hIcon);
      free(exePathPtr);
      
      return null; // Will implement actual conversion
    } catch (e) {
      print('Win32 icon extraction error: $e');
      return null;
    }
  }

  /// Save icon data to application directory
  Future<String?> _saveIconToFile(Uint8List iconData, String sourcePath) async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      final iconsDir = Directory('${appDir.path}/app_icons');
      
      if (!await iconsDir.exists()) {
        await iconsDir.create(recursive: true);
      }

      final fileName = _generateIconFileName(sourcePath);
      final iconFile = File('${iconsDir.path}/$fileName');
      
      await iconFile.writeAsBytes(iconData);
      return iconFile.path;
    } catch (e) {
      print('Failed to save icon: $e');
      return null;
    }
  }

  /// Generate unique icon file name from source path
  String _generateIconFileName(String sourcePath) {
    final hash = sourcePath.hashCode.abs().toString();
    return 'icon_$hash.png';
  }

  /// Delete icon file
  Future<void> deleteIcon(String iconPath) async {
    try {
      final file = File(iconPath);
      if (await file.exists()) {
        await file.delete();
      }
    } catch (e) {
      print('Failed to delete icon: $e');
    }
  }

  /// Check if icon file exists
  Future<bool> iconExists(String iconPath) async {
    try {
      final file = File(iconPath);
      return await file.exists();
    } catch (e) {
      return false;
    }
  }
}

