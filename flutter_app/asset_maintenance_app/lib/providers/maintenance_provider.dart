import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:asset_maintenance_app/models/maintenance_request_model.dart';
import 'package:asset_maintenance_app/services/api_service.dart';

final maintenanceRequestsProvider =
    FutureProvider.family<List<MaintenanceRequest>, Map<String, String?>>((ref, params) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getMaintenanceRequests(
    status: params['status'],
    assignedTo: params['assignedTo'],
    branch: params['branch'],
  );
});

final maintenanceRequestDetailsProvider =
    FutureProvider.family<MaintenanceRequest, String>((ref, name) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getMaintenanceRequestDetails(name);
});

final apiServiceProvider = Provider((ref) => ApiService());

final maintenanceStatusFilterProvider = StateProvider<String?>((ref) => null);
final maintenanceSearchProvider = StateProvider<String>((ref) => '');

final filteredMaintenanceProvider = FutureProvider<List<MaintenanceRequest>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final query = ref.watch(maintenanceSearchProvider);
  final statusFilter = ref.watch(maintenanceStatusFilterProvider);

  final requests = await apiService.getMaintenanceRequests(status: statusFilter);

  if (query.isEmpty) {
    return requests;
  }

  return requests
      .where((request) =>
          request.assetName.toLowerCase().contains(query.toLowerCase()) ||
          request.asset.toLowerCase().contains(query.toLowerCase()))
      .toList();
});

final createMaintenanceRequestProvider =
    FutureProvider.family<MaintenanceRequest, MaintenanceRequest>((ref, request) async {
  final apiService = ref.watch(apiServiceProvider);
  final createdRequest = await apiService.createMaintenanceRequest(request);

  // Invalidate the list to refresh
  ref.invalidate(maintenanceRequestsProvider);

  return createdRequest;
});

final updateMaintenanceRequestProvider =
    FutureProvider.family<MaintenanceRequest, (String, MaintenanceRequest)>((ref, params) async {
  final apiService = ref.watch(apiServiceProvider);
  final name = params.$1;
  final request = params.$2;

  final updatedRequest = await apiService.updateMaintenanceRequest(name, request);

  // Invalidate the list to refresh
  ref.invalidate(maintenanceRequestsProvider);

  return updatedRequest;
});
