# فتح المشروع في Android Studio

## الخطوات السريعة

### 1. افتح Android Studio

### 2. اختر "Open an Existing Project"
```
File → Open
```

### 3. انتقل إلى مجلد المشروع
```
/path/to/asset_maintenance_pro/flutter_app/asset_maintenance_app
```

### 4. انقر على "Open"

### 5. انتظر حتى يتم تحميل المشروع (قد يستغرق دقائق)

## تثبيت الـ Plugins (إذا لم تكن مثبتة)

1. افتح **Android Studio Preferences/Settings**
2. اذهب إلى **Plugins**
3. ابحث عن "Flutter" وانقر على **Install**
4. قم بتثبيت "Dart" أيضاً
5. أعد تشغيل Android Studio

## إذا لم يكن المشروع معترفاً به

جرب هذه الخطوات:

### الحل 1: تحديث Flutter
```bash
flutter upgrade
```

### الحل 2: إنشاء ملف local.properties
في مجلد `android/`، أنشئ ملف باسم `local.properties` بالمحتوى التالي:
```properties
sdk.dir=/path/to/android/sdk
flutter.sdk=/path/to/flutter/sdk
```

### الحل 3: تنظيف والبناء من جديد
```bash
cd flutter_app/asset_maintenance_app
flutter clean
flutter pub get
flutter run
```

### الحل 4: فتح مشروع Android فقط
إذا كنت تريد العمل على كود Android فقط:
1. اختر **Open an Existing Project**
2. انتقل إلى `flutter_app/asset_maintenance_app/android/`
3. انقر على **Open**

## التحقق من التثبيت

تشغيل أمر flutter doctor:
```bash
flutter doctor
```

يجب أن ترى علامات صح ✓ أمام:
- Android Studio
- Android SDK
- Flutter plugin for Android Studio
- Dart plugin

## تشغيل التطبيق

### من الـ Terminal في Android Studio
```bash
flutter run
```

### من سطر الأوامر
```bash
cd flutter_app/asset_maintenance_app
flutter run
```

## مشاكل شائعة

### "Flutter SDK not found"
- تأكد من أن Flutter مثبت بشكل صحيح
- استخدم `flutter --version` للتحقق
- أضف Flutter إلى PATH

### "Gradle build failed"
```bash
cd android
./gradlew clean
cd ..
flutter pub get
flutter run
```

### "Plugin not found: io.flutter.embedding:flutter_embedding"
```bash
flutter pub get
flutter clean
flutter pub get
```

## الميزات في Android Studio

- ✅ Code intellisense و autocomplete
- ✅ Real-time error checking
- ✅ Dart analyzer
- ✅ Flutter DevTools integration
- ✅ Widget preview
- ✅ Run/Debug on emulator or device

## نصائح الإنتاجية

### استخدام Hot Reload
أثناء تشغيل التطبيق، اضغط:
- `r` - Hot reload (إعادة تحميل سريعة)
- `R` - Hot restart (إعادة بدء)

### استخدام DevTools
```bash
flutter pub global activate devtools
devtools
```

### تتبع الأخطاء
استخدم Debug console في Android Studio لعرض logs

## معلومات إضافية

- [Flutter Documentation](https://flutter.dev/docs)
- [Android Studio for Flutter](https://flutter.dev/docs/development/tools/android-studio)
- [Hot Reload Guide](https://flutter.dev/docs/development/tools/hot-reload)
