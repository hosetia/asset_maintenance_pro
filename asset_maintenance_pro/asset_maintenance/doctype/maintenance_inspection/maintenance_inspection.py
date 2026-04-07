import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now


class MaintenanceInspection(Document):

    def before_insert(self):
        self.inspected_by = frappe.session.user

    def validate(self):
        self._calculate_results()
        self._auto_overall_result()

    def _calculate_results(self):
        passed = failed = critical = 0
        for item in self.items:
            if item.result == "Pass":
                passed += 1
            elif item.result == "Fail":
                failed += 1
                if item.is_critical:
                    critical += 1
        self.passed_count   = passed
        self.failed_count   = failed
        self.critical_failures = critical

    def _auto_overall_result(self):
        if not self.items:
            return
        if self.critical_failures and self.critical_failures > 0:
            self.overall_result = "Fail"
            self.status = "Failed"
        elif self.failed_count and self.failed_count > 0:
            self.overall_result = "Conditional Pass"
        elif self.passed_count and self.passed_count > 0:
            self.overall_result = "Pass"
            self.status = "Passed"

    def on_update(self):
        if self.overall_result == "Fail" and self.corrective_action_required:
            self._create_maintenance_request()

    def _create_maintenance_request(self):
        """Auto-create a Maintenance Request for failed critical inspections."""
        if frappe.db.exists("Maintenance Request", {
            "description": ["like", f"%Inspection {self.name}%"],
            "status": ["in", ["New", "Assigned", "In Progress"]]
        }):
            return
        mr = frappe.get_doc({
            "doctype": "Maintenance Request",
            "asset": self.asset,
            "branch": self.branch,
            "maintenance_type": "Corrective",
            "priority": "High",
            "status": "New",
            "description": _(
                "Failed {0} Inspection {1}. Critical failures: {2}. "
                "See findings: {3}"
            ).format(
                self.inspection_type, self.name,
                self.critical_failures, self.findings or ""
            ),
        })
        mr.flags.ignore_permissions = True
        mr.insert()
        frappe.msgprint(
            _("Maintenance Request {0} created for failed inspection.").format(
                frappe.bold(mr.name)
            ),
            indicator="orange", alert=True
        )
