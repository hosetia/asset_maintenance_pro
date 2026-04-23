class Asset {
  final String name;
  final String assetName;
  final String assetCategory;
  final String? branch;
  final String? location;
  final String? description;
  final String? status;
  final DateTime? purchaseDate;
  final double? purchaseValue;
  final String? lastMaintenanceDate;
  final int? maintenanceIntervalDays;

  Asset({
    required this.name,
    required this.assetName,
    required this.assetCategory,
    this.branch,
    this.location,
    this.description,
    this.status,
    this.purchaseDate,
    this.purchaseValue,
    this.lastMaintenanceDate,
    this.maintenanceIntervalDays,
  });

  factory Asset.fromJson(Map<String, dynamic> json) {
    return Asset(
      name: json['name'] ?? '',
      assetName: json['asset_name'] ?? '',
      assetCategory: json['asset_category'] ?? '',
      branch: json['branch'],
      location: json['location'],
      description: json['description'],
      status: json['status'],
      purchaseDate: json['purchase_date'] != null
          ? DateTime.tryParse(json['purchase_date'])
          : null,
      purchaseValue: json['purchase_value'] != null
          ? double.tryParse(json['purchase_value'].toString())
          : null,
      lastMaintenanceDate: json['custom_last_maintenance_date'],
      maintenanceIntervalDays: json['custom_maintenance_interval_days'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'asset_name': assetName,
      'asset_category': assetCategory,
      'branch': branch,
      'location': location,
      'description': description,
      'status': status,
      'purchase_date': purchaseDate?.toIso8601String(),
      'purchase_value': purchaseValue,
    };
  }

  bool get needsMaintenance {
    if (lastMaintenanceDate == null || maintenanceIntervalDays == null) {
      return false;
    }
    final lastDate = DateTime.tryParse(lastMaintenanceDate ?? '');
    if (lastDate == null) return false;
    final daysElapsed = DateTime.now().difference(lastDate).inDays;
    return daysElapsed >= maintenanceIntervalDays!;
  }
}
