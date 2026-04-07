"""
Patch v1.0: Create the Maintenance Kanban Board using direct SQL.
Detects actual DB columns to support different Frappe versions.
"""
import frappe
from frappe.utils import now


COLUMNS = [
    ("New",            "Blue"),
    ("Assigned",       "Orange"),
    ("In Progress",    "Yellow"),
    ("Waiting Parts",  "Red"),
    ("Awaiting Close", "Purple"),
    ("Completed",      "Green"),
]


def execute():
    if frappe.db.exists("Kanban Board", "Maintenance Kanban"):
        return  # Already created

    ts = now()

    # Detect actual columns in tabKanban Board
    actual_cols = {
        row[0]
        for row in frappe.db.sql("SHOW COLUMNS FROM `tabKanban Board`")
    }

    # Build INSERT dynamically based on what columns exist
    base_fields = ["name", "reference_doctype", "field_name", "filters",
                   "private", "owner", "creation", "modified", "modified_by", "docstatus"]
    base_values = {
        "name": "Maintenance Kanban",
        "reference_doctype": "Maintenance Request",
        "field_name": "kanban_column",
        "filters": '[["Maintenance Request","status","!=","Cancelled",false]]',
        "private": 0,
        "owner": "Administrator",
        "creation": ts,
        "modified": ts,
        "modified_by": "Administrator",
        "docstatus": 0,
    }

    # Add optional fields only if they exist in this Frappe version
    for optional in ("board_name", "kanban_board_name"):
        if optional in actual_cols:
            base_fields.append(optional)
            base_values[optional] = "Maintenance Kanban"

    cols_sql = ", ".join(f"`{f}`" for f in base_fields)
    vals_sql = ", ".join(f"%({f})s" for f in base_fields)

    frappe.db.sql(
        f"INSERT IGNORE INTO `tabKanban Board` ({cols_sql}) VALUES ({vals_sql})",
        base_values
    )

    # Insert columns
    col_actual = {
        row[0]
        for row in frappe.db.sql("SHOW COLUMNS FROM `tabKanban Board Column`")
    }

    for idx, (col_name, indicator) in enumerate(COLUMNS, start=1):
        col_fields = ["name", "parent", "parenttype", "parentfield", "idx",
                      "column_name", "status", "indicator", "owner",
                      "creation", "modified", "modified_by", "docstatus"]
        col_values = {
            "name": f"MNT-KB-{idx}-{col_name[:3].replace(' ', '')}",
            "parent": "Maintenance Kanban",
            "parenttype": "Kanban Board",
            "parentfield": "columns",
            "idx": idx,
            "column_name": col_name,
            "status": "Active",
            "indicator": indicator,
            "owner": "Administrator",
            "creation": ts,
            "modified": ts,
            "modified_by": "Administrator",
            "docstatus": 0,
        }
        if "order" in col_actual:
            col_fields.append("order")
            col_values["order"] = "[]"

        c_cols = ", ".join(f"`{f}`" for f in col_fields)
        c_vals = ", ".join(f"%({f})s" for f in col_fields)
        frappe.db.sql(
            f"INSERT IGNORE INTO `tabKanban Board Column` ({c_cols}) VALUES ({c_vals})",
            col_values
        )

    frappe.db.commit()
