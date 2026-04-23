# Asset Maintenance Pro - Mobile App

تطبيق موبايل احترافي لإدارة صيانة الأصول والمعدات، مبني بـ Flutter.

## المميزات الرئيسية

✅ **تسجيل الدخول والمصادقة**
- نظام دخول آمن مع إمكانية تذكر المستخدم
- دعم كامل للعربية

✅ **إدارة الأصول**
- عرض قائمة جميع الأصول
- تفاصيل شاملة لكل أصل
- البحث والتصفية

✅ **طلبات الصيانة**
- إنشاء طلبات صيانة جديدة
- متابعة حالة الطلبات
- عرض تاريخ الطلبات المنجزة

✅ **إدارة الصور**
- التقاط صور للأعطال مباشرة من الكاميرا
- اختيار صور من المعرض
- تحميل الصور مع الطلبات

✅ **الإشعارات**
- إشعارات فورية لحالة الطلبات
- تذكيرات الصيانة الدورية

✅ **الملف الشخصي**
- عرض معلومات المستخدم
- إعدادات التطبيق
- إدارة الجلسة

## المتطلبات

- Flutter 3.10.0 أو أحدث
- Dart 3.0.0 أو أحدث
- Android SDK 21+
- iOS 11.0+

## التثبيت

### 1. استنساخ المشروع

```bash
cd flutter_app/asset_maintenance_app
```

### 2. تثبيت المكتبات

```bash
flutter pub get
```

### 3. توليد الملفات (إذا لزم الأمر)

```bash
flutter pub run build_runner build
```

## التشغيل

### تشغيل التطبيق في development mode

```bash
flutter run
```

### بناء APK

```bash
flutter build apk --release
```

### بناء iOS

```bash
flutter build ios --release
```

## البنية المعمارية

```
lib/
├── config/          # الإعدادات والـ Theme والـ Router
├── models/          # نماذج البيانات
├── providers/       # State Management (Riverpod)
├── screens/         # واجهات المستخدم
│   ├── auth/
│   ├── home/
│   ├── assets/
│   ├── maintenance/
│   └── profile/
├── services/        # خدمات API والتخزين
├── widgets/         # مكونات قابلة لإعادة الاستخدام
├── utils/           # دوال مساعدة
└── main.dart        # نقطة دخول التطبيق
```

## الحالات المدعومة

### حالات الأصول
- Active (نشط)
- Inactive (غير نشط)

### حالات طلبات الصيانة
- Draft (مسودة)
- Open (مفتوح)
- In Progress (قيد الإنجاز)
- Completed (منجز)

### الأولويات
- Low (منخفضة)
- Medium (متوسطة)
- High (عالية)

### أنواع الصيانة
- Preventive (وقائية)
- Corrective (تصحيحية)
- Emergency (طوارئ)

## API Integration

يتصل التطبيق بـ Backend من خلال:
- REST API endpoints
- JSON request/response
- Bearer token authentication

### مثال على الاتصال

```dart
final apiService = ApiService();

// تسجيل الدخول
final user = await apiService.login(username, password);

// جلب الأصول
final assets = await apiService.getAssets(branch: 'Branch A');

// إنشاء طلب صيانة
final request = await apiService.createMaintenanceRequest(maintenanceRequest);
```

## حالة التطوير

هذا التطبيق في مرحلة التطوير الأولى. المميزات التالية قيد التطوير:

- [ ] دعم Offline Mode
- [ ] تحسين الأداء
- [ ] المزيد من التقارير
- [ ] تكامل Firebase للإشعارات
- [ ] دعم المزيد من اللغات

## المساهمة

نرحب بالمساهمات! يرجى إتباع الخطوات التالية:

1. انسخ الـ repository
2. أنشئ فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. قم بـ commit التغييرات (`git commit -m 'Add AmazingFeature'`)
4. ادفع إلى الفرع (`git push origin feature/AmazingFeature`)
5. افتح Pull Request

## الترخيص

هذا المشروع مرخص تحت MIT License - انظر ملف LICENSE للتفاصيل.

## الدعم

للمشاكل والأسئلة، يرجى فتح Issue جديدة في المستودع.

## المؤلفون

تم تطويره بواسطة فريق Asset Maintenance Pro

## تعديلات مستقبلية

- تحسين الواجهة الرسومية
- إضافة المزيد من الميزات المتقدمة
- تحسين الأداء والاستقرار
