"""Patch: Create complete Asset Maintenance Pro Workspace — v3.0."""
import frappe, json

WS_NAME = "Asset Maintenance Pro"

CONTENT = json.dumps([
    {"type":"header","data":{"text":"<h2>🔧 Asset Maintenance Pro</h2>","col":12}},

    {"type":"header","data":{"text":"<h4>📋 Requests & Work Orders</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Maintenance Request","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"New Request","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Work Order","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Work Logs","col":3}},

    {"type":"header","data":{"text":"<h4>📊 Dashboard & Kanban</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Dashboard","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Open Requests","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Overdue Requests","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Spare Part Request","col":3}},

    {"type":"header","data":{"text":"<h4>⚙️ Masters & Configuration</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Maintenance Checklist","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"SLA Policies","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Assignment Rules","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Maintenance Teams","col":3}},

    {"type":"header","data":{"text":"<h4>🏢 Compliance & Contracts</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Inspections","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Service Contracts","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Meter Readings","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Locations","col":3}},

    {"type":"header","data":{"text":"<h4>📈 Reports</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Asset Uptime","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"MTTR & MTBF","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"PM Compliance","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Pareto Analysis","col":3}},

    {"type":"header","data":{"text":"<h4>🧠 Knowledge & Settings</h4>","col":12}},
    {"type":"shortcut","data":{"shortcut_name":"Knowledge Base","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Asset Taxonomy","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Completed Requests","col":3}},
    {"type":"shortcut","data":{"shortcut_name":"Settings","col":3}},
])

SHORTCUTS = [
    ("Maintenance Request",   "Maintenance Request",         "DocType", 1,  "#2490EF", "tool"),
    ("New Request",           "Maintenance Request",         "DocType", 2,  "#28a745", "add"),
    ("Work Order",            "Maintenance Work Order",      "DocType", 3,  "#fd7e14", "list"),
    ("Work Logs",             "Maintenance Work Log",        "DocType", 4,  "#6c757d", "file"),
    ("Dashboard",             "maintenance-dashboard",       "Page",    5,  "#6f42c1", "dashboard"),
    ("Open Requests",         "Maintenance Request",         "DocType", 6,  "#2490EF", "list"),
    ("Overdue Requests",      "Maintenance Request",         "DocType", 7,  "#dc3545", "error"),
    ("Spare Part Request",    "Spare Part Request",          "DocType", 8,  "#17a2b8", "stock"),
    ("Maintenance Checklist", "Maintenance Checklist",       "DocType", 9,  "#6f42c1", "list"),
    ("SLA Policies",          "Maintenance SLA Policy",      "DocType", 10, "#e83e8c", "timer"),
    ("Assignment Rules",      "Maintenance Assignment Rule", "DocType", 11, "#20c997", "assign"),
    ("Maintenance Teams",     "Maintenance Team",            "DocType", 12, "#fd7e14", "group"),
    ("Inspections",           "Maintenance Inspection",      "DocType", 13, "#dc3545", "tick"),
    ("Service Contracts",     "Service Contract",            "DocType", 14, "#6f42c1", "file-text"),
    ("Meter Readings",        "Asset Meter Reading",         "DocType", 15, "#17a2b8", "dashboard"),
    ("Locations",             "Maintenance Location",        "DocType", 16, "#28a745", "map-pin"),
    ("Asset Uptime",          "Asset Availability & Uptime", "Report",  17, "#2490EF", "bar-chart"),
    ("MTTR & MTBF",           "MTTR & MTBF Analysis",       "Report",  18, "#fd7e14", "trending-up"),
    ("PM Compliance",         "PM Compliance",               "Report",  19, "#28a745", "check-circle"),
    ("Pareto Analysis",       "Pareto Fault Analysis",       "Report",  20, "#dc3545", "pie-chart"),
    ("Knowledge Base",        "Maintenance Knowledge Base",  "DocType", 21, "#6610f2", "book"),
    ("Asset Taxonomy",        "Asset Taxonomy",              "DocType", 22, "#6c757d", "tag"),
    ("Completed Requests",    "Maintenance Request",         "DocType", 23, "#28a745", "check"),
    ("Settings",              "Asset Maintenance Settings",  "DocType", 24, "#6c757d", "setting"),
]

LINKS = [
    {"label":"Maintenance Operations","items":[
        {"name":"Maintenance Request",      "label":"Maintenance Request"},
        {"name":"Maintenance Work Order",   "label":"Work Order"},
        {"name":"Maintenance Work Log",     "label":"Work Log"},
        {"name":"Spare Part Consumption",   "label":"Spare Parts"},
        {"name":"Spare Part Request",       "label":"Spare Part Request"},
    ]},
    {"label":"Planning & PM","items":[
        {"name":"Maintenance Checklist",        "label":"PM Checklist"},
        {"name":"Maintenance SLA Policy",       "label":"SLA Policy"},
        {"name":"Maintenance Assignment Rule",  "label":"Assignment Rule"},
        {"name":"Maintenance Team",             "label":"Maintenance Team"},
        {"name":"Asset Maintenance Settings",   "label":"Settings"},
    ]},
    {"label":"Compliance & Contracts","items":[
        {"name":"Maintenance Inspection",    "label":"Inspection"},
        {"name":"Service Contract",          "label":"Service Contract"},
        {"name":"Asset Meter Reading",       "label":"Meter Reading"},
        {"name":"Maintenance Location",      "label":"Location"},
        {"name":"Asset Taxonomy",            "label":"Asset Taxonomy"},
    ]},
    {"label":"Knowledge","items":[
        {"name":"Maintenance Knowledge Base","label":"Knowledge Base"},
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
                    if label in ("Dashboard",):
                        link_to = "Maintenance Request"
                    elif label in ("Asset Uptime","MTTR & MTBF","PM Compliance","Pareto Analysis"):
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
        print("✅ Workspace v3.0 created")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AMP Workspace v3.0")
        print(f"❌ {e}")
