"""Patch: Ensure Maintenance Period Report and TCO report exist with proper permissions."""
import frappe

REPORTS = [
    {
        "name": "Maintenance Period Report",
        "ref_doctype": "Maintenance Request",
        "module": "Asset Maintenance",
    },
    {
        "name": "TCO Analysis",
        "ref_doctype": "Asset",
        "module": "Asset Maintenance",
    },
]

ROLES = ["System Manager","Branch Manager","Maintenance Coordinator","Maintenance Technician"]

def execute():
    for r in REPORTS:
        if not frappe.db.exists("Report", r["name"]):
            continue
        # Ensure roles exist
        existing_roles = frappe.db.get_all("Has Role",
            filters={"parent": r["name"], "parenttype": "Report"},
            pluck="role")
        for role in ROLES:
            if role not in existing_roles and frappe.db.exists("Role", role):
                frappe.db.insert({"doctype": "Has Role",
                    "parent": r["name"], "parenttype": "Report",
                    "parentfield": "roles", "role": role})
    frappe.db.commit()
    print("✅ Report permissions ensured")
