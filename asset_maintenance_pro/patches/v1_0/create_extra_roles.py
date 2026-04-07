"""Patch: Create extra roles - Maintenance Coordinator, Storekeeper."""
import frappe

ROLES = [
    {"name":"Maintenance Coordinator","desk_access":1,"is_custom":1},
    {"name":"Storekeeper","desk_access":1,"is_custom":1},
    {"name":"Branch Requester","desk_access":1,"is_custom":1},
]

def execute():
    for r in ROLES:
        if not frappe.db.exists("Role", r["name"]):
            doc = frappe.get_doc({"doctype":"Role", "role_name": r["name"], **r})
            doc.flags.ignore_permissions = True
            doc.insert()
    frappe.db.commit()
    print("✅ Extra roles created")
