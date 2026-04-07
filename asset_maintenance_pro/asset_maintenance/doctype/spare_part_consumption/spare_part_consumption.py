import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class SparePartConsumption(Document):

    def before_insert(self):
        self.consumed_by = frappe.session.user

    def validate(self):
        self._validate_request_status()
        self._calculate_amount()

    def _validate_request_status(self):
        status = frappe.db.get_value("Maintenance Request", self.maintenance_request, "status")
        if status in ("Completed", "Cancelled"):
            frappe.throw(
                _("Cannot add spare parts to a {0} Maintenance Request.").format(status)
            )

    def _calculate_amount(self):
        self.amount = flt(self.qty) * flt(self.rate)
