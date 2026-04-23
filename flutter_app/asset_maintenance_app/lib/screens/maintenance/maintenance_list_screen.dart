import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:asset_maintenance_app/config/theme.dart';
import 'package:asset_maintenance_app/providers/maintenance_provider.dart';

class MaintenanceListScreen extends ConsumerStatefulWidget {
  const MaintenanceListScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<MaintenanceListScreen> createState() =>
      _MaintenanceListScreenState();
}

class _MaintenanceListScreenState extends ConsumerState<MaintenanceListScreen> {
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
    final filteredMaintenance = ref.watch(filteredMaintenanceProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('طلبات الصيانة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle),
            onPressed: () => context.pushNamed('create-maintenance'),
          ),
        ],
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
                    hintText: 'ابحث عن طلب...',
                    hintTextDirection: TextDirection.rtl,
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _searchController.clear();
                              ref.read(maintenanceSearchProvider.notifier)
                                  .state = '';
                            },
                          )
                        : null,
                  ),
                  onChanged: (value) {
                    ref.read(maintenanceSearchProvider.notifier).state = value;
                  },
                ),
                const SizedBox(height: 12),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      FilterChip(
                        label: const Text('الكل'),
                        selected: _selectedStatus == null,
                        onSelected: (selected) {
                          setState(() => _selectedStatus = null);
                          ref
                              .read(maintenanceStatusFilterProvider.notifier)
                              .state = null;
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('مفتوح'),
                        selected: _selectedStatus == 'Open',
                        onSelected: (selected) {
                          setState(() => _selectedStatus = 'Open');
                          ref
                              .read(maintenanceStatusFilterProvider.notifier)
                              .state = 'Open';
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('قيد الإنجاز'),
                        selected: _selectedStatus == 'In Progress',
                        onSelected: (selected) {
                          setState(() => _selectedStatus = 'In Progress');
                          ref
                              .read(maintenanceStatusFilterProvider.notifier)
                              .state = 'In Progress';
                        },
                      ),
                      const SizedBox(width: 8),
                      FilterChip(
                        label: const Text('منجز'),
                        selected: _selectedStatus == 'Completed',
                        onSelected: (selected) {
                          setState(() => _selectedStatus = 'Completed');
                          ref
                              .read(maintenanceStatusFilterProvider.notifier)
                              .state = 'Completed';
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Maintenance List
          Expanded(
            child: filteredMaintenance.when(
              data: (requests) {
                if (requests.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.assignment_turned_in,
                          size: 64,
                          color: Colors.grey[300],
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'لا توجد طلبات صيانة',
                          style: TextStyle(
                              color: AppTheme.gray, fontSize: 16),
                        ),
                      ],
                    ),
                  );
                }
                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: requests.length,
                  itemBuilder: (context, index) {
                    final request = requests[index];
                    return _MaintenanceCard(
                      request: request,
                      onTap: () {
                        context.pushNamed(
                          'maintenance-detail',
                          pathParameters: {
                            'maintenanceName': request.name ?? ''
                          },
                        );
                      },
                    );
                  },
                );
              },
              loading: () =>
                  const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('خطأ: $err')),
            ),
          ),
        ],
      ),
    );
  }
}

class _MaintenanceCard extends StatelessWidget {
  final dynamic request;
  final VoidCallback onTap;

  const _MaintenanceCard({required this.request, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isOverdue = request.isOverdue;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isOverdue ? AppTheme.errorColor.withOpacity(0.3) : AppTheme.lightGray,
            width: isOverdue ? 2 : 1,
          ),
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
                        request.assetName,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                          color: AppTheme.darkGray,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        request.status,
                        style: TextStyle(
                          fontSize: 12,
                          color: _getStatusColor(request.status),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getPriorityColor(request.priority)
                        .withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    request.priority ?? 'عادي',
                    style: TextStyle(
                      fontSize: 11,
                      color: _getPriorityColor(request.priority),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (request.completionProgress > 0)
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'التقدم',
                              style:
                                  TextStyle(fontSize: 12, color: AppTheme.gray),
                            ),
                            Text(
                              '${request.completionProgress}%',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: AppTheme.primaryColor,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: request.completionProgress / 100,
                            minHeight: 4,
                            backgroundColor: AppTheme.lightGray,
                            valueColor: const AlwaysStoppedAnimation<Color>(
                              AppTheme.primaryColor,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                if (request.dueDate != null)
                  Padding(
                    padding: const EdgeInsets.only(right: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        const Icon(Icons.calendar_today,
                            size: 16, color: AppTheme.gray),
                        const SizedBox(height: 4),
                        Text(
                          request.dueDate
                              .toString()
                              .split(' ')[0],
                          style: const TextStyle(
                            fontSize: 11,
                            color: AppTheme.gray,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
            if (isOverdue)
              Column(
                children: [
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 8, vertical: 6),
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
                          'متأخر عن الموعد',
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

  Color _getStatusColor(String? status) {
    switch (status) {
      case 'Completed':
        return AppTheme.successColor;
      case 'In Progress':
        return AppTheme.accentColor;
      case 'Open':
        return AppTheme.primaryColor;
      default:
        return AppTheme.gray;
    }
  }

  Color _getPriorityColor(String? priority) {
    switch (priority) {
      case 'High':
        return AppTheme.errorColor;
      case 'Medium':
        return AppTheme.accentColor;
      case 'Low':
        return AppTheme.successColor;
      default:
        return AppTheme.gray;
    }
  }
}
