# 🚀 دليل البدء السريع

## الخطوة 1: افتح المشروع في Android Studio

```bash
# الطريقة 1: من Android Studio
File → Open → اختر المجلد:
/path/to/asset_maintenance_pro/flutter_app/asset_maintenance_app

# الطريقة 2: من Terminal
cd /path/to/asset_maintenance_pro/flutter_app/asset_maintenance_app
code .
```

## الخطوة 2: تثبيت المكتبات

```bash
flutter pub get
```

## الخطوة 3: تشغيل التطبيق

```bash
flutter run
```

## ✅ المشروع يجب أن يعمل الآن!

### إذا حدثت مشاكل:

#### المشكلة: "Flutter not found"
```bash
# تأكد من تثبيت Flutter
flutter --version

# أضفه إلى PATH إذا لم يكن موجوداً
```

#### المشكلة: "Android SDK not found"
```bash
# في Android Studio: Tools → SDK Manager
# تأكد من تثبيت Android SDK 21+
```

#### المشكلة: "Gradle build failed"
```bash
flutter clean
flutter pub get
flutter run
```

#### المشكلة: "No connected devices"
```bash
# تشغيل Android Emulator
# أو وصل جهاز حقيقي
```

## 📁 هيكل المشروع

```
flutter_app/asset_maintenance_app/
├── android/           ← كود Android (Gradle)
├── ios/               ← ملفات iOS
├── web/               ← ملفات Web
├── windows/           ← ملفات Windows
├── lib/               ← كود Dart الرئيسي
├── pubspec.yaml       ← المكتبات والإعدادات
└── README.md          ← التوثيق
```

## 🔧 الأوامر الأساسية

```bash
# تحديث Flutter
flutter upgrade

# فحص التثبيت
flutter doctor

# تشغيل الاختبارات
flutter test

# بناء APK
flutter build apk --release

# بناء iOS
flutter build ios --release

# تنظيف المشروع
flutter clean
```

## 🎯 المراحل القادمة

1. ✅ التطبيق يعمل بشكل أساسي
2. [ ] إضافة الشاشات المتقدمة
3. [ ] اتصال API كامل
4. [ ] الإشعارات
5. [ ] الصور والملفات

## 📞 الدعم

للمشاكل:
1. تشغيل `flutter doctor`
2. البحث عن الحل في [Flutter Docs](https://flutter.dev/docs)
3. فتح Issue في المستودع

---

**تم إنشاء المشروع بنجاح! استمتع بالتطوير! 🎉**
