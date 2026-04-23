import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:asset_maintenance_app/config/theme.dart';
import 'package:asset_maintenance_app/config/router.dart';
import 'package:asset_maintenance_app/services/storage_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await StorageService.init();
  runApp(
    const ProviderScope(
      child: AssetMaintenanceApp(),
    ),
  );
}

class AssetMaintenanceApp extends StatelessWidget {
  const AssetMaintenanceApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Asset Maintenance Pro',
      theme: AppTheme.lightTheme,
      routerConfig: appRouter,
      debugShowCheckedModeBanner: false,
    );
  }
}
