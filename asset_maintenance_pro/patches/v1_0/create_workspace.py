"""
Patch v1.0: Create Asset Maintenance Workspace via direct SQL insert.
Runs after fixtures to guarantee the workspace exists.
"""
import frappe
import json
from frappe.utils import now


SHORTCUTS = [
    ("Maintenance Request",       "Maintenance Request",       "DocType", 1),
    ("Maintenance Checklist",     "Maintenance Checklist",     "DocType", 2),
    ("Work Logs",                 "Maintenance Work Log",      "DocType", 3),
    ("Spare Parts",               "Spare Part Consumption",    "DocType", 4),
    ("Meter Readings",            "Asset Meter Reading",       "DocType", 5),
    ("Settings",                  "Asset Maintenance Settings","DocType", 6),
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


def execute():
    ts = now()
    ws_name = "Asset Maintenance Pro"

    # Detect available columns in tabWorkspace
    ws_cols = {r[0] for r in frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`")}

    if frappe.db.exists("Workspace", ws_name):
        # Update existing to make sure it's public
        frappe.db.set_value("Workspace", ws_name, {
            "public": 1,
            "is_standard": 0,
        })
    else:
        fields = ["name", "owner", "creation", "modified", "modified_by",
                  "docstatus", "module", "is_standard", "public", "content"]
        values = {
            "name": ws_name,
            "owner": "Administrator",
            "creation": ts,
            "modified": ts,
            "modified_by": "Administrator",
            "docstatus": 0,
            "module": "Asset Maintenance",
            "is_standard": 0,
            "public": 1,
            "content": CONTENT,
        }

        for optional in ("label", "title"):
            if optional in ws_cols:
                fields.append(optional)
                values[optional] = "Asset Maintenance"

        for optional in ("icon",):
            if optional in ws_cols:
                fields.append(optional)
                values[optional] = "tool"

        for optional in ("color",):
            if optional in ws_cols:
                fields.append(optional)
                values[optional] = "#2490EF"

        for optional in ("category",):
            if optional in ws_cols:
                fields.append(optional)
                values[optional] = "Modules"

        for optional in ("sequence_id",):
            if optional in ws_cols:
                fields.append(optional)
                values[optional] = 99.0

        cols_sql = ", ".join(f"`{f}`" for f in fields)
        vals_sql = ", ".join(f"%({f})s" for f in fields)
        frappe.db.sql(
            f"INSERT IGNORE INTO `tabWorkspace` ({cols_sql}) VALUES ({vals_sql})",
            values
        )

    # Detect Workspace Shortcut table name
    shortcut_table = None
    for tbl in ("tabWorkspace Shortcut", "tabWorkspace Link"):
        try:
            frappe.db.sql(f"SELECT 1 FROM `{tbl}` LIMIT 1")
            shortcut_table = tbl
            break
        except Exception:
            continue

    if shortcut_table:
        sc_cols = {r[0] for r in frappe.db.sql(f"SHOW COLUMNS FROM `{shortcut_table}`")}
        # Clear old shortcuts for this workspace
        frappe.db.sql(
            f"DELETE FROM `{shortcut_table}` WHERE parent = %s",
            ws_name
        )
        for label, link_to, link_type, idx in SHORTCUTS:
            sc_fields = ["name", "parent", "parenttype", "parentfield",
                         "idx", "owner", "creation", "modified", "modified_by", "docstatus"]
            sc_values = {
                "name": f"{ws_name}-SC-{idx}",
                "parent": ws_name,
                "parenttype": "Workspace",
                "parentfield": "shortcuts",
                "idx": idx,
                "owner": "Administrator",
                "creation": ts,
                "modified": ts,
                "modified_by": "Administrator",
                "docstatus": 0,
            }
            for opt in ("label",):
                if opt in sc_cols:
                    sc_fields.append(opt)
                    sc_values[opt] = label
            for opt in ("link_to",):
                if opt in sc_cols:
                    sc_fields.append(opt)
                    sc_values[opt] = link_to
            for opt in ("type",):
                if opt in sc_cols:
                    sc_fields.append(opt)
                    sc_values[opt] = link_type

            c = ", ".join(f"`{f}`" for f in sc_fields)
            v = ", ".join(f"%({f})s" for f in sc_fields)
            frappe.db.sql(
                f"INSERT IGNORE INTO `{shortcut_table}` ({c}) VALUES ({v})",
                sc_values
            )

    frappe.db.commit()
