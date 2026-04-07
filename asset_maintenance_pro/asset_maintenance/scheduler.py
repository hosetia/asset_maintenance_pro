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


# ══════════════════════════════════════════════════════════════════════════════
# ASSET METRICS UPDATE (MTTR / MTBF)
# ══════════════════════════════════════════════════════════════════════════════

def update_asset_metrics():
    """Daily: recalculate MTTR and MTBF for all assets with work orders."""
    assets = frappe.get_all("Asset", pluck="name")
    for asset in assets:
        try:
            _recalc_asset_metrics(asset)
        except Exception:
            pass
    frappe.db.commit()


def _recalc_asset_metrics(asset):
    rows = frappe.db.sql("""
        SELECT COUNT(*) AS cnt,
               SUM(COALESCE(downtime_hours,0)) AS total_downtime,
               DATEDIFF(MAX(creation), MIN(creation)) AS span_days
        FROM `tabMaintenance Work Order`
        WHERE asset = %s AND status IN ('Completed','Closed') AND work_order_type='Corrective'
    """, asset, as_dict=True)
    if not rows or not rows[0].cnt:
        return
    r = rows[0]
    cnt = r.cnt or 1
    mttr = round(flt(r.total_downtime) / cnt, 2)
    mtbf = round((r.span_days or 1) / cnt, 1)
    frappe.db.set_value("Asset", asset, {
        "custom_mttr_hours": mttr,
        "custom_mtbf_days":  mtbf,
    })


# ══════════════════════════════════════════════════════════════════════════════
# WARRANTY + CONTRACT EXPIRY CHECKS
# ══════════════════════════════════════════════════════════════════════════════

def check_warranty_expiry():
    """Daily: alert for assets with warranty expiring in 30/60/90 days."""
    from asset_maintenance_pro.asset_maintenance.notifications import _send_inapp, _send_email
    thresholds = [30, 60, 90]
    for days in thresholds:
        expiring = frappe.db.sql(f"""
            SELECT name, asset_name, branch, custom_warranty_end
            FROM `tabAsset`
            WHERE custom_warranty_end IS NOT NULL
              AND DATEDIFF(custom_warranty_end, CURDATE()) = {days}
        """, as_dict=True)
        for asset in expiring:
            subject = f"⚠️ Warranty expiring in {days} days: {asset.asset_name}"
            message = f"<p>Asset <b>{asset.asset_name}</b> warranty expires on <b>{asset.custom_warranty_end}</b>.</p>"
            managers = _get_branch_managers(asset.branch)
            for user in managers:
                _send_inapp(user, subject, message, frappe._dict({"name": asset.name, "doctype": "Asset"}))
                _send_email(user, subject, message)


def check_contract_expiry():
    """Daily: check service contracts expiring soon."""
    contracts = frappe.get_all("Service Contract",
        filters={"status": ["in", ["Active", "Expiring Soon"]]},
        fields=["name", "contract_name", "vendor", "end_date", "renewal_reminder_days", "alert_sent"]
    )
    for c in contracts:
        days = date_diff(c.end_date, today())
        threshold = c.renewal_reminder_days or 30
        if 0 < days <= threshold and not c.alert_sent:
            frappe.db.set_value("Service Contract", c.name, "status", "Expiring Soon")
            frappe.db.set_value("Service Contract", c.name, "alert_sent", 1)


# ══════════════════════════════════════════════════════════════════════════════
# PM REMINDERS
# ══════════════════════════════════════════════════════════════════════════════

def send_pm_reminders():
    """Daily: send weekly PM plan reminder."""
    from frappe.utils import get_weekday
    if get_weekday() != "Sunday":
        return  # Only send on Sundays
    upcoming = frappe.get_all("Maintenance Request",
        filters={
            "request_type": "Preventive (Auto-generated)",
            "status": ["in", ["New", "Assigned"]],
            "due_date": ["between", [today(), add_days(today(), 7)]],
        },
        fields=["name", "asset", "branch", "due_date", "assigned_to"]
    )
    if not upcoming:
        return
    from asset_maintenance_pro.asset_maintenance.notifications import _send_email
    msg = "<p>Upcoming PM tasks this week:</p><ul>"
    for r in upcoming:
        msg += f"<li>{r.asset} — Due: {r.due_date} — {r.name}</li>"
    msg += "</ul>"
    subject = f"📋 {len(upcoming)} PM tasks due this week"
    # Send to all coordinators/managers
    users = frappe.get_all("User",
        filters={"enabled": 1, "name": ["in",
            frappe.db.sql("SELECT DISTINCT parent FROM `tabHas Role` WHERE role IN ('Branch Manager','Maintenance Coordinator')", pluck=True)
        ]},
        pluck="name", limit=20
    )
    for user in users:
        try:
            _send_email(user, subject, msg)
        except Exception:
            pass


def _get_branch_managers(branch):
    if not branch:
        return []
    employees = frappe.get_all("Employee",
        filters={"branch": branch, "status": "Active"},
        pluck="user_id"
    )
    managers = []
    for uid in employees:
        if uid and "Branch Manager" in frappe.get_roles(uid):
            managers.append(uid)
    return managers
