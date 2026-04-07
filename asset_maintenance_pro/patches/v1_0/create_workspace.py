"""
Patch v1.0: Create Asset Maintenance Workspace.
Discovers actual DB columns first to avoid Unknown column errors.
"""
import frappe
import json
from frappe.utils import now


SHORTCUTS = [
    ("Maintenance Request",    "Maintenance Request",        "DocType", 1),
    ("Maintenance Checklist",  "Maintenance Checklist",      "DocType", 2),
    ("Work Logs",              "Maintenance Work Log",       "DocType", 3),
    ("Spare Parts",            "Spare Part Consumption",     "DocType", 4),
    ("Meter Readings",         "Asset Meter Reading",        "DocType", 5),
    ("Settings",               "Asset Maintenance Settings", "DocType", 6),
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


def _get_cols(table):
    return {r[0] for r in frappe.db.sql(f"SHOW COLUMNS FROM `{table}`")}


def execute():
    ts = now()

    # ── Discover actual Workspace columns ────────────────────────────────────
    ws_cols = _get_cols("tabWorkspace")

    # Mandatory columns that must exist in every Frappe version
    fields  = ["name", "owner", "creation", "modified", "modified_by", "docstatus"]
    values  = {
        "name":          WS_NAME,
        "owner":         "Administrator",
        "creation":      ts,
        "modified":      ts,
        "modified_by":   "Administrator",
        "docstatus":     0,
    }

    # Optional columns — add only if present in this installation
    optionals = {
        "label":       "Asset Maintenance",
        "title":       "Asset Maintenance",
        "module":      "Asset Maintenance",
        "category":    "Modules",
        "icon":        "tool",
        "color":       "#2490EF",
        "public":      1,
        "sequence_id": 99.0,
        "content":     CONTENT,
        "is_standard": 0,
        "for_user":    "",
    }
    for col, val in optionals.items():
        if col in ws_cols:
            fields.append(col)
            values[col] = val

    if frappe.db.exists("Workspace", WS_NAME):
        # Just make sure it's public and has content
        update = {}
        for col in ("public", "content", "is_standard"):
            if col in ws_cols:
                update[col] = optionals.get(col, "")
        if update:
            frappe.db.set_value("Workspace", WS_NAME, update)
    else:
        cols_sql = ", ".join(f"`{f}`" for f in fields)
        vals_sql = ", ".join(f"%({f})s" for f in fields)
        frappe.db.sql(
            f"INSERT IGNORE INTO `tabWorkspace` ({cols_sql}) VALUES ({vals_sql})",
            values
        )

    # ── Shortcuts ─────────────────────────────────────────────────────────────
    # Find shortcut child table
    shortcut_table = None
    for tbl in ("tabWorkspace Shortcut", "tabWorkspace Link"):
        try:
            frappe.db.sql(f"SELECT 1 FROM `{tbl}` LIMIT 1")
            shortcut_table = tbl
            break
        except Exception:
            continue

    if shortcut_table:
        sc_cols = _get_cols(shortcut_table)
        frappe.db.sql(f"DELETE FROM `{shortcut_table}` WHERE parent = %s", WS_NAME)

        for label, link_to, link_type, idx in SHORTCUTS:
            sc_fields = ["name", "parent", "parenttype", "parentfield",
                         "idx", "owner", "creation", "modified", "modified_by", "docstatus"]
            sc_values = {
                "name":        f"{WS_NAME}-SC-{idx}",
                "parent":      WS_NAME,
                "parenttype":  "Workspace",
                "parentfield": "shortcuts",
                "idx":         idx,
                "owner":       "Administrator",
                "creation":    ts,
                "modified":    ts,
                "modified_by": "Administrator",
                "docstatus":   0,
            }
            for opt, val in {"label": label, "link_to": link_to, "type": link_type}.items():
                if opt in sc_cols:
                    sc_fields.append(opt)
                    sc_values[opt] = val

            c = ", ".join(f"`{f}`" for f in sc_fields)
            v = ", ".join(f"%({f})s" for f in sc_fields)
            frappe.db.sql(
                f"INSERT IGNORE INTO `{shortcut_table}` ({c}) VALUES ({v})",
                sc_values
            )

    frappe.db.commit()
