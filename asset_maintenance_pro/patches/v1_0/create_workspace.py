"""
Patch v1.0: Create Asset Maintenance Workspace safely.
- Only creates OUR workspace, never touches any other workspace
- Uses frappe.get_doc().insert() with ignore flags for safety
- Skips silently if workspace already exists
"""
import frappe
import json


SHORTCUTS = [
    ("Maintenance Request",   "Maintenance Request",        "DocType", 1),
    ("Maintenance Checklist", "Maintenance Checklist",      "DocType", 2),
    ("Work Logs",             "Maintenance Work Log",       "DocType", 3),
    ("Spare Parts",           "Spare Part Consumption",     "DocType", 4),
    ("Meter Readings",        "Asset Meter Reading",        "DocType", 5),
    ("Settings",              "Asset Maintenance Settings", "DocType", 6),
]

CONTENT = json.dumps([
    {"type": "header",   "data": {"text": "<h2>Asset Maintenance</h2>", "col": 12}},
    {"type": "shortcut", "data": {"shortcut_name": "Maintenance Request",   "col": 4}},
    {"type": "shortcut", "data": {"shortcut_name": "Maintenance Checklist", "col": 4}},
    {"type": "shortcut", "data": {"shortcut_name": "Work Logs",             "col": 4}},
    {"type": "shortcut", "data": {"shortcut_name": "Spare Parts",           "col": 4}},
    {"type": "shortcut", "data": {"shortcut_name": "Meter Readings",        "col": 4}},
    {"type": "shortcut", "data": {"shortcut_name": "Settings",              "col": 4}},
])

WS_NAME = "Asset Maintenance Pro"


def execute():
    if frappe.db.exists("Workspace", WS_NAME):
        return

    try:
        ws = frappe.new_doc("Workspace")
        ws.public = 1
        ws.content = CONTENT

        meta = frappe.get_meta("Workspace")
        field_names = {f.fieldname for f in meta.fields}

        if "label"       in field_names: ws.label       = "Asset Maintenance"
        if "title"       in field_names: ws.title       = "Asset Maintenance"
        if "module"      in field_names: ws.module      = "Asset Maintenance"
        if "category"    in field_names: ws.category    = "Modules"
        if "icon"        in field_names: ws.icon        = "tool"
        if "color"       in field_names: ws.color       = "#2490EF"
        if "sequence_id" in field_names: ws.sequence_id = 99.0
        if "is_standard" in field_names: ws.is_standard = 0

        if "shortcuts" in field_names:
            for label, link_to, stype, idx in SHORTCUTS:
                ws.append("shortcuts", {
                    "label": label, "link_to": link_to,
                    "type": stype, "idx": idx,
                })

        ws.flags.ignore_permissions = True
        ws.flags.ignore_mandatory   = True
        ws.flags.ignore_validate    = True
        ws.insert(set_name=WS_NAME)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(str(e), "Asset Maintenance Workspace Creation")
