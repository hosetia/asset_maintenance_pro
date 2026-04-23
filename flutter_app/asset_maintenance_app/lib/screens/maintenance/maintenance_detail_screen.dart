import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:asset_maintenance_app/config/theme.dart';
import 'package:asset_maintenance_app/providers/maintenance_provider.dart';

class MaintenanceDetailScreen extends ConsumerWidget {
  final String maintenanceName;

  const MaintenanceDetailScreen({Key? key, required this.maintenanceName})
      : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final maintenanceAsync = ref.watch(maintenanceRequestDetailsProvider(maintenanceName));

    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل الصيانة'),
      ),
      body: maintenanceAsync.when(
        data: (maintenance) {
          return SingleChildScrollView(
            child: Column(
              children: [
                // Header
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
                          Icons.construction,
                          size: 40,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        maintenance.assetName,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              maintenance.status,
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                                fontSize: 12,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          if (maintenance.priority != null)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                maintenance.priority ?? '',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
                // Details
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      // Basic Info
                      _Section(
                        title: 'المعلومات الأساسية',
                        children: [
                          if (maintenance.maintenanceType != null)
                            _InfoRow(
                              label: 'نوع الصيانة',
                              value: maintenance.maintenanceType ?? '',
                            ),
                          _InfoRow(
                            label: 'حالة الطلب',
                            value: maintenance.status,
                          ),
                          if (maintenance.description != null)
                            _InfoRow(
                              label: 'الوصف',
                              value: maintenance.description ?? '',
                            ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Dates
                      _Section(
                        title: 'المواعيد',
                        children: [
                          _InfoRow(
                            label: 'تاريخ الإنشاء',
                            value: maintenance.createdDate
                                .toString()
                                .split(' ')[0],
                          ),
                          if (maintenance.dueDate != null)
                            _InfoRow(
                              label: 'موعد الاستحقاق',
                              value: maintenance.dueDate!
                                  .toString()
                                  .split(' ')[0],
                            ),
                          if (maintenance.completedDate != null)
                            _InfoRow(
                              label: 'تاريخ الإكمال',
                              value: maintenance.completedDate!
                                  .toString()
                                  .split(' ')[0],
                            ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      // Assignment
                      if (maintenance.assignedTo != null)
                        Column(
                          children: [
                            _Section(
                              title: 'التخصيص',
                              children: [
                                _InfoRow(
                                  label: 'مسؤول الصيانة',
                                  value: maintenance.assignedTo ?? 'غير محدد',
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                          ],
                        ),
                      // Progress
                      if (maintenance.completionProgress > 0)
                        Column(
                          children: [
                            _Section(
                              title: 'التقدم',
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      children: [
                                        const Text(
                                          'نسبة الإنجاز',
                                          style: TextStyle(
                                            color: AppTheme.gray,
                                            fontSize: 12,
                                          ),
                                        ),
                                        Text(
                                          '${maintenance.completionProgress}%',
                                          style: const TextStyle(
                                            color: AppTheme.primaryColor,
                                            fontWeight: FontWeight.w600,
                                            fontSize: 14,
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 8),
                                    ClipRRect(
                                      borderRadius:
                                          BorderRadius.circular(4),
                                      child:
                                          LinearProgressIndicator(
                                        value: maintenance
                                                .completionProgress /
                                            100,
                                        minHeight: 6,
                                        backgroundColor:
                                            AppTheme.lightGray,
                                        valueColor:
                                            const AlwaysStoppedAnimation<
                                                Color>(
                                          AppTheme.primaryColor,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                          ],
                        ),
                      // Cost
                      if (maintenance.estimatedCost != null)
                        Column(
                          children: [
                            _Section(
                              title: 'التكلفة',
                              children: [
                                _InfoRow(
                                  label: 'التكلفة المقدرة',
                                  value: 'ر.س ${maintenance.estimatedCost?.toStringAsFixed(2) ?? '0'}',
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                          ],
                        ),
                      // Notes
                      if (maintenance.notes != null &&
                          maintenance.notes!.isNotEmpty)
                        _Section(
                          title: 'ملاحظات',
                          children: [
                            Text(
                              maintenance.notes ?? '',
                              style: const TextStyle(
                                color: AppTheme.darkGray,
                                fontSize: 14,
                                height: 1.6,
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

class _Section extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _Section({required this.title, required this.children});

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

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: AppTheme.gray,
              fontSize: 12,
            ),
          ),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.end,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
                color: AppTheme.darkGray,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
