"""
Patch v1.0: Create full Asset Maintenance Pro Workspace.
Complete workspace with shortcuts, links grouped by section,
and Kanban board link.
"""
import frappe
import json

WS_NAME = "Asset Maintenance Pro"

CONTENT = json.dumps([
    # ── Hero Header ──────────────────────────────────────────────────────────
    {
        "type": "header",
        "data": {"text": "<h2>🔧 Asset Maintenance Pro</h2>", "col": 12}
    },
    # ── Transactions ─────────────────────────────────────────────────────────
    {
        "type": "header",
        "data": {"text": "<h4>Transactions</h4>", "col": 12}
    },
    {"type": "shortcut", "data": {"shortcut_name": "Maintenance Request",   "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "New Request",           "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Kanban Board",          "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Work Logs",             "col": 3}},
    # ── Masters ──────────────────────────────────────────────────────────────
    {
        "type": "header",
        "data": {"text": "<h4>Masters & Configuration</h4>", "col": 12}
    },
    {"type": "shortcut", "data": {"shortcut_name": "Maintenance Checklist", "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Spare Parts",           "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Meter Readings",        "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Settings",              "col": 3}},
    # ── Reports ──────────────────────────────────────────────────────────────
    {
        "type": "header",
        "data": {"text": "<h4>Reports</h4>", "col": 12}
    },
    {"type": "shortcut", "data": {"shortcut_name": "Open Requests",         "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Overdue Requests",      "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Completed Requests",    "col": 3}},
    {"type": "shortcut", "data": {"shortcut_name": "Spare Part Usage",      "col": 3}},
    # ── Links Section ─────────────────────────────────────────────────────────
    {
        "type": "header",
        "data": {"text": "<h4>Documents</h4>", "col": 12}
    },
    {
        "type": "card",
        "data": {
            "card_name": "Maintenance",
            "col": 4
        }
    },
    {
        "type": "card",
        "data": {
            "card_name": "Configuration",
            "col": 4
        }
    },
    {
        "type": "card",
        "data": {
            "card_name": "Readings & Logs",
            "col": 4
        }
    },
])

SHORTCUTS = [
    # label, link_to, type, idx, color, icon, url
    ("Maintenance Request",   "Maintenance Request",        "DocType", 1,  "#2490EF", "tool",      None),
    ("New Request",           "Maintenance Request",        "DocType", 2,  "#28a745", "add",       None),
    ("Kanban Board",          "Maintenance Kanban",         "Page",    3,  "#6f42c1", "kanban",    "/app/maintenance-request?kanban=Maintenance%20Kanban"),
    ("Work Logs",             "Maintenance Work Log",       "DocType", 4,  "#fd7e14", "file",      None),
    ("Maintenance Checklist", "Maintenance Checklist",      "DocType", 5,  "#6f42c1", "list",      None),
    ("Spare Parts",           "Spare Part Consumption",     "DocType", 6,  "#dc3545", "stock",     None),
    ("Meter Readings",        "Asset Meter Reading",        "DocType", 7,  "#17a2b8", "dashboard", None),
    ("Settings",              "Asset Maintenance Settings", "DocType", 8,  "#6c757d", "setting",   None),
    # Report shortcuts (open List with filters)
    ("Open Requests",         "Maintenance Request",        "DocType", 9,  "#2490EF", "list",      None),
    ("Overdue Requests",      "Maintenance Request",        "DocType", 10, "#dc3545", "error",     None),
    ("Completed Requests",    "Maintenance Request",        "DocType", 11, "#28a745", "check",     None),
    ("Spare Part Usage",      "Spare Part Consumption",     "DocType", 12, "#fd7e14", "stock",     None),
]

LINKS = [
    {
        "label": "Maintenance",
        "items": [
            {"type": "DocType", "name": "Maintenance Request",   "label": "Maintenance Request"},
            {"type": "DocType", "name": "Maintenance Work Log",  "label": "Work Log"},
        ]
    },
    {
        "label": "Configuration",
        "items": [
            {"type": "DocType", "name": "Maintenance Checklist",      "label": "Maintenance Checklist"},
            {"type": "DocType", "name": "Spare Part Consumption",     "label": "Spare Parts"},
            {"type": "DocType", "name": "Asset Maintenance Settings", "label": "Settings"},
        ]
    },
    {
        "label": "Readings & Logs",
        "items": [
            {"type": "DocType", "name": "Asset Meter Reading", "label": "Meter Reading"},
        ]
    },
]


def execute():
    # Delete old version if exists to rebuild fresh
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
            for label, link_to, stype, idx, color, icon, url in SHORTCUTS:
                row = {"label": label, "link_to": link_to, "type": stype, "idx": idx}
                if "color" in sc_fields: row["color"] = color
                if "icon"  in sc_fields: row["icon"]  = icon
                if "url"   in sc_fields and url: row["url"] = url
                ws.append("shortcuts", row)

        # Links (card groups)
        if "links" in field_names:
            lk_meta   = frappe.get_meta("Workspace Link")
            lk_fields = {f.fieldname for f in lk_meta.fields}
            for group in LINKS:
                # Add group header
                ws.append("links", {
                    "type": "Card Break",
                    "label": group["label"],
                    "hidden": 0,
                })
                for item in group["items"]:
                    row = {
                        "type":   item["type"],
                        "hidden": 0,
                    }
                    if "link_to" in lk_fields: row["link_to"] = item["name"]
                    if "label"   in lk_fields: row["label"]   = item.get("label", item["name"])
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
