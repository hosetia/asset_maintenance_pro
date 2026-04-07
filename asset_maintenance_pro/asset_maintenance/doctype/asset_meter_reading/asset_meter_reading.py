import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class AssetMeterReading(Document):

    def before_insert(self):
        self.recorded_by = frappe.session.user
        self._populate_previous_reading()

    def validate(self):
        self._validate_meter_value()
        self._calculate_delta()

    def _populate_previous_reading(self):
        prev = frappe.db.get_value(
            "Asset Meter Reading",
            filters={"asset": self.asset, "uom": self.uom},
            fieldname="meter_value",
            order_by="reading_date desc, creation desc",
        )
        self.previous_reading = flt(prev)

    def _validate_meter_value(self):
        if flt(self.meter_value) < flt(self.previous_reading):
            frappe.msgprint(
                _("Meter value {0} is less than previous reading {1}. Please verify.").format(
                    self.meter_value, self.previous_reading
                ),
                indicator="orange",
                alert=True,
            )

    def _calculate_delta(self):
        self.delta = flt(self.meter_value) - flt(self.previous_reading)
