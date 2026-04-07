import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours


class WorkOrderTimeLog(Document):

    def validate(self):
        if self.from_time and self.to_time:
            self.hours = round(time_diff_in_hours(self.to_time, self.from_time), 2)
