import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, today, add_days


class ServiceContract(Document):

    def validate(self):
        self._update_status()
        self._update_visits_remaining()

    def _update_status(self):
        if self.status in ("Cancelled", "Draft"):
            return
        days_to_expiry = date_diff(self.end_date, today())
        if days_to_expiry < 0:
            self.status = "Expired"
        elif days_to_expiry <= (self.renewal_reminder_days or 30):
            self.status = "Expiring Soon"
        else:
            self.status = "Active"

    def _update_visits_remaining(self):
        if self.included_visits_per_year:
            self.visits_remaining = max(0, (self.included_visits_per_year or 0) - (self.visits_used or 0))
