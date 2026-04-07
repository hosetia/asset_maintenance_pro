"""Patch v1.0: Create full Asset Maintenance Pro Workspace v4.0 — grouped cards."""
import frappe, json

WS_NAME = "Asset Maintenance Pro"

CONTENT = json.dumps([
    {"type":"header","data":{"text":"<h2>🔧 Asset Maintenance Pro</h2>","col":12}},

    # ── Operations ─────────────────────────────────────────────────────────────
    {"type":"header","data":{"text":"<h4>📋 العمليات</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"طلب صيانة جديد","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"كل الطلبات","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"أوامر العمل","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"طلبات قطع الغيار","col":3}},

    # ── Dashboard ──────────────────────────────────────────────────────────────
    {"type":"header","data":{"text":"<h4>📊 لوحات التحكم والتقارير</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"لوحة التحكم","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تقرير دوري","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تحليل TCO","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"مطابقة SLA","col":3}},

    # ── Config ─────────────────────────────────────────────────────────────────
    {"type":"header","data":{"text":"<h4>⚙️ الإعدادات والتخطيط</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"جداول PM","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"سياسات SLA","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"فرق الصيانة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"قواعد التعيين","col":3}},

    # ── Compliance ─────────────────────────────────────────────────────────────
    {"type":"header","data":{"text":"<h4>🏢 الامتثال والعقود</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"الفحوصات","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"عقود الخدمة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"قراءات العداد","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"المواقع","col":3}},

    # ── Knowledge ──────────────────────────────────────────────────────────────
    {"type":"header","data":{"text":"<h4>🧠 المعرفة والأدلة</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"قاعدة المعرفة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"الأدلة التقنية","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"BOM الصيانة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تصنيف الأعطال","col":3}},
])

SHORTCUTS = [
    # Operations
    ("طلب صيانة جديد",  "Maintenance Request",         "DocType", 1,  "#28a745", "add"),
    ("كل الطلبات",       "Maintenance Request",         "DocType", 2,  "#2490EF", "list"),
    ("أوامر العمل",      "Maintenance Work Order",      "DocType", 3,  "#fd7e14", "tool"),
    ("طلبات قطع الغيار","Spare Part Request",           "DocType", 4,  "#17a2b8", "stock"),
    # Dashboard & Reports
    ("لوحة التحكم",      "maintenance-dashboard",       "Page",    5,  "#6f42c1", "dashboard"),
    ("تقرير دوري",       "Maintenance Period Report",   "Report",  6,  "#20c997", "file-text"),
    ("تحليل TCO",        "TCO Analysis",                "Report",  7,  "#e83e8c", "bar-chart"),
    ("مطابقة SLA",       "PM Compliance",               "Report",  8,  "#fd7e14", "check-circle"),
    # Config
    ("جداول PM",         "Maintenance Checklist",       "DocType", 9,  "#6f42c1", "list"),
    ("سياسات SLA",       "Maintenance SLA Policy",      "DocType", 10, "#e83e8c", "timer"),
    ("فرق الصيانة",      "Maintenance Team",            "DocType", 11, "#20c997", "users"),
    ("قواعد التعيين",    "Maintenance Assignment Rule", "DocType", 12, "#17a2b8", "assign"),
    # Compliance
    ("الفحوصات",         "Maintenance Inspection",      "DocType", 13, "#dc3545", "clipboard"),
    ("عقود الخدمة",      "Service Contract",            "DocType", 14, "#6f42c1", "file-text"),
    ("قراءات العداد",    "Asset Meter Reading",         "DocType", 15, "#17a2b8", "activity"),
    ("المواقع",          "Maintenance Location",        "DocType", 16, "#28a745", "map-pin"),
    # Knowledge
    ("قاعدة المعرفة",    "Maintenance Knowledge Base",  "DocType", 17, "#6610f2", "book"),
    ("الأدلة التقنية",   "Maintenance Technical Manual","DocType", 18, "#fd7e14", "book-open"),
    ("BOM الصيانة",      "Maintenance BOM",             "DocType", 19, "#20c997", "layers"),
    ("تصنيف الأعطال",   "Asset Taxonomy",              "DocType", 20, "#6c757d", "tag"),
]

LINKS = [
    {"label":"📋 العمليات اليومية","items":[
        {"name":"Maintenance Request",    "label":"طلب صيانة"},
        {"name":"Maintenance Work Order", "label":"أمر عمل"},
        {"name":"Spare Part Request",     "label":"طلب قطع غيار"},
        {"name":"Maintenance Work Log",   "label":"سجل العمل"},
        {"name":"Spare Part Consumption", "label":"استهلاك قطع الغيار"},
    ]},
    {"label":"📊 التقارير والتحليل","items":[
        {"name":"Maintenance Period Report","label":"تقرير الفترة"},
        {"name":"TCO Analysis",             "label":"تحليل TCO"},
        {"name":"Asset Availability & Uptime","label":"توفر الأصول"},
        {"name":"MTTR & MTBF Analysis",     "label":"MTTR & MTBF"},
        {"name":"PM Compliance",            "label":"مطابقة PM"},
        {"name":"Open Tickets Aging",       "label":"تقادم الطلبات"},
        {"name":"Pareto Fault Analysis",    "label":"تحليل باريتو"},
        {"name":"Technician Productivity",  "label":"إنتاجية الفنيين"},
        {"name":"Vendor SLA Compliance",    "label":"مطابقة مورد SLA"},
        {"name":"Maintenance Cost by Branch","label":"التكلفة بالفرع"},
        {"name":"Spare Parts Consumption",  "label":"استهلاك قطع الغيار"},
        {"name":"Repeat Failures Analysis", "label":"تحليل الأعطال المتكررة"},
        {"name":"Warranty Expiry Tracker",  "label":"تتبع انتهاء الضمان"},
        {"name":"Contract Utilization",     "label":"استخدام العقود"},
    ]},
    {"label":"⚙️ الإعدادات والتخطيط","items":[
        {"name":"Maintenance Checklist",       "label":"جدول PM"},
        {"name":"Maintenance SLA Policy",      "label":"سياسة SLA"},
        {"name":"Maintenance Assignment Rule", "label":"قاعدة التعيين"},
        {"name":"Maintenance Team",            "label":"فريق الصيانة"},
        {"name":"Maintenance BOM",             "label":"BOM الصيانة"},
        {"name":"Asset Maintenance Settings",  "label":"الإعدادات"},
    ]},
    {"label":"🏢 الامتثال والضمان","items":[
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
    if frappe.db.exists("Workspace", WS_NAME):
        frappe.delete_doc("Workspace", WS_NAME, ignore_permissions=True, force=True)
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
            if sc_meta.get_field("type"):
                valid_types = [o.strip() for o in sc_meta.get_field("type").options.split("\n")]
            for label, link_to, stype, idx, color, icon in SHORTCUTS:
                if valid_types and stype not in valid_types:
                    stype = "DocType"
                    if stype == "Page": link_to = "Maintenance Request"
                    elif stype == "Report": link_to = "Maintenance Request"
                row = {"label": label, "link_to": link_to, "type": stype, "idx": idx}
                if "color" in sc_fields: row["color"] = color
                if "icon"  in sc_fields: row["icon"]  = icon
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
        print("✅ Workspace v4.0 created")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AMP Workspace v4.0")
        print(f"❌ {e}")
