"""
Patch v1.0: Create the Maintenance Kanban Board programmatically.
Using a patch instead of fixture avoids the get_order_for_column IndexError
that occurs when Frappe tries to parse empty filters on Kanban Board insert.
"""
import frappe


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

    # Build column rows
    columns = []
    for col_name, indicator in COLUMNS:
        columns.append({
            "doctype": "Kanban Board Column",
            "column_name": col_name,
            "status": "Active",
            "indicator": indicator,
            "order": "[]",
        })

    kb = frappe.get_doc({
        "doctype": "Kanban Board",
        "name": "Maintenance Kanban",
        "reference_doctype": "Maintenance Request",
        "field_name": "kanban_column",
        "filters": '[["Maintenance Request","status","!=","Cancelled",false]]',
        "private": 0,
        "columns": columns,
    })
    kb.flags.ignore_permissions = True
    kb.flags.ignore_mandatory = True
    kb.insert()
    frappe.db.commit()
