class MaintenanceRequest {
  final String? name;
  final String asset;
  final String assetName;
  final String assetCategory;
  final String? maintenanceType;
  final String? description;
  final String status;
  final String? assignedTo;
  final String? branch;
  final DateTime createdDate;
  final DateTime? dueDate;
  final DateTime? completedDate;
  final String? priority;
  final double? estimatedCost;
  final int? completionProgress;
  final List<String>? attachments;
  final String? notes;

  MaintenanceRequest({
    this.name,
    required this.asset,
    required this.assetName,
    required this.assetCategory,
    this.maintenanceType,
    this.description,
    this.status = 'Draft',
    this.assignedTo,
    this.branch,
    required this.createdDate,
    this.dueDate,
    this.completedDate,
    this.priority,
    this.estimatedCost,
    this.completionProgress = 0,
    this.attachments,
    this.notes,
  });

  factory MaintenanceRequest.fromJson(Map<String, dynamic> json) {
    return MaintenanceRequest(
      name: json['name'],
      asset: json['asset'] ?? '',
      assetName: json['asset_name'] ?? '',
      assetCategory: json['asset_category'] ?? '',
      maintenanceType: json['maintenance_type'],
      description: json['description'],
      status: json['status'] ?? 'Draft',
      assignedTo: json['assigned_to'],
      branch: json['branch'],
      createdDate: json['creation'] != null
          ? DateTime.parse(json['creation'])
          : DateTime.now(),
      dueDate: json['due_date'] != null ? DateTime.parse(json['due_date']) : null,
      completedDate: json['completed_date'] != null
          ? DateTime.parse(json['completed_date'])
          : null,
      priority: json['priority'],
      estimatedCost: json['estimated_cost'] != null
          ? double.tryParse(json['estimated_cost'].toString())
          : null,
      completionProgress: json['completion_progress'] ?? 0,
      attachments: json['attachments'] != null
          ? List<String>.from(json['attachments'])
          : null,
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'asset': asset,
      'asset_name': assetName,
      'asset_category': assetCategory,
      'maintenance_type': maintenanceType,
      'description': description,
      'status': status,
      'assigned_to': assignedTo,
      'branch': branch,
      'due_date': dueDate?.toIso8601String(),
      'priority': priority,
      'estimated_cost': estimatedCost,
      'notes': notes,
    };
  }

  bool get isActive => status == 'Open' || status == 'In Progress';
  bool get isCompleted => status == 'Completed';
  bool get isOverdue => dueDate != null && dueDate!.isBefore(DateTime.now()) && isActive;

  MaintenanceRequest copyWith({
    String? name,
    String? asset,
    String? assetName,
    String? assetCategory,
    String? maintenanceType,
    String? description,
    String? status,
    String? assignedTo,
    String? branch,
    DateTime? createdDate,
    DateTime? dueDate,
    DateTime? completedDate,
    String? priority,
    double? estimatedCost,
    int? completionProgress,
    List<String>? attachments,
    String? notes,
  }) {
    return MaintenanceRequest(
      name: name ?? this.name,
      asset: asset ?? this.asset,
      assetName: assetName ?? this.assetName,
      assetCategory: assetCategory ?? this.assetCategory,
      maintenanceType: maintenanceType ?? this.maintenanceType,
      description: description ?? this.description,
      status: status ?? this.status,
      assignedTo: assignedTo ?? this.assignedTo,
      branch: branch ?? this.branch,
      createdDate: createdDate ?? this.createdDate,
      dueDate: dueDate ?? this.dueDate,
      completedDate: completedDate ?? this.completedDate,
      priority: priority ?? this.priority,
      estimatedCost: estimatedCost ?? this.estimatedCost,
      completionProgress: completionProgress ?? this.completionProgress,
      attachments: attachments ?? this.attachments,
      notes: notes ?? this.notes,
    );
  }
}
