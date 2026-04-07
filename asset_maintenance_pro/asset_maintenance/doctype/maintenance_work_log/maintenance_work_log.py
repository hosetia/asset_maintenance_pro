import frappe
from frappe import _
from frappe.model.document import Document


class MaintenanceWorkLog(Document):

    def before_insert(self):
        self.logged_by = frappe.session.user

    def validate(self):
        self._validate_technician_ownership()

    def _validate_technician_ownership(self):
        roles = frappe.get_roles(frappe.session.user)
        if "System Manager" in roles or "Branch Manager" in roles:
            return
        # Technicians can only log against requests assigned to them
        assigned = frappe.db.get_value(
            "Maintenance Request", self.maintenance_request, "assigned_to"
        )
        if assigned and assigned != frappe.session.user:
            frappe.throw(
                _("You can only add work logs to Maintenance Requests assigned to you.")
            )
