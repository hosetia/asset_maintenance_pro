class AppConstants {
  // API
  static const String apiBaseUrl = 'http://localhost:8000/api';
  static const Duration apiTimeout = Duration(seconds: 15);

  // Storage Keys
  static const String userKey = 'user';
  static const String tokenKey = 'auth_token';
  static const String rememberMeKey = 'remember_me';
  static const String lastUsernameKey = 'last_username';

  // App Info
  static const String appName = 'Asset Maintenance Pro';
  static const String appVersion = '1.0.0';

  // Pagination
  static const int defaultPageSize = 50;

  // Maintenance Status
  static const String statusDraft = 'Draft';
  static const String statusOpen = 'Open';
  static const String statusInProgress = 'In Progress';
  static const String statusCompleted = 'Completed';

  // Maintenance Types
  static const String typePrevention = 'Preventive';
  static const String typeCorrection = 'Corrective';
  static const String typeEmergency = 'Emergency';

  // Priorities
  static const String priorityLow = 'Low';
  static const String priorityMedium = 'Medium';
  static const String priorityHigh = 'High';

  // Asset Status
  static const String assetActive = 'Active';
  static const String assetInactive = 'Inactive';
}

class AppStrings {
  // Common
  static const String app = 'Asset Maintenance Pro';
  static const String loading = 'جاري التحميل...';
  static const String error = 'خطأ';
  static const String success = 'نجح';
  static const String cancel = 'إلغاء';
  static const String submit = 'إرسال';
  static const String save = 'حفظ';
  static const String delete = 'حذف';
  static const String edit = 'تعديل';
  static const String back = 'رجوع';
  static const String close = 'إغلاق';

  // Auth
  static const String login = 'تسجيل الدخول';
  static const String logout = 'تسجيل الخروج';
  static const String username = 'اسم المستخدم';
  static const String password = 'كلمة المرور';
  static const String rememberMe = 'تذكرني';
  static const String loginFailed = 'فشل تسجيل الدخول';

  // Assets
  static const String assets = 'الأصول';
  static const String assetDetails = 'تفاصيل الأصل';
  static const String noAssets = 'لا توجد أصول';
  static const String searchAssets = 'ابحث عن أصل...';

  // Maintenance
  static const String maintenance = 'الصيانة';
  static const String createMaintenance = 'إنشاء طلب صيانة';
  static const String maintenanceRequests = 'طلبات الصيانة';
  static const String noMaintenanceRequests = 'لا توجد طلبات صيانة';
  static const String searchMaintenance = 'ابحث عن طلب...';
  static const String maintenanceStatus = 'حالة الصيانة';
  static const String maintenanceType = 'نوع الصيانة';
  static const String priority = 'الأولوية';
  static const String dueDate = 'موعد الاستحقاق';
  static const String description = 'الوصف';
  static const String notes = 'ملاحظات';

  // Profile
  static const String profile = 'الملف الشخصي';
  static const String accountInfo = 'معلومات الحساب';
  static const String email = 'البريد الإلكتروني';
  static const String fullName = 'الاسم الكامل';
  static const String role = 'الدور';
  static const String branch = 'الفرع';
  static const String settings = 'الإعدادات';
  static const String notifications = 'الإشعارات';
  static const String language = 'اللغة';
  static const String changePassword = 'تغيير كلمة المرور';

  // Status
  static const String active = 'نشط';
  static const String inactive = 'غير نشط';
  static const String pending = 'قيد الانتظار';
  static const String completed = 'منجز';
  static const String inProgress = 'قيد الإنجاز';
  static const String overdue = 'متأخر عن الموعد';
  static const String needsMaintenance = 'يحتاج إلى صيانة';

  // Messages
  static const String confirmLogout = 'هل أنت متأكد من أنك تريد تسجيل الخروج؟';
  static const String emptyFields = 'يرجى ملء جميع الحقول المطلوبة';
  static const String operationSuccess = 'تمت العملية بنجاح';
  static const String operationFailed = 'فشلت العملية';
}
