"""
Permission hooks for Maintenance Request.

Branch Managers see only their branch.
Technicians see only requests assigned to them.
System Managers see everything.
"""

import frappe


def maintenance_request_query(user):
    """
    permission_query_conditions hook.
    Returns a SQL WHERE clause fragment for list views (frappe.get_list).
    """
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if "System Manager" in roles or "Administrator" == user:
        return ""  # See all

    if "Branch Manager" in roles:
        # Find the employee record for this user to get their branch
        employee = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"}, "branch")
        if employee:
            return "`tabMaintenance Request`.`branch` = {0}".format(
                frappe.db.escape(employee)
            )
        # Branch Manager with no employee record sees nothing
        return "1=0"

    if "Maintenance Technician" in roles:
        return "`tabMaintenance Request`.`assigned_to` = {0}".format(
            frappe.db.escape(user)
        )

    # All other roles: no access
    return "1=0"


def has_maintenance_request_permission(doc, user=None, permission_type=None):
    """
    has_permission hook.
    Returns True (allow), False (deny), or None (use default role permissions).
    """
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if "System Manager" in roles or user == "Administrator":
        return None  # Use default role permissions

    if "Branch Manager" in roles:
        employee_branch = frappe.db.get_value(
            "Employee", {"user_id": user, "status": "Active"}, "branch"
        )
        if doc.branch == employee_branch:
            return None
        return False

    if "Maintenance Technician" in roles:
        if permission_type == "write":
            # Technicians can only write to requests assigned to them
            return doc.assigned_to == user or None
        # Read: technicians can read requests assigned to them
        return doc.assigned_to == user or None

    return False
