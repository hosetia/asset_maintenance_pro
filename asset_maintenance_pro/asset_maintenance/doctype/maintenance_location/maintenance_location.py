import frappe
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet


class MaintenanceLocation(NestedSet):
    nsm_parent_field = "parent_location"
