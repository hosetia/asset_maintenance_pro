"""
Scheduler tasks for Asset Maintenance Pro.
- generate_preventive_maintenance_requests: Daily long
- send_overdue_notifications: Daily
- run_sla_escalations: Hourly
- update_technician_load_counts: Daily
- auto_assign_new_requests: Every 30 min
"""
import frappe
from frappe import _
from frappe.utils import add_days, date_diff, flt, getdate, now, nowdate, today


# ══════════════════════════════════════════════════════════════════════════════
# PREVENTIVE MAINTENANCE GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_preventive_maintenance_requests():
    settings = frappe.get_single("Asset Maintenance Settings")
    if not settings.enable_preventive_scheduler:
        return

    lookahead = settings.scheduler_lookahead_days or 7
    generation_date = add_days(today(), lookahead)

    checklists = frappe.get_all(
        "Maintenance Checklist", filters={"is_active": 1},
        fields=["name","title","asset_category","trigger_type",
                "maintenance_interval_days","meter_threshold","meter_uom",
                "last_generated_date","last_generated_meter_value",
                "advance_notice_days","maintenance_type"],
    )
    for checklist in checklists:
        try:
            _process_checklist(checklist, generation_date)
            frappe.db.commit()
        except Exception:
            frappe.log_error(frappe.get_traceback(),
                             f"Preventive scheduler error: {checklist.name}")
            frappe.db.rollback()


def _process_checklist(checklist, generation_date):
    filters = {"docstatus": 1, "disposal_date": ["is", "not set"]}
    if checklist.asset_category:
        filters["asset_category"] = checklist.asset_category
    assets = frappe.get_all("Asset", filters=filters, fields=["name","branch"])
    for asset in assets:
        if asset.branch:
            _maybe_create_request(asset, checklist, generation_date)


def _maybe_create_request(asset, checklist, generation_date):
    trigger = checklist.trigger_type
    calendar_due = False
    meter_due    = False

    if trigger in ("Calendar (Days)", "Both (whichever comes first)"):
        interval  = checklist.maintenance_interval_days or 0
        if interval > 0:
            last_date = checklist.last_generated_date or getdate("1900-01-01")
            next_due  = add_days(last_date, interval)
            if getdate(generation_date) >= getdate(next_due):
                calendar_due = True

    if trigger in ("Meter Reading", "Both (whichever comes first)"):
        threshold = flt(checklist.meter_threshold)
        if threshold > 0:
            latest = frappe.db.get_value(
                "Asset Meter Reading",
                filters={"asset": asset.name, "uom": checklist.meter_uom},
                fieldname="meter_value", order_by="reading_date desc",
            )
            if latest is not None:
                if flt(latest) - flt(checklist.last_generated_meter_value) >= threshold:
                    meter_due = True

    should_create = (
        (trigger == "Calendar (Days)"            and calendar_due) or
        (trigger == "Meter Reading"              and meter_due)    or
        (trigger == "Both (whichever comes first)" and (calendar_due or meter_due))
    )
    if not should_create:
        return

    duplicate = frappe.db.exists("Maintenance Request", {
        "asset": asset.name,
        "preventive_schedule": checklist.name,
        "status": ["in", ["New","Assigned","In Progress","Waiting Parts","Awaiting Close"]],
    })
    if duplicate:
        return

    _create_preventive_request(asset, checklist)
    _update_checklist_tracking(checklist)


