import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:asset_maintenance_app/models/user_model.dart';

class StorageService {
  static late SharedPreferences _prefs;

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // User
  static Future<void> saveUser(User user) async {
    final userJson = jsonEncode(user.toJson());
    await _prefs.setString('user', userJson);
  }

  static User? getUser() {
    final userJson = _prefs.getString('user');
    if (userJson == null) return null;
    try {
      return User.fromJson(jsonDecode(userJson));
    } catch (e) {
      return null;
    }
  }

  static Future<void> clearUser() async {
    await _prefs.remove('user');
  }

  // Auth Token
  static Future<void> saveToken(String token) async {
    await _prefs.setString('auth_token', token);
  }

  static String? getToken() {
    return _prefs.getString('auth_token');
  }

  static Future<void> clearToken() async {
    await _prefs.remove('auth_token');
  }

  // Session
  static Future<void> clearSession() async {
    await clearUser();
    await clearToken();
  }

  // Remember me
  static Future<void> setRememberMe(bool value) async {
    await _prefs.setBool('remember_me', value);
  }

  static bool getRememberMe() {
    return _prefs.getBool('remember_me') ?? false;
  }

  // Last username
  static Future<void> setLastUsername(String username) async {
    await _prefs.setString('last_username', username);
  }

  static String? getLastUsername() {
    return _prefs.getString('last_username');
  }

  // App preferences
  static Future<void> setThemeMode(String mode) async {
    await _prefs.setString('theme_mode', mode);
  }

  static String getThemeMode() {
    return _prefs.getString('theme_mode') ?? 'light';
  }

  static Future<void> setNotificationsEnabled(bool enabled) async {
    await _prefs.setBool('notifications_enabled', enabled);
  }

  static bool getNotificationsEnabled() {
    return _prefs.getBool('notifications_enabled') ?? true;
  }

  // Cache
  static Future<void> cacheData(String key, dynamic data) async {
    try {
      final json = jsonEncode(data);
      await _prefs.setString('cache_$key', json);
    } catch (e) {
      // Handle cache errors silently
    }
  }

  static dynamic getCachedData(String key) {
    try {
      final json = _prefs.getString('cache_$key');
      return json != null ? jsonDecode(json) : null;
    } catch (e) {
      return null;
    }
  }

  static Future<void> clearCache() async {
    final keys = _prefs.getKeys();
    for (final key in keys) {
      if (key.startsWith('cache_')) {
        await _prefs.remove(key);
      }
    }
  }
}
