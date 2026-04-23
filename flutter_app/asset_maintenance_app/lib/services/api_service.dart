import 'package:dio/dio.dart';
import 'package:asset_maintenance_app/models/user_model.dart';
import 'package:asset_maintenance_app/models/asset_model.dart';
import 'package:asset_maintenance_app/models/maintenance_request_model.dart';
import 'package:logger/logger.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  late final Dio _dio;
  final logger = Logger();
  String? _authToken;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      contentType: Headers.jsonContentType,
    ));

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: _onRequest,
        onError: _onError,
      ),
    );
  }

  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (_authToken != null) {
      options.headers['Authorization'] = 'Bearer $_authToken';
    }
    logger.d('REQUEST: ${options.method} ${options.path}');
    handler.next(options);
  }

  Future<void> _onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    logger.e('ERROR: ${err.message}');
    handler.next(err);
  }

  // ════════════════════════════════════════
  // Authentication
  // ════════════════════════════════════════

  Future<User> login(String username, String password) async {
    try {
      final response = await _dio.post(
        '/auth/login',
        data: {
          'username': username,
          'password': password,
        },
      );
      final user = User.fromJson(response.data);
      _authToken = user.token;
      return user;
    } on DioException catch (e) {
      logger.e('Login failed: ${e.response?.statusCode}');
      throw ApiException(e.response?.statusCode ?? 500, e.message ?? 'Login failed');
    }
  }

  void setAuthToken(String token) {
    _authToken = token;
  }

  // ════════════════════════════════════════
  // User Operations
  // ════════════════════════════════════════

  Future<Map<String, dynamic>> getUserBranch() async {
    try {
      final response = await _dio.get('/resource/User/get-user-branch');
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw ApiException(e.response?.statusCode ?? 500, 'Failed to get user branch');
    }
  }

  // ════════════════════════════════════════
  // Asset Operations
  // ════════════════════════════════════════

  Future<List<Asset>> getAssets({
    String? branch,
    String? status,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final filters = [];
      if (branch != null) filters.add(['branch', '=', branch]);
      if (status != null) filters.add(['status', '=', status]);

      final response = await _dio.get(
        '/resource/Asset',
        queryParameters: {
          'fields': '["name","asset_name","asset_category","branch","location","status"]',
          'filters': filters.isNotEmpty ? jsonEncodeFilters(filters) : null,
          'limit_page_length': limit,
          'limit_page_length_offset': offset,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final assets = (data['data'] as List)
          .map((item) => Asset.fromJson(item as Map<String, dynamic>))
          .toList();
      return assets;
    } on DioException catch (e) {
      throw ApiException(e.response?.statusCode ?? 500, 'Failed to fetch assets');
    }
  }

  Future<Asset> getAssetDetails(String assetName) async {
    try {
      final response = await _dio.get('/resource/Asset/$assetName');
      final data = response.data as Map<String, dynamic>;
      return Asset.fromJson(data['data']);
    } on DioException catch (e) {
      throw ApiException(e.response?.statusCode ?? 500, 'Failed to get asset details');
    }
  }

  // ════════════════════════════════════════
  // Maintenance Request Operations
  // ════════════════════════════════════════

  Future<List<MaintenanceRequest>> getMaintenanceRequests({
    String? status,
    String? assignedTo,
    String? branch,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final filters = [];
      if (status != null) filters.add(['status', '=', status]);
      if (assignedTo != null) filters.add(['assigned_to', '=', assignedTo]);
      if (branch != null) filters.add(['branch', '=', branch]);

      final response = await _dio.get(
        '/resource/Maintenance Request',
        queryParameters: {
          'fields':
              '["name","asset","asset_name","asset_category","status","assigned_to","creation","due_date","priority","completion_progress"]',
          'filters': filters.isNotEmpty ? jsonEncodeFilters(filters) : null,
          'limit_page_length': limit,
          'limit_page_length_offset': offset,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final requests = (data['data'] as List)
          .map((item) => MaintenanceRequest.fromJson(item as Map<String, dynamic>))
          .toList();
      return requests;
    } on DioException catch (e) {
      throw ApiException(e.response?.statusCode ?? 500, 'Failed to fetch maintenance requests');
    }
  }

  Future<MaintenanceRequest> getMaintenanceRequestDetails(String name) async {
    try {
      final response = await _dio.get('/resource/Maintenance Request/$name');
      final data = response.data as Map<String, dynamic>;
      return MaintenanceRequest.fromJson(data['data']);
    } on DioException catch (e) {
      throw ApiException(e.response?.statusCode ?? 500, 'Failed to get maintenance request details');
    }
  }

  Future<MaintenanceRequest> createMaintenanceRequest(
    MaintenanceRequest request,
  ) async {
    try {
      final response = await _dio.post(
        '/resource/Maintenance Request',
        data: request.toJson(),
      );
      final data = response.data as Map<String, dynamic>;
      return MaintenanceRequest.fromJson(data['data']);
    } on DioException catch (e) {
      throw ApiException(e.response?.statusCode ?? 500, 'Failed to create maintenance request');
    }
  }

  Future<MaintenanceRequest> updateMaintenanceRequest(
    String name,
    MaintenanceRequest request,
  ) async {
    try {
      final response = await _dio.put(
        '/resource/Maintenance Request/$name',
        data: request.toJson(),
      );
      final data = response.data as Map<String, dynamic>;
      return MaintenanceRequest.fromJson(data['data']);
    } on DioException catch (e) {
      throw ApiException(e.response?.statusCode ?? 500, 'Failed to update maintenance request');
    }
  }

  // ════════════════════════════════════════
  // File Upload
  // ════════════════════════════════════════

  Future<String> uploadFile(String filePath, String fileName) async {
    try {
      final file = await MultipartFile.fromFile(filePath, filename: fileName);
      final formData = FormData.fromMap({
        'file': file,
        'doctype': 'Maintenance Request',
      });

      final response = await _dio.post(
        '/upload-file',
        data: formData,
      );
      final data = response.data as Map<String, dynamic>;
      return data['file_url'] ?? '';
    } on DioException catch (e) {
      throw ApiException(e.response?.statusCode ?? 500, 'Failed to upload file');
    }
  }

  // ════════════════════════════════════════
  // Utilities
  // ════════════════════════════════════════

  String jsonEncodeFilters(List<List<dynamic>> filters) {
    return jsonEncode(filters);
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException($statusCode): $message';
}

import 'dart:convert';

final apiService = ApiService();