def _create_preventive_request(asset, checklist):
    tasks = []
    for task in (checklist.get("tasks") or []):
        tasks.append({"task": task.task, "is_mandatory": task.is_mandatory})

    mr = frappe.get_doc({
        "doctype": "Maintenance Request",
        "asset":    asset.name,
        "branch":   asset.branch,
        "maintenance_type": checklist.maintenance_type or "Preventive",
        "status":   "New",
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
    update = {"last_generated_date": today()}
    if checklist.trigger_type in ("Meter Reading", "Both (whichever comes first)"):
        reading = frappe.db.get_value(
            "Asset Meter Reading",
            filters={"uom": checklist.meter_uom},
            fieldname="meter_value", order_by="reading_date desc",
        )
        if reading is not None:
            update["last_generated_meter_value"] = flt(reading)
    frappe.db.set_value("Maintenance Checklist", checklist.name, update)


# ══════════════════════════════════════════════════════════════════════════════
# SLA ESCALATION
# ══════════════════════════════════════════════════════════════════════════════

def run_sla_escalations():
    """Hourly: escalate overdue requests to manager."""
    settings = frappe.get_single("Asset Maintenance Settings")
    open_statuses = ["New", "Assigned", "In Progress", "Waiting Parts", "Awaiting Close"]

    overdue = frappe.get_all(
        "Maintenance Request",
        filters={
            "status": ["in", open_statuses],
            "due_date": ["<", today()],
        },
        fields=["name","asset","branch","assigned_to","requested_by","due_date",
                "status","priority","maintenance_type"],
    )

    from asset_maintenance_pro.asset_maintenance.notifications import send_overdue_notification

    for req in overdue:
        try:
            doc = frappe.get_doc("Maintenance Request", req.name)

            # Check SLA policy for escalation
            from asset_maintenance_pro.asset_maintenance.doctype.maintenance_sla_policy.maintenance_sla_policy import get_sla_for_request
            policy = get_sla_for_request(doc.priority, doc.maintenance_type)

            if policy and policy.escalate_to:
                days_overdue = abs(date_diff(doc.due_date, today()))
                escalate_after = (policy.escalation_after_hours or 24) / 24  # convert to days

                if days_overdue >= escalate_after:
                    _escalate_to_manager(doc, policy.escalate_to)

            send_overdue_notification(doc)
        except Exception:
            frappe.log_error(frappe.get_traceback(),
                             f"SLA Escalation failed for {req.name}")


def _escalate_to_manager(doc, escalate_to):
    """Send escalation notification to manager."""
    from asset_maintenance_pro.asset_maintenance.notifications import _send_email, _send_inapp
    subject = _(f"🚨 ESCALATION: Maintenance Request {doc.name} is overdue")
    message = f"""
    <p>This maintenance request requires your immediate attention:</p>
    <ul>
        <li><b>Request:</b> {doc.name}</li>
        <li><b>Asset:</b> {doc.asset}</li>
        <li><b>Branch:</b> {doc.branch}</li>
        <li><b>Priority:</b> {doc.priority}</li>
        <li><b>Due Date:</b> {doc.due_date}</li>
        <li><b>Status:</b> {doc.status}</li>
        <li><b>Assigned To:</b> {doc.assigned_to or 'Unassigned'}</li>
    </ul>
    <p>Please take immediate action.</p>
    """
    _send_inapp(escalate_to, subject, message, doc)
    _send_email(escalate_to, subject, message)


# ══════════════════════════════════════════════════════════════════════════════
# AUTO ASSIGNMENT
# ══════════════════════════════════════════════════════════════════════════════

def auto_assign_new_requests():
    """Every 30 min: auto-assign 'New' requests that have no assignee."""
    new_requests = frappe.get_all(
        "Maintenance Request",
        filters={"status": "New", "assigned_to": ["is", "not set"]},
        fields=["name", "branch", "maintenance_type", "priority"],
        limit_page_length=50,
    )

    for req in new_requests:
        try:
            from asset_maintenance_pro.api import get_suggested_technician
            result = get_suggested_technician(req.branch, req.maintenance_type)
            if result and result.get("user"):
                frappe.db.set_value("Maintenance Request", req.name, {
                    "assigned_to": result["user"],
                    "status": "Assigned",
                })
                frappe.db.commit()
        except Exception:
            frappe.log_error(frappe.get_traceback(),
                             f"Auto-assign failed for {req.name}")


# ══════════════════════════════════════════════════════════════════════════════
# UPDATE TECHNICIAN LOAD
# ══════════════════════════════════════════════════════════════════════════════

def update_technician_load_counts():
    """Daily: update current_load_count in Assignment Rules."""
    rules = frappe.get_all(
        "Maintenance Assignment Rule",
        filters={"is_active": 1},
        fields=["name", "assigned_technician"],
    )
    for rule in rules:
        load = frappe.db.count("Maintenance Request", {
            "assigned_to": rule.assigned_technician,
            "status": ["in", ["New","Assigned","In Progress","Waiting Parts","Awaiting Close"]],
        })
        frappe.db.set_value("Maintenance Assignment Rule", rule.name, "current_load_count", load)
    frappe.db.commit()


# ══════════════════════════════════════════════════════════════════════════════
# OVERDUE NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

def send_overdue_notifications():
    """Daily: notify about overdue requests."""
    settings = frappe.get_single("Asset Maintenance Settings")
    if not settings.notify_on_overdue:
        return

    threshold  = settings.overdue_threshold_days or 3
    cutoff_date = add_days(today(), -threshold)

    overdue = frappe.get_all(
        "Maintenance Request",
        filters={
            "status": ["in", ["New","Assigned","In Progress","Waiting Parts"]],
            "due_date": ["<", cutoff_date],
        },
        fields=["name","asset","branch","assigned_to","requested_by","due_date","status"],
    )

    from asset_maintenance_pro.asset_maintenance.notifications import send_overdue_notification
    for req in overdue:
        try:
            doc = frappe.get_doc("Maintenance Request", req.name)
            send_overdue_notification(doc)
        except Exception:
            frappe.log_error(frappe.get_traceback(),
                             f"Overdue notification failed: {req.name}")
