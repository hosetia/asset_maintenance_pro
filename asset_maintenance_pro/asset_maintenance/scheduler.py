"""
Scheduler tasks for Asset Maintenance Pro.

- generate_preventive_maintenance_requests: Daily long task
  Creates Maintenance Requests for assets whose preventive
  schedule is due (calendar-based or meter-based).

- send_overdue_notifications: Daily task
  Notifies stakeholders about overdue open requests.
"""

import frappe
from frappe import _
from frappe.utils import (
    add_days,
    date_diff,
    flt,
    getdate,
    nowdate,
    today,
)


def generate_preventive_maintenance_requests():
    """
    Daily long scheduler task.
    Iterates all active Maintenance Checklists and creates
    Maintenance Requests for eligible assets.
    """
    settings = frappe.get_single("Asset Maintenance Settings")
    if not settings.enable_preventive_scheduler:
        return

    lookahead = settings.scheduler_lookahead_days or 7
    generation_date = add_days(today(), lookahead)

    checklists = frappe.get_all(
        "Maintenance Checklist",
        filters={"is_active": 1},
        fields=[
            "name", "title", "asset_category", "trigger_type",
            "maintenance_interval_days", "meter_threshold", "meter_uom",
            "last_generated_date", "last_generated_meter_value",
            "advance_notice_days", "maintenance_type",
        ],
    )

    for checklist in checklists:
        try:
            _process_checklist(checklist, generation_date)
            frappe.db.commit()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                _("Preventive scheduler error for {0}").format(checklist.name)
            )
            frappe.db.rollback()


def send_overdue_notifications():
    """
    Daily scheduler task.
    Finds open requests past their due date and sends notifications.
    """
    settings = frappe.get_single("Asset Maintenance Settings")
    if not settings.notify_on_overdue:
        return

    threshold = settings.overdue_threshold_days or 3
    cutoff_date = add_days(today(), -threshold)

    overdue = frappe.get_all(
        "Maintenance Request",
        filters={
            "status": ["in", ["New", "Assigned", "In Progress", "Waiting Parts"]],
            "due_date": ["<", cutoff_date],
        },
        fields=["name", "asset", "branch", "assigned_to", "requested_by", "due_date", "status"],
    )

    from asset_maintenance_pro.asset_maintenance.notifications import send_overdue_notification

    for req in overdue:
        try:
            doc = frappe.get_doc("Maintenance Request", req.name)
            send_overdue_notification(doc)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                _("Overdue notification failed for {0}").format(req.name)
            )


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _process_checklist(checklist, generation_date):
    """Determine if a checklist should spawn new requests for its assets."""
    # Find all active assets matching this checklist's category
    filters = {"docstatus": 1, "disposal_date": ["is", "not set"]}
    if checklist.asset_category:
        filters["asset_category"] = checklist.asset_category

    assets = frappe.get_all("Asset", filters=filters, fields=["name", "branch"])

    for asset in assets:
        if not asset.branch:
            continue
        _maybe_create_request(asset, checklist, generation_date)


def _maybe_create_request(asset, checklist, generation_date):
    """
    Create a preventive Maintenance Request for an asset if the
    calendar or meter trigger threshold has been reached.
    """
    trigger = checklist.trigger_type

    calendar_due = False
    meter_due = False

    # ── Calendar trigger ──────────────────────────────────────────────────────
    if trigger in ("Calendar (Days)", "Both (whichever comes first)"):
        interval = checklist.maintenance_interval_days or 0
        if interval > 0:
            last_date = checklist.last_generated_date or getdate("1900-01-01")
            next_due = add_days(last_date, interval)
            if getdate(generation_date) >= getdate(next_due):
                calendar_due = True

    # ── Meter trigger ─────────────────────────────────────────────────────────
    if trigger in ("Meter Reading", "Both (whichever comes first)"):
        threshold = flt(checklist.meter_threshold)
        if threshold > 0:
            latest_reading = frappe.db.get_value(
                "Asset Meter Reading",
                filters={"asset": asset.name, "uom": checklist.meter_uom},
                fieldname="meter_value",
                order_by="reading_date desc, creation desc",
            )
            if latest_reading is not None:
                last_meter = flt(checklist.last_generated_meter_value)
                if flt(latest_reading) - last_meter >= threshold:
                    meter_due = True

    should_create = (
        (trigger == "Calendar (Days)" and calendar_due) or
        (trigger == "Meter Reading" and meter_due) or
        (trigger == "Both (whichever comes first)" and (calendar_due or meter_due))
    )

    if not should_create:
        return

    # Avoid duplicate open requests for same asset + checklist
    duplicate = frappe.db.exists("Maintenance Request", {
        "asset": asset.name,
        "preventive_schedule": checklist.name,
        "status": ["in", ["New", "Assigned", "In Progress", "Waiting Parts", "Awaiting Close"]],
    })
    if duplicate:
        return

    _create_preventive_request(asset, checklist)
    _update_checklist_tracking(checklist)


def _create_preventive_request(asset, checklist):
    """Insert a new preventive Maintenance Request."""
    # Clone checklist tasks into request checklist rows
    tasks = []
    for task in (checklist.get("tasks") or []):
        tasks.append({
            "task": task.task,
            "is_mandatory": task.is_mandatory,
        })

    mr = frappe.get_doc({
        "doctype": "Maintenance Request",
        "asset": asset.name,
        "branch": asset.branch,
        "maintenance_type": checklist.maintenance_type or "Preventive",
        "status": "New",
        "priority": "Medium",
        "request_type": "Preventive (Auto-generated)",
        "preventive_schedule": checklist.name,
        "description": _("Auto-generated preventive maintenance: {0}").format(checklist.title),
        "due_date": add_days(today(), checklist.advance_notice_days or 3),
        "checklist": tasks,
    })
    mr.flags.ignore_permissions = True
    mr.insert()

    from asset_maintenance_pro.asset_maintenance.notifications import send_new_request_notification
    send_new_request_notification(mr)


def _update_checklist_tracking(checklist):
    """Update last_generated_date and meter value on the checklist."""
    update = {"last_generated_date": today()}

    if checklist.trigger_type in ("Meter Reading", "Both (whichever comes first)"):
        # Get current meter value for any asset (use the first one found)
        reading = frappe.db.get_value(
            "Asset Meter Reading",
            filters={"uom": checklist.meter_uom},
            fieldname="meter_value",
            order_by="reading_date desc",
        )
        if reading is not None:
            update["last_generated_meter_value"] = flt(reading)

    frappe.db.set_value("Maintenance Checklist", checklist.name, update)
