import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:asset_maintenance_app/models/asset_model.dart';
import 'package:asset_maintenance_app/services/api_service.dart';

final assetsProvider = FutureProvider.family<List<Asset>, Map<String, String?>>((ref, params) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getAssets(
    branch: params['branch'],
    status: params['status'],
  );
});

final assetDetailsProvider = FutureProvider.family<Asset, String>((ref, assetName) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getAssetDetails(assetName);
});

final apiServiceProvider = Provider((ref) => ApiService());

final assetSearchProvider = StateProvider<String>((ref) => '');
final assetFilterProvider = StateProvider<String?>((ref) => null);

final filteredAssetsProvider = FutureProvider<List<Asset>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final query = ref.watch(assetSearchProvider);
  final filter = ref.watch(assetFilterProvider);

  final assets = await apiService.getAssets(status: filter);

  if (query.isEmpty) {
    return assets;
  }

  return assets
      .where((asset) =>
          asset.assetName.toLowerCase().contains(query.toLowerCase()) ||
          asset.assetCategory.toLowerCase().contains(query.toLowerCase()))
      .toList();
});
