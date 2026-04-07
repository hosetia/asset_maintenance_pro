import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, flt, time_diff_in_hours


WO_KANBAN_MAP = {
    "Ready": "Ready", "Scheduled Today": "Scheduled Today",
    "On Route": "On Route", "On Site": "On Site",
    "Repairing": "Repairing", "Testing": "Testing",
    "Completed": "Completed", "Manager Verification": "Manager Verification",
}


class MaintenanceWorkOrder(Document):

    def validate(self):
        self._validate_completion()
        self._calculate_hours()
        self._calculate_costs()
        self._sync_kanban()

    def on_update(self):
        old = self.get_doc_before_save()
        if old and old.status != self.status:
            self._handle_status_change(old.status)

    # ── Validation ────────────────────────────────────────────────────────────

    def _validate_completion(self):
        if self.status not in ("Completed", "Manager Verification", "Closed"):
            return
        errors = []
        if not self.actual_end:
            errors.append(_("Actual End time is required to complete a Work Order."))
        if not self.completion_photos:
            errors.append(_("Completion photo is required."))
        # Check mandatory tasks
        incomplete = [r.task for r in self.tasks if r.is_mandatory and not r.completed]
        if incomplete:
            errors.append(_("Incomplete mandatory tasks: {0}").format(", ".join(incomplete)))
        if self.is_closure_risk or self.is_food_safety_impact:
            if not self.root_cause_analysis:
                errors.append(_("Root Cause Analysis required for food safety/closure-risk issues."))
        if errors:
            frappe.throw("<br>".join(errors))

    def _calculate_hours(self):
        total = sum(flt(row.hours) for row in self.time_logs)
        self.total_hours = round(total, 2)
        if self.actual_start and self.actual_end:
            self.downtime_hours = round(
                time_diff_in_hours(self.actual_end, self.actual_start), 2
            )

    def _calculate_costs(self):
        # Labor cost from time logs (could link to salary/rate later)
        self.total_labor_cost = flt(self.total_hours) * 0  # placeholder
        # Parts cost from linked Spare Part Consumptions
        parts_cost = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0)
            FROM `tabSpare Part Consumption`
            WHERE maintenance_request = %s AND docstatus = 0
        """, self.maintenance_request)
        self.total_parts_cost = flt(parts_cost[0][0]) if parts_cost else 0
        self.total_cost = self.total_labor_cost + self.total_parts_cost

    def _sync_kanban(self):
        self.kanban_column = WO_KANBAN_MAP.get(self.status, "Ready")

    # ── Status Change ─────────────────────────────────────────────────────────

    def _handle_status_change(self, old_status):
        if self.status == "Completed":
            frappe.db.set_value(self.doctype, self.name, {
                "actual_end": self.actual_end or now(),
            })
            # Update linked Maintenance Request
            if self.maintenance_request:
                frappe.db.set_value(
                    "Maintenance Request", self.maintenance_request,
                    "status", "Awaiting Close"
                )
        elif self.status == "Closed":
            frappe.db.set_value(self.doctype, self.name, {
                "verified_by": frappe.session.user,
                "verified_on": now(),
            })

    # ── Whitelisted Methods ───────────────────────────────────────────────────

    @frappe.whitelist()
    def start_timer(self, technician=None):
        """Technician clicks Start — logs time entry."""
        tech = technician or frappe.session.user
        self.append("time_logs", {
            "technician": tech,
            "activity": "Repair",
            "from_time": now(),
        })
        if self.status in ("Ready", "Scheduled Today"):
            self.status = "On Site"
        if not self.actual_start:
            self.actual_start = now()
        self.save()
        return {"message": "Timer started"}

    @frappe.whitelist()
    def stop_timer(self, technician=None):
        """Technician clicks Stop — closes last open time entry."""
        tech = technician or frappe.session.user
        for row in reversed(self.time_logs):
            if row.technician == tech and row.from_time and not row.to_time:
                row.to_time = now()
                row.hours = round(time_diff_in_hours(row.to_time, row.from_time), 2)
                break
        self.save()
        return {"message": "Timer stopped"}
