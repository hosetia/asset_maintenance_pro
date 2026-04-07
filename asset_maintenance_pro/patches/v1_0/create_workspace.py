"""
Patch v1.0: Create full Asset Maintenance Pro Workspace.
Deletes and recreates to always stay up to date.
"""
import frappe
import json

WS_NAME = "Asset Maintenance Pro"

CONTENT = json.dumps([
    {"type": "header", "data": {"text": "<h2>🔧 Asset Maintenance Pro</h2>", "col": 12}},

    {"type": "header", "data": {"text": "<h4>📋 Transactions</h4>", "col": 12}},
    {"type": "shortcut", "data": {"shortcut_name": "Maintenance Request",   "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "New Request",           "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Work Logs",             "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Spare Parts",           "col": 3}},

    {"type": "header", "data": {"text": "<h4>⚙️ Masters & Configuration</h4>", "col": 12}},
    {"type": "shortcut", "data": {"shortcut_name": "Maintenance Checklist", "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Meter Readings",        "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "SLA Policies",          "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Assignment Rules",      "col": 3}},

    {"type": "header", "data": {"text": "<h4>📊 Reports & Analysis</h4>", "col": 12}},
    {"type": "shortcut", "data": {"shortcut_name": "Open Requests",         "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Overdue Requests",      "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Completed Requests",    "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Spare Part Usage",      "col": 3}},

    {"type": "header", "data": {"text": "<h4>🧠 Knowledge & Settings</h4>", "col": 12}},
    {"type": "shortcut", "data": {"shortcut_name": "Knowledge Base",        "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Asset Meter Readings",  "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Settings",              "col": 3}},
])

SHORTCUTS = [
    # label,                   link_to,                       type,      idx,  color,     icon
    ("Maintenance Request",    "Maintenance Request",         "DocType", 1,   "#2490EF", "tool"),
    ("New Request",            "Maintenance Request",         "DocType", 2,   "#28a745", "add"),
    ("Work Logs",              "Maintenance Work Log",        "DocType", 3,   "#fd7e14", "file"),
    ("Spare Parts",            "Spare Part Consumption",      "DocType", 4,   "#dc3545", "stock"),
    ("Maintenance Checklist",  "Maintenance Checklist",       "DocType", 5,   "#6f42c1", "list"),
    ("Meter Readings",         "Asset Meter Reading",         "DocType", 6,   "#17a2b8", "dashboard"),
    ("SLA Policies",           "Maintenance SLA Policy",      "DocType", 7,   "#e83e8c", "timer"),
    ("Assignment Rules",       "Maintenance Assignment Rule", "DocType", 8,   "#20c997", "assign"),
    ("Open Requests",          "Maintenance Request",         "DocType", 9,   "#2490EF", "list"),
    ("Overdue Requests",       "Maintenance Request",         "DocType", 10,  "#dc3545", "error"),
    ("Completed Requests",     "Maintenance Request",         "DocType", 11,  "#28a745", "check"),
    ("Spare Part Usage",       "Spare Part Consumption",      "DocType", 12,  "#fd7e14", "stock"),
    ("Knowledge Base",         "Maintenance Knowledge Base",  "DocType", 13,  "#6610f2", "book"),
    ("Asset Meter Readings",   "Asset Meter Reading",         "DocType", 14,  "#17a2b8", "dashboard"),
    ("Settings",               "Asset Maintenance Settings",  "DocType", 15,  "#6c757d", "setting"),
]

LINKS = [
    {
        "label": "Maintenance Transactions",
        "items": [
            {"name": "Maintenance Request",      "label": "Maintenance Request"},
            {"name": "Maintenance Work Log",     "label": "Work Log"},
            {"name": "Spare Part Consumption",   "label": "Spare Parts"},
        ]
    },
    {
        "label": "Planning & Configuration",
        "items": [
            {"name": "Maintenance Checklist",       "label": "Maintenance Checklist"},
            {"name": "Maintenance SLA Policy",      "label": "SLA Policy"},
            {"name": "Maintenance Assignment Rule", "label": "Assignment Rule"},
            {"name": "Asset Maintenance Settings",  "label": "Settings"},
        ]
    },
    {
        "label": "Readings & Knowledge",
        "items": [
            {"name": "Asset Meter Reading",         "label": "Meter Reading"},
            {"name": "Maintenance Knowledge Base",  "label": "Knowledge Base"},
        ]
    },
]


def execute():
    # Always delete and recreate to stay current
    if frappe.db.exists("Workspace", WS_NAME):
        frappe.delete_doc("Workspace", WS_NAME, ignore_permissions=True, force=True)
        frappe.db.commit()

    try:
        ws = frappe.new_doc("Workspace")
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

        # Shortcuts
        if "shortcuts" in field_names:
            sc_meta   = frappe.get_meta("Workspace Shortcut")
            sc_fields = {f.fieldname for f in sc_meta.fields}
            for label, link_to, stype, idx, color, icon in SHORTCUTS:
                row = {"label": label, "link_to": link_to, "type": stype, "idx": idx}
                if "color" in sc_fields: row["color"] = color
                if "icon"  in sc_fields: row["icon"]  = icon
                ws.append("shortcuts", row)

        # Links (card groups in Documents section)
        if "links" in field_names:
            lk_meta   = frappe.get_meta("Workspace Link")
            lk_fields = {f.fieldname for f in lk_meta.fields}
            for group in LINKS:
                ws.append("links", {"type": "Card Break", "label": group["label"], "hidden": 0})
                for item in group["items"]:
                    row = {"type": "Link", "hidden": 0}
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
        frappe.log_error(frappe.get_traceback(), "Asset Maintenance Workspace Creation")
        print(f"❌ Error: {e}")
