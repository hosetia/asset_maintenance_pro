"""Patch v1.0: Asset Maintenance Pro Workspace — stable v6."""
import frappe, json

WS_NAME = "Asset Maintenance Pro"

CONTENT = json.dumps([
    {"type":"header","data":{"text":"<h2>🔧 Asset Maintenance Pro</h2>","col":12}},

    {"type":"header","data":{"text":"<h4>⚡ إجراءات سريعة</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"لوحة التحكم","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"طلب صيانة جديد","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"كل الطلبات","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"أوامر العمل","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"تقرير دوري","col":2}},
    {"type":"shortcut","data":{"shortcut_name":"الإعدادات","col":2}},

    {"type":"header","data":{"text":"<h4>📋 العمليات</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"طلبات قطع الغيار","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"سجلات العمل","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"استهلاك قطع الغيار","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"الفحوصات","col":3}},

    {"type":"header","data":{"text":"<h4>⚙️ التخطيط</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"جداول PM","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"سياسات SLA","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"فرق الصيانة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"قواعد التعيين","col":3}},

    {"type":"header","data":{"text":"<h4>🏢 الامتثال والعقود</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"عقود الخدمة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"قراءات العداد","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"المواقع","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"الأدلة التقنية","col":3}},

    {"type":"header","data":{"text":"<h4>🧠 المعرفة</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"قاعدة المعرفة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تصنيف الأعطال","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"BOM الصيانة","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"تحليل TCO","col":3}},
])

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
        {"name":"Maintenance BOM",              "label":"BOM الصيانة"},
    ]},
    {"label":"📊 الأصول والمخزون","items":[
        {"name":"Asset",                  "label":"الأصول"},
        {"name":"Asset Meter Reading",    "label":"قراءات العداد"},
        {"name":"Spare Part Consumption", "label":"استهلاك قطع الغيار"},
    ]},
]


def execute():
    # Delete all old variants
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

        # Detect valid shortcut types from meta
        if "shortcuts" in field_names:
            sc_meta     = frappe.get_meta("Workspace Shortcut")
            sc_fields   = {f.fieldname for f in sc_meta.fields}
            type_field  = sc_meta.get_field("type")
            valid_types = set()
            if type_field and type_field.options:
                valid_types = {o.strip() for o in type_field.options.split("\n") if o.strip()}

            # Build shortcuts — detect dashboard page support
            has_page = "Page" in valid_types

            all_shortcuts = [
                # label,                  link_to,                        type,      idx, color
                ("لوحة التحكم",      "maintenance-dashboard" if has_page else "Maintenance Request",
                                                                          "Page" if has_page else "DocType", 1,  "#6f42c1"),
                ("طلب صيانة جديد",  "Maintenance Request",              "DocType", 2,  "#28a745"),
                ("كل الطلبات",       "Maintenance Request",              "DocType", 3,  "#2490EF"),
                ("أوامر العمل",      "Maintenance Work Order",           "DocType", 4,  "#fd7e14"),
                ("تقرير دوري",       "Maintenance Request",              "DocType", 5,  "#20c997"),
                ("الإعدادات",        "Asset Maintenance Settings",       "DocType", 6,  "#6c757d"),
                ("طلبات قطع الغيار","Spare Part Request",               "DocType", 7,  "#17a2b8"),
                ("سجلات العمل",      "Maintenance Work Log",             "DocType", 8,  "#6c757d"),
                ("استهلاك قطع الغيار","Spare Part Consumption",         "DocType", 9,  "#dc3545"),
                ("الفحوصات",         "Maintenance Inspection",           "DocType", 10, "#dc3545"),
                ("جداول PM",         "Maintenance Checklist",            "DocType", 11, "#6f42c1"),
                ("سياسات SLA",       "Maintenance SLA Policy",           "DocType", 12, "#e83e8c"),
                ("فرق الصيانة",      "Maintenance Team",                 "DocType", 13, "#20c997"),
                ("قواعد التعيين",    "Maintenance Assignment Rule",      "DocType", 14, "#17a2b8"),
                ("عقود الخدمة",      "Service Contract",                 "DocType", 15, "#6f42c1"),
                ("قراءات العداد",    "Asset Meter Reading",              "DocType", 16, "#17a2b8"),
                ("المواقع",          "Maintenance Location",             "DocType", 17, "#28a745"),
                ("الأدلة التقنية",   "Maintenance Technical Manual",     "DocType", 18, "#fd7e14"),
                ("قاعدة المعرفة",    "Maintenance Knowledge Base",       "DocType", 19, "#6610f2"),
                ("تصنيف الأعطال",   "Asset Taxonomy",                   "DocType", 20, "#6c757d"),
                ("BOM الصيانة",      "Maintenance BOM",                  "DocType", 21, "#20c997"),
                ("تحليل TCO",        "Asset",                            "DocType", 22, "#e83e8c"),
            ]

            for label, link_to, stype, idx, color in all_shortcuts:
                # Validate type
                if valid_types and stype not in valid_types:
                    stype    = "DocType"
                    link_to  = "Maintenance Request"
                row = {"label": label, "link_to": link_to, "type": stype, "idx": idx}
                if "color" in sc_fields: row["color"] = color
                ws.append("shortcuts", row)

        if "links" in field_names:
            lk_meta   = frappe.get_meta("Workspace Link")
            lk_fields = {f.fieldname for f in lk_meta.fields}
            for group in LINKS:
                ws.append("links", {"type":"Card Break","label":group["label"],"hidden":0})
                for item in group["items"]:
                    # Validate DocType exists before adding
                    if not frappe.db.exists("DocType", item["name"]):
                        continue
                    row = {"type":"Link","hidden":0}
                    if "link_to" in lk_fields: row["link_to"] = item["name"]
                    if "label"   in lk_fields: row["label"]   = item["label"]
                    ws.append("links", row)

        ws.flags.ignore_permissions = True
        ws.flags.ignore_mandatory   = True
        ws.flags.ignore_validate    = True
        ws.insert(set_name=WS_NAME)
        frappe.db.commit()

        # Add Dashboard shortcut via SQL after insert (bypasses type validation)
        _add_dashboard_shortcut_sql()

        print("✅ Workspace v6 created")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AMP Workspace v6")
        print(f"❌ {e}")


def _add_dashboard_shortcut_sql():
    """Add the Dashboard page shortcut directly via SQL to bypass type validation."""
    from frappe.utils import now
    ts = now()

    # Check what columns exist in tabWorkspace Shortcut
    cols = {r[0] for r in frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Shortcut`")}

    # Check if dashboard shortcut already exists
    existing = frappe.db.sql(
        "SELECT name FROM `tabWorkspace Shortcut` WHERE parent=%s AND label=%s",
        (WS_NAME, "لوحة التحكم")
    )
    if existing:
        return

    fields = ["name","parent","parenttype","parentfield","idx","label",
              "owner","creation","modified","modified_by","docstatus"]
    values = {
        "name":        f"{WS_NAME}-dashboard",
        "parent":      WS_NAME,
        "parenttype":  "Workspace",
        "parentfield": "shortcuts",
        "idx":         0,
        "label":       "لوحة التحكم",
        "owner":       "Administrator",
        "creation":    ts,
        "modified":    ts,
        "modified_by": "Administrator",
        "docstatus":   0,
    }

    # Add optional fields if they exist
    for col, val in {
        "type":    "Page",
        "link_to": "maintenance-dashboard",
        "color":   "#6f42c1",
        "icon":    "dashboard",
    }.items():
        if col in cols:
            fields.append(col)
            values[col] = val

    cols_sql = ", ".join(f"`{f}`" for f in fields)
    vals_sql = ", ".join(f"%({f})s" for f in fields)
    frappe.db.sql(
        f"INSERT IGNORE INTO `tabWorkspace Shortcut` ({cols_sql}) VALUES ({vals_sql})",
        values
    )
    frappe.db.commit()
