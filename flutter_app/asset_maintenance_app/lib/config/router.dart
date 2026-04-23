import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:asset_maintenance_app/screens/auth/login_screen.dart';
import 'package:asset_maintenance_app/screens/home/home_screen.dart';
import 'package:asset_maintenance_app/screens/assets/assets_screen.dart';
import 'package:asset_maintenance_app/screens/assets/asset_detail_screen.dart';
import 'package:asset_maintenance_app/screens/maintenance/maintenance_list_screen.dart';
import 'package:asset_maintenance_app/screens/maintenance/maintenance_detail_screen.dart';
import 'package:asset_maintenance_app/screens/maintenance/create_maintenance_screen.dart';
import 'package:asset_maintenance_app/screens/profile/profile_screen.dart';
import 'package:asset_maintenance_app/providers/auth_provider.dart';

final appRouter = GoRouter(
  initialLocation: '/login',
  errorBuilder: (context, state) => Scaffold(
    body: Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 48, color: Colors.red),
          const SizedBox(height: 16),
          const Text('صفحة غير موجودة'),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => context.go('/'),
            child: const Text('العودة للرئيسية'),
          ),
        ],
      ),
    ),
  ),
  refreshListenable: _RouterRefreshStream(),
  redirect: (context, state) async {
    final authState = ProviderScope.containerOf(context).read(authStateProvider);
    final isLoggingIn = state.matchedLocation == '/login';

    if (!authState.isAuthenticated && !isLoggingIn) {
      return '/login';
    }

    if (authState.isAuthenticated && isLoggingIn) {
      return '/';
    }

    return null;
  },
  routes: [
    GoRoute(
      path: '/login',
      name: 'login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/',
      name: 'home',
      builder: (context, state) => const HomeScreen(),
      routes: [
        GoRoute(
          path: 'assets',
          name: 'assets',
          builder: (context, state) => const AssetsScreen(),
          routes: [
            GoRoute(
              path: ':assetName',
              name: 'asset-detail',
              builder: (context, state) {
                final assetName = state.pathParameters['assetName']!;
                return AssetDetailScreen(assetName: assetName);
              },
            ),
          ],
        ),
        GoRoute(
          path: 'maintenance',
          name: 'maintenance',
          builder: (context, state) => const MaintenanceListScreen(),
          routes: [
            GoRoute(
              path: ':maintenanceName',
              name: 'maintenance-detail',
              builder: (context, state) {
                final maintenanceName = state.pathParameters['maintenanceName']!;
                return MaintenanceDetailScreen(maintenanceName: maintenanceName);
              },
            ),
            GoRoute(
              path: 'create',
              name: 'create-maintenance',
              builder: (context, state) => const CreateMaintenanceScreen(),
            ),
          ],
        ),
        GoRoute(
          path: 'profile',
          name: 'profile',
          builder: (context, state) => const ProfileScreen(),
        ),
      ],
    ),
  ],
);

class _RouterRefreshStream extends ChangeNotifier {
  _RouterRefreshStream();
}
