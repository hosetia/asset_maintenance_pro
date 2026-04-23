# دليل الإعداد - تطبيق Flutter

## المتطلبات الأساسية

### 1. تثبيت Flutter

#### على Windows
```bash
# تحميل Flutter SDK
git clone https://github.com/flutter/flutter.git -b stable

# إضافة Flutter إلى PATH
# قم بإضافة مسار Flutter/bin إلى متغير PATH البيئي
```

#### على macOS و Linux
```bash
# تحميل Flutter SDK
git clone https://github.com/flutter/flutter.git -b stable

# إضافة Flutter إلى PATH
export PATH="$PATH:`pwd`/flutter/bin"
```

### 2. تثبيت Android Studio و iOS Development Tools

#### Android
- تحميل Android Studio من https://developer.android.com/studio
- تثبيت Android SDK و Flutter plugin

#### iOS (macOS only)
```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcode-select --reset
```

### 3. التحقق من التثبيت

```bash
flutter doctor
```

## إعداد المشروع

### 1. استنساخ المشروع

```bash
git clone <repository-url>
cd flutter_app/asset_maintenance_app
```

### 2. تثبيت المكتبات

```bash
flutter pub get
```

### 3. توليد الملفات المطلوبة

```bash
# توليد ملفات Riverpod و Freezed
flutter pub run build_runner build --delete-conflicting-outputs

# للمراقبة المستمرة (أثناء التطوير)
flutter pub run build_runner watch
```

### 4. إعداد Backend

تأكد من أن Backend قيد التشغيل على:
```
http://localhost:8000
```

تعديل `lib/services/api_service.dart` إذا كان Backend على عنوان مختلف:

```dart
static const String baseUrl = 'http://your-backend-url/api';
```

## التشغيل

### تشغيل على Android Emulator

```bash
# فتح Android Studio و إنشاء emulator
flutter run -d emulator-5554
```

### تشغيل على iOS Simulator

```bash
# (macOS only)
open -a Simulator
flutter run
```

### تشغيل على جهاز حقيقي

```bash
# فتح وضع المطور على الجهاز
flutter run
```

## البناء

### بناء APK

```bash
# debug APK
flutter build apk --debug

# release APK
flutter build apk --release
```

### بناء iOS IPA

```bash
# (macOS only)
flutter build ios --release
```

## أثناء التطوير

### مراقبة الملفات

```bash
flutter pub run build_runner watch
```

### تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
flutter test

# تشغيل اختبار معين
flutter test test/screens/auth/login_screen_test.dart
```

### تحليل الكود

```bash
flutter analyze
```

### تنسيق الكود

```bash
dart format lib/
```

## استكشاف الأخطاء

### مشاكل شائعة

#### 1. "Flutter command not found"
- تأكد من إضافة Flutter إلى PATH
- تشغيل `flutter doctor` للتحقق

#### 2. "Android SDK not found"
- فتح Android Studio
- الذهاب إلى Tools > SDK Manager
- تثبيت Android SDK

#### 3. "CocoaPods not installed" (macOS)
```bash
sudo gem install cocoapods
cd ios
pod install
cd ..
```

#### 4. مشاكل الاتصال بـ Backend
- تحقق من عنوان Backend في `api_service.dart`
- تأكد من أن Backend قيد التشغيل
- تحقق من الـ Firewall والـ networking

## الإعدادات المتقدمة

### تغيير رقم الإصدار

في `pubspec.yaml`:
```yaml
version: 1.0.0+1
```

### تخصيص أسماء الحزم

#### Android
في `android/app/build.gradle`:
```gradle
defaultConfig {
    applicationId "com.assetmaintenance.app"
}
```

#### iOS
في `ios/Runner.xcodeproj/project.pbxproj`:
```
PRODUCT_BUNDLE_IDENTIFIER = com.assetmaintenance.app
```

## دعم إضافي

للمزيد من المعلومات:
- [Flutter Documentation](https://flutter.dev/docs)
- [Riverpod Guide](https://riverpod.dev)
- [Go Router](https://pub.dev/packages/go_router)
