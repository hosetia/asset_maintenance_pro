"""
Patch v1.0: Create the Maintenance Kanban Board using direct SQL.
Bypasses Frappe's naming/validation hooks that cause issues during migrate.
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

    # Insert the Kanban Board directly via SQL
    frappe.db.sql("""
        INSERT IGNORE INTO `tabKanban Board`
            (name, board_name, reference_doctype, field_name, filters,
             private, owner, creation, modified, modified_by, docstatus)
        VALUES
            (%(name)s, %(board_name)s, %(ref)s, %(field)s, %(filters)s,
             0, 'Administrator', %(ts)s, %(ts)s, 'Administrator', 0)
    """, {
        "name": "Maintenance Kanban",
        "board_name": "Maintenance Kanban",
        "ref": "Maintenance Request",
        "field": "kanban_column",
        "filters": '[["Maintenance Request","status","!=","Cancelled",false]]',
        "ts": ts,
    })

    # Insert columns
    for idx, (col_name, indicator) in enumerate(COLUMNS, start=1):
        frappe.db.sql("""
            INSERT IGNORE INTO `tabKanban Board Column`
                (name, parent, parenttype, parentfield, idx,
                 column_name, status, indicator, `order`,
                 owner, creation, modified, modified_by, docstatus)
            VALUES
                (%(name)s, 'Maintenance Kanban', 'Kanban Board', 'columns', %(idx)s,
                 %(col)s, 'Active', %(indicator)s, '[]',
                 'Administrator', %(ts)s, %(ts)s, 'Administrator', 0)
        """, {
            "name": f"Maintenance Kanban-{col_name}",
            "idx": idx,
            "col": col_name,
            "indicator": indicator,
            "ts": ts,
        })

    frappe.db.commit()
