import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:asset_maintenance_app/config/theme.dart';
import 'package:asset_maintenance_app/providers/asset_provider.dart';

class AssetDetailScreen extends ConsumerWidget {
  final String assetName;

  const AssetDetailScreen({Key? key, required this.assetName}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final assetAsync = ref.watch(assetDetailsProvider(assetName));

    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل الأصل'),
      ),
      body: assetAsync.when(
        data: (asset) {
          return SingleChildScrollView(
            child: Column(
              children: [
                // Asset Header
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      colors: [AppTheme.primaryColor, Color(0xFF1e40af)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 64,
                        height: 64,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.build_circle,
                          size: 40,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        asset.assetName,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        asset.assetCategory,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                // Details Sections
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      // Status
                      _DetailSection(
                        title: 'الحالة',
                        children: [
                          _DetailItem(
                            label: 'الحالة الحالية',
                            value: asset.status ?? 'نشط',
                            icon: Icons.info_outline,
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Location Info
                      if (asset.location != null)
                        Column(
                          children: [
                            _DetailSection(
                              title: 'الموقع',
                              children: [
                                _DetailItem(
                                  label: 'الموقع',
                                  value: asset.location ?? 'غير محدد',
                                  icon: Icons.location_on,
                                ),
                                if (asset.branch != null)
                                  _DetailItem(
                                    label: 'الفرع',
                                    value: asset.branch ?? 'غير محدد',
                                    icon: Icons.business,
                                  ),
                              ],
                            ),
                            const SizedBox(height: 16),
                          ],
                        ),
                      // Maintenance Info
                      _DetailSection(
                        title: 'معلومات الصيانة',
                        children: [
                          if (asset.lastMaintenanceDate != null)
                            _DetailItem(
                              label: 'آخر صيانة',
                              value: asset.lastMaintenanceDate ?? 'لم تجرَ صيانة بعد',
                              icon: Icons.calendar_today,
                            ),
                          if (asset.maintenanceIntervalDays != null)
                            _DetailItem(
                              label: 'فترة الصيانة',
                              value: '${asset.maintenanceIntervalDays} أيام',
                              icon: Icons.schedule,
                            ),
                          if (asset.needsMaintenance)
                            Container(
                              margin: const EdgeInsets.only(top: 12),
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 8),
                              decoration: BoxDecoration(
                                color: AppTheme.errorColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                  color: AppTheme.errorColor.withOpacity(0.3),
                                ),
                              ),
                              child: Row(
                                children: [
                                  const Icon(
                                    Icons.warning_amber,
                                    color: AppTheme.errorColor,
                                    size: 18,
                                  ),
                                  const SizedBox(width: 8),
                                  const Expanded(
                                    child: Text(
                                      'هذا الأصل يحتاج إلى صيانة فورية',
                                      style: TextStyle(
                                        color: AppTheme.errorColor,
                                        fontWeight: FontWeight.w600,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Purchase Info
                      if (asset.purchaseDate != null)
                        Column(
                          children: [
                            _DetailSection(
                              title: 'معلومات الشراء',
                              children: [
                                _DetailItem(
                                  label: 'تاريخ الشراء',
                                  value: asset.purchaseDate.toString().split(' ')[0],
                                  icon: Icons.shopping_cart,
                                ),
                                if (asset.purchaseValue != null)
                                  _DetailItem(
                                    label: 'قيمة الشراء',
                                    value: 'ر.س ${asset.purchaseValue?.toStringAsFixed(2)}',
                                    icon: Icons.attach_money,
                                  ),
                              ],
                            ),
                            const SizedBox(height: 16),
                          ],
                        ),
                      // Action Buttons
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              icon: const Icon(Icons.add_circle),
                              label: const Text('فتح طلب صيانة'),
                              onPressed: () =>
                                  context.pushNamed('create-maintenance'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(child: Text('خطأ: $err')),
      ),
    );
  }
}

class _DetailSection extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _DetailSection({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.lightGray),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              fontSize: 14,
              color: AppTheme.darkGray,
            ),
          ),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    );
  }
}

class _DetailItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _DetailItem({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppTheme.primaryColor),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppTheme.gray,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                    color: AppTheme.darkGray,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
