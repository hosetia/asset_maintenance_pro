import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:asset_maintenance_app/config/theme.dart';
import 'package:asset_maintenance_app/providers/asset_provider.dart';

class AssetsScreen extends ConsumerStatefulWidget {
  const AssetsScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<AssetsScreen> createState() => _AssetsScreenState();
}

class _AssetsScreenState extends ConsumerState<AssetsScreen> {
  late TextEditingController _searchController;
  String? _selectedStatus;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filteredAssets = ref.watch(filteredAssetsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('الأصول'),
      ),
      body: Column(
        children: [
          // Search and Filter
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                TextField(
                  controller: _searchController,
                  textDirection: TextDirection.rtl,
                  decoration: InputDecoration(
                    hintText: 'ابحث عن أصل...',
                    hintTextDirection: TextDirection.rtl,
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _searchController.clear();
                              ref.read(assetSearchProvider.notifier).state = '';
                            },
                          )
                        : null,
                  ),
                  onChanged: (value) {
                    ref.read(assetSearchProvider.notifier).state = value;
                  },
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: Wrap(
                        spacing: 8,
                        children: [
                          FilterChip(
                            label: const Text('الكل'),
                            selected: _selectedStatus == null,
                            onSelected: (selected) {
                              setState(() => _selectedStatus = null);
                              ref.read(assetFilterProvider.notifier).state = null;
                            },
                          ),
                          FilterChip(
                            label: const Text('نشط'),
                            selected: _selectedStatus == 'Active',
                            onSelected: (selected) {
                              setState(() => _selectedStatus = 'Active');
                              ref.read(assetFilterProvider.notifier).state = 'Active';
                            },
                          ),
                          FilterChip(
                            label: const Text('غير نشط'),
                            selected: _selectedStatus == 'Inactive',
                            onSelected: (selected) {
                              setState(() => _selectedStatus = 'Inactive');
                              ref.read(assetFilterProvider.notifier).state = 'Inactive';
                            },
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Assets List
          Expanded(
            child: filteredAssets.when(
              data: (assets) {
                if (assets.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.inbox,
                          size: 64,
                          color: Colors.grey[300],
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'لا توجد أصول',
                          style: TextStyle(color: AppTheme.gray, fontSize: 16),
                        ),
                      ],
                    ),
                  );
                }
                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: assets.length,
                  itemBuilder: (context, index) {
                    final asset = assets[index];
                    return _AssetCard(
                      asset: asset,
                      onTap: () {
                        context.pushNamed(
                          'asset-detail',
                          pathParameters: {'assetName': asset.name},
                        );
                      },
                    );
                  },
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('خطأ: $err')),
            ),
          ),
        ],
      ),
    );
  }
}

class _AssetCard extends StatelessWidget {
  final dynamic asset;
  final VoidCallback onTap;

  const _AssetCard({required this.asset, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.lightGray),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        asset.assetName,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                          color: AppTheme.darkGray,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        asset.assetCategory,
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppTheme.gray,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: asset.status == 'Active'
                        ? AppTheme.successColor.withOpacity(0.1)
                        : Colors.grey[200],
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    asset.status ?? 'نشط',
                    style: TextStyle(
                      fontSize: 12,
                      color: asset.status == 'Active'
                          ? AppTheme.successColor
                          : AppTheme.gray,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (asset.location != null)
              Row(
                children: [
                  const Icon(Icons.location_on, size: 16, color: AppTheme.gray),
                  const SizedBox(width: 6),
                  Text(
                    asset.location,
                    style: const TextStyle(fontSize: 12, color: AppTheme.gray),
                  ),
                ],
              ),
            if (asset.needsMaintenance)
              Column(
                children: [
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppTheme.errorColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.warning_amber,
                          size: 14,
                          color: AppTheme.errorColor,
                        ),
                        const SizedBox(width: 4),
                        const Text(
                          'يحتاج إلى صيانة',
                          style: TextStyle(
                            fontSize: 11,
                            color: AppTheme.errorColor,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
