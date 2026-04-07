"""Patch v1.0: Create Asset Maintenance Pro Workspace — stable version."""
import frappe, json

WS_NAME = "Asset Maintenance Pro"

CONTENT = json.dumps([
    {"type":"header","data":{"text":"<h2>🔧 Asset Maintenance Pro</h2>","col":12}},

    {"type":"header","data":{"text":"<h4>📋 العمليات</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"طلب صيانة جديد","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"كل الطلبات","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"أوامر العمل","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"طلبات قطع الغيار","col":3}},

    {"type":"header","data":{"text":"<h4>📊 التقارير</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"لوحة التحكم","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تقرير دوري","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تحليل TCO","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"مطابقة PM","col":3}},

    {"type":"header","data":{"text":"<h4>⚙️ الإعدادات</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"جداول PM","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"سياسات SLA","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"فرق الصيانة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"قواعد التعيين","col":3}},

    {"type":"header","data":{"text":"<h4>🏢 الامتثال</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"الفحوصات","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"عقود الخدمة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"قراءات العداد","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"المواقع","col":3}},

    {"type":"header","data":{"text":"<h4>🧠 المعرفة</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"قاعدة المعرفة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"الأدلة التقنية","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"BOM الصيانة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تصنيف الأعطال","col":3}},
])

# Only DocType shortcuts — no Page or Report (causes validation errors)
SHORTCUTS = [
    ("طلب صيانة جديد",  "Maintenance Request",          "DocType", 1,  "#28a745"),
    ("كل الطلبات",       "Maintenance Request",          "DocType", 2,  "#2490EF"),
    ("أوامر العمل",      "Maintenance Work Order",       "DocType", 3,  "#fd7e14"),
    ("طلبات قطع الغيار","Spare Part Request",            "DocType", 4,  "#17a2b8"),
    ("لوحة التحكم",      "Maintenance Request",          "DocType", 5,  "#6f42c1"),
    ("تقرير دوري",       "Maintenance Request",          "DocType", 6,  "#20c997"),
    ("تحليل TCO",        "Asset",                        "DocType", 7,  "#e83e8c"),
    ("مطابقة PM",        "Maintenance Checklist",        "DocType", 8,  "#fd7e14"),
    ("جداول PM",         "Maintenance Checklist",        "DocType", 9,  "#6f42c1"),
    ("سياسات SLA",       "Maintenance SLA Policy",       "DocType", 10, "#e83e8c"),
    ("فرق الصيانة",      "Maintenance Team",             "DocType", 11, "#20c997"),
    ("قواعد التعيين",    "Maintenance Assignment Rule",  "DocType", 12, "#17a2b8"),
    ("الفحوصات",         "Maintenance Inspection",       "DocType", 13, "#dc3545"),
    ("عقود الخدمة",      "Service Contract",             "DocType", 14, "#6f42c1"),
    ("قراءات العداد",    "Asset Meter Reading",          "DocType", 15, "#17a2b8"),
    ("المواقع",          "Maintenance Location",         "DocType", 16, "#28a745"),
    ("قاعدة المعرفة",    "Maintenance Knowledge Base",   "DocType", 17, "#6610f2"),
    ("الأدلة التقنية",   "Maintenance Technical Manual", "DocType", 18, "#fd7e14"),
    ("BOM الصيانة",      "Maintenance BOM",              "DocType", 19, "#20c997"),
    ("تصنيف الأعطال",   "Asset Taxonomy",               "DocType", 20, "#6c757d"),
]

LINKS = [
    {"label":"📋 العمليات اليومية","items":[
        {"name":"Maintenance Request",    "label":"طلب صيانة"},
        {"name":"Maintenance Work Order", "label":"أمر عمل"},
        {"name":"Spare Part Request",     "label":"طلب قطع غيار"},
        {"name":"Maintenance Work Log",   "label":"سجل العمل"},
        {"name":"Spare Part Consumption", "label":"استهلاك قطع الغيار"},
    ]},
    {"label":"⚙️ التخطيط والإعدادات","items":[
        {"name":"Maintenance Checklist",       "label":"جدول PM"},
        {"name":"Maintenance SLA Policy",      "label":"سياسة SLA"},
        {"name":"Maintenance Assignment Rule", "label":"قاعدة التعيين"},
        {"name":"Maintenance Team",            "label":"فريق الصيانة"},
        {"name":"Maintenance BOM",             "label":"BOM الصيانة"},
        {"name":"Asset Maintenance Settings",  "label":"الإعدادات"},
    ]},
    {"label":"🏢 الامتثال والعقود","items":[
        {"name":"Maintenance Inspection",       "label":"الفحوصات"},
        {"name":"Service Contract",             "label":"عقد الخدمة"},
        {"name":"Asset Meter Reading",          "label":"قراءة العداد"},
        {"name":"Maintenance Location",         "label":"الموقع"},
        {"name":"Maintenance Technical Manual", "label":"الدليل التقني"},
    ]},
    {"label":"🧠 المعرفة والتصنيف","items":[
        {"name":"Maintenance Knowledge Base","label":"قاعدة المعرفة"},
        {"name":"Asset Taxonomy",            "label":"تصنيف الأعطال"},
    ]},
]


def execute():
    # Delete old versions with any name variant
    for old_name in [WS_NAME, "Asset Maintenance", "Asset Maintenance Pro"]:
        if frappe.db.exists("Workspace", old_name):
            frappe.delete_doc("Workspace", old_name, ignore_permissions=True, force=True)
    frappe.db.commit()

    try:
        ws        = frappe.new_doc("Workspace")
        ws.public = 1
        ws.content = CONTENT

        meta        = frappe.get_meta("Workspace")
        field_names = {f.fieldname for f in meta.fields}

        if "label"       in field_names: ws.label       = "Asset Maintenance"
        if "title"       in field_names: ws.title       = "Asset Maintenance Pro"
        if "module"      in field_names: ws.module      = "Asset Maintenance"
        if "category"    in field_names: ws.category    = "Modules"
        if "icon"        in field_names: ws.icon        = "tool"
        if "color"       in field_names: ws.color       = "#2490EF"
        if "sequence_id" in field_names: ws.sequence_id = 99.0
        if "is_standard" in field_names: ws.is_standard = 0

        if "shortcuts" in field_names:
            sc_meta   = frappe.get_meta("Workspace Shortcut")
            sc_fields = {f.fieldname for f in sc_meta.fields}
            for label, link_to, stype, idx, color in SHORTCUTS:
                row = {"label": label, "link_to": link_to, "type": stype, "idx": idx}
                if "color" in sc_fields: row["color"] = color
                ws.append("shortcuts", row)

        if "links" in field_names:
            lk_meta   = frappe.get_meta("Workspace Link")
            lk_fields = {f.fieldname for f in lk_meta.fields}
            for group in LINKS:
                ws.append("links", {"type":"Card Break","label":group["label"],"hidden":0})
                for item in group["items"]:
                    row = {"type":"Link","hidden":0}
                    if "link_to" in lk_fields: row["link_to"] = item["name"]
                    if "label"   in lk_fields: row["label"]   = item["label"]
                    ws.append("links", row)

        ws.flags.ignore_permissions = True
        ws.flags.ignore_mandatory   = True
        ws.flags.ignore_validate    = True
        ws.insert(set_name=WS_NAME)
        frappe.db.commit()
        print("✅ Workspace created")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AMP Workspace")
        print(f"❌ {e}")
