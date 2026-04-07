"""Patch v1.0: Asset Maintenance Pro Workspace — complete & organized."""
import frappe, json

WS_NAME = "Asset Maintenance Pro"

CONTENT = json.dumps([
    {"type":"header","data":{"text":"<h2>🔧 Asset Maintenance Pro</h2>","col":12}},

    # Row 1 — Quick Actions
    {"type":"header","data":{"text":"<h4>⚡ إجراءات سريعة</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"طلب صيانة جديد","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"لوحة التحكم","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"Kanban","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"تقرير دوري","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"تحليل TCO","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"الإعدادات","col":2}},

    # Row 2 — Operations
    {"type":"header","data":{"text":"<h4>📋 العمليات</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"كل الطلبات","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"أوامر العمل","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"طلبات قطع الغيار","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"سجلات العمل","col":3}},

    # Row 3 — Planning
    {"type":"header","data":{"text":"<h4>⚙️ التخطيط والجدولة</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"جداول PM","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"سياسات SLA","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"فرق الصيانة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"قواعد التعيين","col":3}},

    # Row 4 — Compliance
    {"type":"header","data":{"text":"<h4>🏢 الامتثال والعقود</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"الفحوصات","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"عقود الخدمة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"قراءات العداد","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"المواقع","col":3}},

    # Row 5 — Knowledge & Reports
    {"type":"header","data":{"text":"<h4>🧠 المعرفة والتقارير</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"قاعدة المعرفة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"الأدلة التقنية","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تصنيف الأعطال","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"إنتاجية الفنيين","col":3}},
])

SHORTCUTS = [
    # Quick actions (row 1)
    ("طلب صيانة جديد",  "Maintenance Request",          "DocType", 1,  "#28a745"),
    ("لوحة التحكم",      "Maintenance Request",          "DocType", 2,  "#6f42c1"),
    ("Kanban",           "Maintenance Request",          "DocType", 3,  "#2490EF"),
    ("تقرير دوري",       "Maintenance Request",          "DocType", 4,  "#20c997"),
    ("تحليل TCO",        "Asset",                        "DocType", 5,  "#e83e8c"),
    ("الإعدادات",        "Asset Maintenance Settings",   "DocType", 6,  "#6c757d"),
    # Operations (row 2)
    ("كل الطلبات",       "Maintenance Request",          "DocType", 7,  "#2490EF"),
    ("أوامر العمل",      "Maintenance Work Order",       "DocType", 8,  "#fd7e14"),
    ("طلبات قطع الغيار","Spare Part Request",            "DocType", 9,  "#17a2b8"),
    ("سجلات العمل",      "Maintenance Work Log",         "DocType", 10, "#6c757d"),
    # Planning (row 3)
    ("جداول PM",         "Maintenance Checklist",        "DocType", 11, "#6f42c1"),
    ("سياسات SLA",       "Maintenance SLA Policy",       "DocType", 12, "#e83e8c"),
    ("فرق الصيانة",      "Maintenance Team",             "DocType", 13, "#20c997"),
    ("قواعد التعيين",    "Maintenance Assignment Rule",  "DocType", 14, "#17a2b8"),
    # Compliance (row 4)
    ("الفحوصات",         "Maintenance Inspection",       "DocType", 15, "#dc3545"),
    ("عقود الخدمة",      "Service Contract",             "DocType", 16, "#6f42c1"),
    ("قراءات العداد",    "Asset Meter Reading",          "DocType", 17, "#17a2b8"),
    ("المواقع",          "Maintenance Location",         "DocType", 18, "#28a745"),
    # Knowledge (row 5)
    ("قاعدة المعرفة",    "Maintenance Knowledge Base",   "DocType", 19, "#6610f2"),
    ("الأدلة التقنية",   "Maintenance Technical Manual", "DocType", 20, "#fd7e14"),
    ("تصنيف الأعطال",   "Asset Taxonomy",               "DocType", 21, "#6c757d"),
    ("إنتاجية الفنيين",  "Maintenance Work Order",       "DocType", 22, "#20c997"),
]

LINKS = [
    {"label":"📋 العمليات اليومية","items":[
        {"name":"Maintenance Request",    "label":"طلب صيانة"},
        {"name":"Maintenance Work Order", "label":"أمر عمل"},
        {"name":"Spare Part Request",     "label":"طلب قطع غيار"},
        {"name":"Maintenance Work Log",   "label":"سجل العمل"},
        {"name":"Spare Part Consumption", "label":"استهلاك قطع الغيار"},
        {"name":"Maintenance Inspection", "label":"فحص"},
    ]},
    {"label":"⚙️ التخطيط والإعدادات","items":[
        {"name":"Maintenance Checklist",       "label":"جدول PM"},
        {"name":"Maintenance SLA Policy",      "label":"سياسة SLA"},
        {"name":"Maintenance Assignment Rule", "label":"قاعدة التعيين"},
        {"name":"Maintenance Team",            "label":"فريق الصيانة"},
        {"name":"Asset Maintenance Settings",  "label":"الإعدادات"},
        {"name":"Maintenance Location",        "label":"الموقع"},
        {"name":"Asset Taxonomy",              "label":"تصنيف الأعطال"},
        {"name":"Asset Meter Reading",         "label":"قراءة العداد"},
    ]},
    {"label":"🏢 العقود والضمان","items":[
        {"name":"Service Contract",             "label":"عقد الخدمة"},
        {"name":"Maintenance Technical Manual", "label":"الدليل التقني"},
        {"name":"Maintenance Knowledge Base",   "label":"قاعدة المعرفة"},
    ]},
    {"label":"📊 الأصول والمخزون","items":[
        {"name":"Asset",                  "label":"الأصول"},
        {"name":"Asset Meter Reading",    "label":"قراءات العداد"},
        {"name":"Spare Part Consumption", "label":"استهلاك قطع الغيار"},
        {"name":"Spare Part Request",     "label":"طلب قطع غيار"},
    ]},
]


def execute():
    for old_name in [WS_NAME, "Asset Maintenance", "Asset Maintenance Pro"]:
        if frappe.db.exists("Workspace", old_name):
            frappe.delete_doc("Workspace", old_name, ignore_permissions=True, force=True)
    frappe.db.commit()

    try:
        ws         = frappe.new_doc("Workspace")
        ws.public  = 1
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
            valid_types = []
            type_field = sc_meta.get_field("type")
            if type_field and type_field.options:
                valid_types = [o.strip() for o in type_field.options.split("\n") if o.strip()]
            for label, link_to, stype, idx, color in SHORTCUTS:
                # If URL type not supported, use DocType fallback
                if valid_types and stype not in valid_types:
                    if stype == "URL":
                        stype = "DocType"
                        link_to = "Maintenance Request"
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
        print("✅ Workspace created successfully")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AMP Workspace")
        print(f"❌ {e}")
