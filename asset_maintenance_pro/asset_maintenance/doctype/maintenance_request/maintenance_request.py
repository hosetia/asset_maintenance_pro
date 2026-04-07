import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now, today, flt


KANBAN_STATUS_MAP = {
    "New": "New",
    "Assigned": "Assigned",
    "In Progress": "In Progress",
    "Waiting Parts": "Waiting Parts",
    "Awaiting Close": "Awaiting Close",
    "Completed": "Completed",
    "Cancelled": "Completed",
}

TECHNICIAN_ALLOWED_STATUSES = {
    "Assigned", "In Progress", "Waiting Parts", "Awaiting Close"
}


class MaintenanceRequest(Document):

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def before_insert(self):
        self.requested_by = frappe.session.user
        self.requested_on = now()
        self.kanban_column = self.status or "New"

    def validate(self):
        self._validate_branch_manager_scope()
        self._validate_technician_scope()
        self._validate_asset_branch_match()
        self._validate_completion_fields()
        self._sync_kanban_column()
        self._auto_stamp_checklist_items()

    def on_update(self):
        old = self.get_doc_before_save()
        if old and old.status != self.status:
            self._handle_status_change(old.status)

    def on_trash(self):
        if self.status == "Completed":
            frappe.throw(_("Cannot delete a Completed Maintenance Request."))

    # ─── Validation helpers ───────────────────────────────────────────────────

    def _validate_branch_manager_scope(self):
        """Branch Managers can only create/edit requests for their own branch."""
        roles = frappe.get_roles(frappe.session.user)
        if "Branch Manager" not in roles or "System Manager" in roles:
            return
        user_branch = frappe.db.get_value("Employee",
            {"user_id": frappe.session.user}, "branch")
        if user_branch and self.branch and self.branch != user_branch:
            frappe.throw(
                _("You can only create Maintenance Requests for your branch: {0}").format(user_branch)
            )

    def _validate_technician_scope(self):
        """Technicians can only update status and work logs, not reassign branch/asset."""
        roles = frappe.get_roles(frappe.session.user)
        if "Maintenance Technician" not in roles or "System Manager" in roles or "Branch Manager" in roles:
            return
        if self.status not in TECHNICIAN_ALLOWED_STATUSES and self.status != "Awaiting Close":
            if self.status == "Completed":
                frappe.throw(_("Only a Branch Manager or System Manager can mark as Completed."))

    def _validate_asset_branch_match(self):
        """Ensure the asset belongs to the selected branch."""
        if not self.asset or not self.branch:
            return
        asset_branch = frappe.db.get_value("Asset", self.asset, "branch")
        if asset_branch and asset_branch != self.branch:
            frappe.throw(
                _("Asset {0} belongs to branch {1}, not {2}.").format(
                    self.asset, asset_branch, self.branch
                )
            )

    def _validate_completion_fields(self):
        """On Completed status, total_cost and completion_image are mandatory."""
        if self.status != "Completed":
            return
        errors = []
        if not self.total_cost or flt(self.total_cost) <= 0:
            errors.append(_("Total Cost is required when completing a Maintenance Request."))
        if not self.completion_image:
            errors.append(_("Completion Image is required when completing a Maintenance Request."))
        # Check mandatory checklist items
        incomplete_mandatory = [
            row.task for row in self.checklist
            if row.is_mandatory and not row.completed
        ]
        if incomplete_mandatory:
            errors.append(
                _("Mandatory checklist items not completed: {0}").format(
                    ", ".join(incomplete_mandatory)
                )
            )
        if errors:
            frappe.throw("<br>".join(errors))

    def _sync_kanban_column(self):
        self.kanban_column = KANBAN_STATUS_MAP.get(self.status, "New")

    def _auto_stamp_checklist_items(self):
        for row in self.checklist:
            if row.completed and not row.completed_by:
                row.completed_by = frappe.session.user
                row.completed_on = now()
            elif not row.completed:
                row.completed_by = None
                row.completed_on = None

    # ─── Status change side effects ───────────────────────────────────────────

    def _handle_status_change(self, old_status):
        if self.status == "Completed":
            closed_on = now()
            # Calculate completion duration
            duration_hours = 0
            if self.requested_on:
                from frappe.utils import time_diff_in_hours
                duration_hours = round(time_diff_in_hours(closed_on, self.requested_on), 1)
            frappe.db.set_value(self.doctype, self.name, {
                "closed_by": frappe.session.user,
                "closed_on": closed_on,
                "completion_duration_hours": duration_hours,
            })
            self._update_asset_last_maintenance_date()
            self._create_stock_entry_for_spare_parts()
            self._send_completion_notification()
        self._send_status_change_notification(old_status)
        self._log_status_change(old_status)

    def _update_asset_last_maintenance_date(self):
        """Update Asset.last_maintenance_date (custom field added via fixture)."""
        try:
            frappe.db.set_value("Asset", self.asset, "custom_last_maintenance_date", today())
        except Exception:
            pass  # Custom field may not exist in all ERPNext versions

    def _create_stock_entry_for_spare_parts(self):
        """Auto-create a Stock Entry for spare parts consumed."""
        spare_parts = frappe.get_all(
            "Spare Part Consumption",
            filters={"maintenance_request": self.name, "docstatus": 0},
            fields=["item_code", "qty", "uom", "warehouse", "rate"]
        )
        if not spare_parts:
            return
        items = []
        for sp in spare_parts:
            if sp.item_code and sp.qty:
                items.append({
                    "item_code": sp.item_code,
                    "qty": sp.qty,
                    "uom": sp.uom or "Nos",
                    "s_warehouse": sp.warehouse,
                    "basic_rate": sp.rate or 0,
                })
        if not items:
            return
        try:
            se = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Issue",
                "purpose": "Material Issue",
                "remarks": _("Auto-generated for Maintenance Request {0}").format(self.name),
                "items": items,
            })
            se.insert(ignore_permissions=True)
            se.submit()
            frappe.msgprint(
                _("Stock Entry {0} created for spare parts.").format(
                    frappe.bold(se.name)
                ),
                indicator="green",
                alert=True,
            )
        except Exception as e:
            frappe.log_error(
                frappe.get_traceback(),
                _("Stock Entry creation failed for {0}").format(self.name)
            )

    def _send_status_change_notification(self, old_status):
        """Send in-app + email notification on status change."""
        from asset_maintenance_pro.asset_maintenance.notifications import (
            send_status_change_notification,
        )
        send_status_change_notification(self, old_status)

    def _send_completion_notification(self):
        try:
            from asset_maintenance_pro.asset_maintenance.notifications import send_completion_notification
            send_completion_notification(self)
        except Exception:
            pass

    def _log_status_change(self, old_status):
        """Write a Work Log entry automatically on status transitions."""
        try:
            wl = frappe.get_doc({
                "doctype": "Maintenance Work Log",
                "maintenance_request": self.name,
                "log_type": "Status Change",
                "description": _("Status changed from {0} to {1}").format(
                    old_status, self.status
                ),
                "logged_by": frappe.session.user,
                "log_datetime": now(),
            })
            wl.insert(ignore_permissions=True)
        except Exception:
            pass

    # ─── Whitelisted API methods ───────────────────────────────────────────────

    @frappe.whitelist()
    def transition_status(self, new_status):
        """Client-callable status transition with validation."""
        allowed = ["New", "Assigned", "In Progress", "Waiting Parts",
                   "Awaiting Close", "Completed", "Cancelled"]
        if new_status not in allowed:
            frappe.throw(_("Invalid status: {0}").format(new_status))
        self.status = new_status
        self.save()
        return {"status": self.status, "kanban_column": self.kanban_column}

    @frappe.whitelist()
    def get_work_logs(self):
        return frappe.get_all(
            "Maintenance Work Log",
            filters={"maintenance_request": self.name},
            fields=["name", "log_type", "description", "logged_by",
                    "log_datetime", "time_spent_hours"],
            order_by="log_datetime desc",
        )
