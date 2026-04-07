import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, flt

class SparePartRequest(Document):

    def before_insert(self):
        self.requested_by = frappe.session.user

    def validate(self):
        self._calculate_total()
        self._check_stock_availability()

    def _calculate_total(self):
        total = 0
        for item in self.items:
            item.amount = flt(item.qty) * flt(item.rate)
            total += item.amount
        self.total_amount = total

    def _check_stock_availability(self):
        for item in self.items:
            if item.warehouse and item.item_code:
                stock = frappe.db.get_value("Bin",
                    {"item_code": item.item_code, "warehouse": item.warehouse},
                    "actual_qty") or 0
                item.available_stock = flt(stock)

    def on_update(self):
        if self.status == "Approved":
            frappe.db.set_value(self.doctype, self.name, {
                "approved_by": frappe.session.user,
                "approved_on": now(),
            })
        elif self.status == "Issued from Stock":
            frappe.db.set_value(self.doctype, self.name, "issued_on", now())
            self._create_stock_entry()

    def _create_stock_entry(self):
        if not self.warehouse:
            return
        items = [{"item_code": i.item_code, "qty": i.qty, "uom": i.uom,
                  "s_warehouse": self.warehouse, "basic_rate": i.rate or 0}
                 for i in self.items if i.item_code]
        if not items:
            return
        try:
            se = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Issue",
                "purpose": "Material Issue",
                "remarks": f"Spare Part Request {self.name}",
                "items": items,
            })
            se.insert(ignore_permissions=True)
            se.submit()
            frappe.msgprint(f"Stock Entry {se.name} created.", indicator="green", alert=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Stock Entry failed for SPR {self.name}")
