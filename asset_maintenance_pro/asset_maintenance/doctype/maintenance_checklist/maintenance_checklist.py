import frappe
from frappe import _
from frappe.model.document import Document


class MaintenanceChecklist(Document):

    def validate(self):
        self._validate_trigger_fields()

    def _validate_trigger_fields(self):
        if self.trigger_type in ("Calendar (Days)", "Both (whichever comes first)"):
            if not self.maintenance_interval_days or self.maintenance_interval_days <= 0:
                frappe.throw(_("Interval (Days) must be set for Calendar-based trigger."))
        if self.trigger_type in ("Meter Reading", "Both (whichever comes first)"):
            if not self.meter_threshold or self.meter_threshold <= 0:
                frappe.throw(_("Meter Threshold must be set for Meter Reading trigger."))
            if not self.meter_uom:
                frappe.throw(_("Meter UOM is required for Meter Reading trigger."))
