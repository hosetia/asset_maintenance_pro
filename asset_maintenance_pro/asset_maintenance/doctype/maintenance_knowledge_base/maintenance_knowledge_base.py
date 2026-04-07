import frappe
from frappe.model.document import Document


class MaintenanceKnowledgeBase(Document):

    def before_insert(self):
        self.author = frappe.session.user

    def on_update(self):
        if self.is_published and not self.published_on:
            self.db_set("published_on", frappe.utils.today())
