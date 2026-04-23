import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:asset_maintenance_app/config/theme.dart';
import 'package:asset_maintenance_app/models/maintenance_request_model.dart';
import 'package:asset_maintenance_app/providers/maintenance_provider.dart';
import 'dart:io';

class CreateMaintenanceScreen extends ConsumerStatefulWidget {
  const CreateMaintenanceScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<CreateMaintenanceScreen> createState() =>
      _CreateMaintenanceScreenState();
}

class _CreateMaintenanceScreenState
    extends ConsumerState<CreateMaintenanceScreen> {
  late TextEditingController _assetController;
  late TextEditingController _descriptionController;
  late TextEditingController _notesController;
  String? _maintenanceType;
  String? _priority;
  DateTime? _dueDate;
  final List<File> _attachments = [];
  final ImagePicker _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _assetController = TextEditingController();
    _descriptionController = TextEditingController();
    _notesController = TextEditingController();
    _maintenanceType = 'Preventive';
    _priority = 'Medium';
  }

  @override
  void dispose() {
    _assetController.dispose();
    _descriptionController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _pickImage() async {
    final XFile? image =
        await _imagePicker.pickImage(source: ImageSource.camera);
    if (image != null) {
      setState(() {
        _attachments.add(File(image.path));
      });
    }
  }

  Future<void> _pickGalleryImage() async {
    final XFile? image =
        await _imagePicker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() {
        _attachments.add(File(image.path));
      });
    }
  }

  Future<void> _selectDueDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 7)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      locale: const Locale('ar', 'SA'),
    );
    if (picked != null && picked != _dueDate) {
      setState(() {
        _dueDate = picked;
      });
    }
  }

  Future<void> _submitForm() async {
    if (_assetController.text.isEmpty) {
      _showError('يرجى إدخال اسم الأصل');
      return;
    }

    final request = MaintenanceRequest(
      asset: _assetController.text,
      assetName: _assetController.text,
      assetCategory: 'Equipment',
      maintenanceType: _maintenanceType,
      description: _descriptionController.text,
      status: 'Draft',
      dueDate: _dueDate,
      priority: _priority,
      notes: _notesController.text,
      createdDate: DateTime.now(),
    );

    // TODO: Upload attachments
    // TODO: Create request via API

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('تم إنشاء طلب الصيانة بنجاح'),
          backgroundColor: Colors.green,
        ),
      );
      context.pop();
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('فتح طلب صيانة جديد'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Asset Field
              const Text(
                'اختر الأصل *',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: AppTheme.darkGray,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _assetController,
                textDirection: TextDirection.rtl,
                decoration: InputDecoration(
                  hintText: 'اسم الأصل',
                  hintTextDirection: TextDirection.rtl,
                  prefixIcon: const Icon(Icons.widgets),
                ),
              ),
              const SizedBox(height: 20),
              // Maintenance Type
              const Text(
                'نوع الصيانة',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: AppTheme.darkGray,
                ),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _maintenanceType,
                items: const [
                  DropdownMenuItem(
                    value: 'Preventive',
                    child: Text('وقائية'),
                  ),
                  DropdownMenuItem(
                    value: 'Corrective',
                    child: Text('تصحيحية'),
                  ),
                  DropdownMenuItem(
                    value: 'Emergency',
                    child: Text('طوارئ'),
                  ),
                ],
                onChanged: (value) {
                  setState(() => _maintenanceType = value);
                },
              ),
              const SizedBox(height: 20),
              // Priority
              const Text(
                'الأولوية',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: AppTheme.darkGray,
                ),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _priority,
                items: const [
                  DropdownMenuItem(
                    value: 'Low',
                    child: Text('منخفضة'),
                  ),
                  DropdownMenuItem(
                    value: 'Medium',
                    child: Text('متوسطة'),
                  ),
                  DropdownMenuItem(
                    value: 'High',
                    child: Text('عالية'),
                  ),
                ],
                onChanged: (value) {
                  setState(() => _priority = value);
                },
              ),
              const SizedBox(height: 20),
              // Due Date
              const Text(
                'موعد الاستحقاق',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: AppTheme.darkGray,
                ),
              ),
              const SizedBox(height: 8),
              GestureDetector(
                onTap: _selectDueDate,
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  decoration: BoxDecoration(
                    color: AppTheme.lightGray,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _dueDate != null
                            ? _dueDate.toString().split(' ')[0]
                            : 'حدد التاريخ',
                        style: TextStyle(
                          color: _dueDate != null
                              ? AppTheme.darkGray
                              : AppTheme.gray,
                          fontSize: 14,
                        ),
                      ),
                      const Icon(Icons.calendar_today,
                          color: AppTheme.primaryColor),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
              // Description
              const Text(
                'الوصف',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: AppTheme.darkGray,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _descriptionController,
                textDirection: TextDirection.rtl,
                maxLines: 3,
                decoration: InputDecoration(
                  hintText: 'صف المشكلة أو الصيانة المطلوبة',
                  hintTextDirection: TextDirection.rtl,
                ),
              ),
              const SizedBox(height: 20),
              // Attachments
              const Text(
                'الصور والمرفقات',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: AppTheme.darkGray,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  ElevatedButton.icon(
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('التقط صورة'),
                    onPressed: _pickImage,
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    icon: const Icon(Icons.image),
                    label: const Text('من المعرض'),
                    onPressed: _pickGalleryImage,
                  ),
                ],
              ),
              if (_attachments.isNotEmpty)
                Column(
                  children: [
                    const SizedBox(height: 12),
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate:
                          const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 3,
                        mainAxisSpacing: 8,
                        crossAxisSpacing: 8,
                      ),
                      itemCount: _attachments.length,
                      itemBuilder: (context, index) {
                        return Stack(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Image.file(
                                _attachments[index],
                                fit: BoxFit.cover,
                              ),
                            ),
                            Positioned(
                              top: 4,
                              right: 4,
                              child: GestureDetector(
                                onTap: () {
                                  setState(() {
                                    _attachments.removeAt(index);
                                  });
                                },
                                child: Container(
                                  decoration: BoxDecoration(
                                    color: Colors.red,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: const Icon(
                                    Icons.close,
                                    color: Colors.white,
                                    size: 16,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        );
                      },
                    ),
                  ],
                ),
              const SizedBox(height: 20),
              // Notes
              const Text(
                'ملاحظات إضافية',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: AppTheme.darkGray,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _notesController,
                textDirection: TextDirection.rtl,
                maxLines: 3,
                decoration: InputDecoration(
                  hintText: 'أضف أي ملاحظات إضافية',
                  hintTextDirection: TextDirection.rtl,
                ),
              ),
              const SizedBox(height: 24),
              // Submit Button
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: _submitForm,
                  child: const Text(
                    'إنشاء طلب الصيانة',
                    style: TextStyle(fontSize: 16),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: OutlinedButton(
                  onPressed: () => context.pop(),
                  child: const Text('إلغاء'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
