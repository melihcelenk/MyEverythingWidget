import 'dart:io';
import 'package:url_launcher/url_launcher.dart';
import '../models/app_shortcut.dart';

/// Service for launching applications and URLs
class AppLauncherService {
  /// Launch an application shortcut
  Future<bool> launch(AppShortcut shortcut) async {
    try {
      switch (shortcut.type) {
        case LaunchType.exe:
          return await _launchExecutable(shortcut.target);
        case LaunchType.url:
          return await _launchUrl(shortcut.target);
        case LaunchType.folder:
          return await _openFolder(shortcut.target);
      }
    } catch (e) {
      // Log error in production
      return false;
    }
  }

  Future<bool> _launchExecutable(String path) async {
    try {
      await Process.start(path, [], mode: ProcessStartMode.detached);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    return await launchUrl(uri, mode: LaunchMode.externalApplication);
  }

  Future<bool> _openFolder(String path) async {
    try {
      // Windows: explorer.exe
      if (Platform.isWindows) {
        await Process.start('explorer.exe', [path], mode: ProcessStartMode.detached);
        return true;
      }
      // Linux: xdg-open
      else if (Platform.isLinux) {
        await Process.start('xdg-open', [path], mode: ProcessStartMode.detached);
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}
