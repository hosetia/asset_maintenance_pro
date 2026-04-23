import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:asset_maintenance_app/models/user_model.dart';
import 'package:asset_maintenance_app/services/api_service.dart';
import 'package:asset_maintenance_app/services/storage_service.dart';

final authServiceProvider = Provider((ref) => ApiService());

final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final apiService = ref.watch(authServiceProvider);
  return AuthNotifier(apiService);
});

class AuthState {
  final User? user;
  final bool isLoading;
  final String? error;
  final bool isAuthenticated;

  const AuthState({
    this.user,
    this.isLoading = false,
    this.error,
    this.isAuthenticated = false,
  });

  AuthState copyWith({
    User? user,
    bool? isLoading,
    String? error,
    bool? isAuthenticated,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiService apiService;

  AuthNotifier(this.apiService) : super(const AuthState()) {
    _initializeAuth();
  }

  Future<void> _initializeAuth() async {
    final token = StorageService.getToken();
    final user = StorageService.getUser();

    if (token != null && user != null) {
      apiService.setAuthToken(token);
      state = state.copyWith(
        user: user,
        isAuthenticated: true,
      );
    }
  }

  Future<bool> login(String username, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final user = await apiService.login(username, password);

      await StorageService.saveUser(user);
      if (user.token != null) {
        await StorageService.saveToken(user.token!);
      }

      state = state.copyWith(
        user: user,
        isAuthenticated: true,
        isLoading: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return false;
    }
  }

  Future<void> logout() async {
    await StorageService.clearSession();
    state = const AuthState();
  }

  Future<void> updateUserProfile(User updatedUser) async {
    await StorageService.saveUser(updatedUser);
    state = state.copyWith(user: updatedUser);
  }
}
