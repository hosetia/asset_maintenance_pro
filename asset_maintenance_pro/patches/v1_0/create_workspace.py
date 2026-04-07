"""
Patch v1.0: Create full Asset Maintenance Pro Workspace.
"""
import frappe, json

WS_NAME = "Asset Maintenance Pro"

CONTENT = json.dumps([
    {"type":"header","data":{"text":"<h2>🔧 Asset Maintenance Pro</h2>","col":12}},

    {"type":"header","data":{"text":"<h4>📋 Transactions</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Maintenance Request","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"New Request","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Work Logs","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Spare Parts","col":3}},

    {"type":"header","data":{"text":"<h4>📊 Dashboard & Kanban</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Dashboard","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Kanban Board","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Open Requests","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Overdue Requests","col":3}},

    {"type":"header","data":{"text":"<h4>⚙️ Masters & Configuration</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Maintenance Checklist","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"SLA Policies","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Assignment Rules","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Meter Readings","col":3}},

    {"type":"header","data":{"text":"<h4>🧠 Knowledge & Reports</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Knowledge Base","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Completed Requests","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Spare Part Usage","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Settings","col":3}},
])

SHORTCUTS = [
    ("Maintenance Request",   "Maintenance Request",         "DocType", 1,  "#2490EF", "tool"),
    ("New Request",           "Maintenance Request",         "DocType", 2,  "#28a745", "add"),
    ("Work Logs",             "Maintenance Work Log",        "DocType", 3,  "#fd7e14", "file"),
    ("Spare Parts",           "Spare Part Consumption",      "DocType", 4,  "#dc3545", "stock"),
    ("Dashboard",             "maintenance-dashboard",       "Page",    5,  "#6f42c1", "dashboard"),
    ("Kanban Board",          "Maintenance Request",         "DocType", 6,  "#805ad5", "kanban"),
    ("Open Requests",         "Maintenance Request",         "DocType", 7,  "#2490EF", "list"),
    ("Overdue Requests",      "Maintenance Request",         "DocType", 8,  "#dc3545", "error"),
    ("Maintenance Checklist", "Maintenance Checklist",       "DocType", 9,  "#6f42c1", "list"),
    ("SLA Policies",          "Maintenance SLA Policy",      "DocType", 10, "#e83e8c", "timer"),
    ("Assignment Rules",      "Maintenance Assignment Rule", "DocType", 11, "#20c997", "assign"),
    ("Meter Readings",        "Asset Meter Reading",         "DocType", 12, "#17a2b8", "dashboard"),
    ("Knowledge Base",        "Maintenance Knowledge Base",  "DocType", 13, "#6610f2", "book"),
    ("Completed Requests",    "Maintenance Request",         "DocType", 14, "#28a745", "check"),
    ("Spare Part Usage",      "Spare Part Consumption",      "DocType", 15, "#fd7e14", "stock"),
    ("Settings",              "Asset Maintenance Settings",  "DocType", 16, "#6c757d", "setting"),
]

LINKS = [
    {"label":"Maintenance","items":[
        {"name":"Maintenance Request",      "label":"Maintenance Request"},
        {"name":"Maintenance Work Log",     "label":"Work Log"},
        {"name":"Spare Part Consumption",   "label":"Spare Parts"},
    ]},
    {"label":"Planning","items":[
        {"name":"Maintenance Checklist",       "label":"Maintenance Checklist"},
        {"name":"Maintenance SLA Policy",      "label":"SLA Policy"},
        {"name":"Maintenance Assignment Rule", "label":"Assignment Rule"},
        {"name":"Asset Maintenance Settings",  "label":"Settings"},
    ]},
    {"label":"Readings & Knowledge","items":[
        {"name":"Asset Meter Reading",        "label":"Meter Reading"},
        {"name":"Maintenance Knowledge Base", "label":"Knowledge Base"},
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
            for label, link_to, stype, idx, color, icon in SHORTCUTS:
                # Skip Page type if not supported in this version
                if stype == "Page":
                    valid_types = [o.value for o in sc_meta.get_field("type").options.split("\n")] if sc_meta.get_field("type") else []
                    if valid_types and "Page" not in valid_types:
                        stype = "DocType"
                        link_to = "Maintenance Request"
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
        print("✅ Workspace created")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AMP Workspace Creation")
        print(f"❌ {e}")
