"""doc_events handlers for Asset Maintenance Pro."""
import frappe
from frappe import _
from frappe.utils import today, flt


def on_maintenance_request_insert(doc, method=None):
    _set_sla_due_date(doc)
    _auto_set_priority_from_impact(doc)
    _check_warranty_alert(doc)
    from asset_maintenance_pro.asset_maintenance.notifications import send_new_request_notification
    send_new_request_notification(doc)


def on_maintenance_request_update(doc, method=None):
    _update_asset_metrics_on_complete(doc)


def on_work_order_update(doc, method=None):
    if doc.status in ("Completed", "Closed") and doc.asset:
        _update_asset_last_maintenance(doc.asset)


def on_asset_insert(doc, method=None):
    if not doc.asset_category:
        return
    checklists = frappe.get_all("Maintenance Checklist",
        filters={"asset_category": doc.asset_category, "is_active": 1},
        fields=["name", "title"])
    if checklists:
        frappe.msgprint(
            _("{0} preventive schedule(s) apply to this asset category.").format(len(checklists)),
            indicator="blue", alert=True)


def on_service_contract_update(doc, method=None):
    from frappe.utils import date_diff
    days = date_diff(doc.end_date, today())
    if 0 < days <= (doc.renewal_reminder_days or 30) and not doc.alert_sent:
        _send_contract_renewal_alert(doc)
        frappe.db.set_value("Service Contract", doc.name, "alert_sent", 1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _set_sla_due_date(doc):
    if doc.due_date:
        return
    try:
        from asset_maintenance_pro.asset_maintenance.doctype.maintenance_sla_policy.maintenance_sla_policy import get_sla_for_request
        from frappe.utils import add_to_date, getdate
        policy = get_sla_for_request(doc.priority, doc.maintenance_type)
        if policy and policy.resolution_time_hours:
            due = add_to_date(doc.creation or frappe.utils.now(),
                              hours=int(policy.resolution_time_hours))
            frappe.db.set_value("Maintenance Request", doc.name, "due_date", getdate(due))
    except Exception:
        pass


def _auto_set_priority_from_impact(doc):
    """Auto-escalate priority for food safety/closure risk."""
    impact = getattr(doc, "impact", "") or ""
    is_food = getattr(doc, "is_food_safety_impact", 0)
    is_closure = getattr(doc, "is_closure_risk", 0)
    if is_closure or "Closure" in impact:
        if doc.priority not in ("Critical",):
            frappe.db.set_value("Maintenance Request", doc.name, "priority", "Critical")
    elif is_food or "Food Safety" in impact:
        if doc.priority not in ("Critical", "High"):
            frappe.db.set_value("Maintenance Request", doc.name, "priority", "High")


def _update_asset_metrics_on_complete(doc):
    if doc.status != "Completed" or not doc.asset:
        return
    _update_asset_last_maintenance(doc.asset)


def _update_asset_last_maintenance(asset):
    frappe.db.set_value("Asset", asset, "custom_last_maintenance_date", today())


def _send_contract_renewal_alert(doc):
    from asset_maintenance_pro.asset_maintenance.notifications import _send_email, _send_inapp
    managers = frappe.get_all("User",
        filters={"enabled": 1, "name": ["in", frappe.get_roles_and_doctypes("System Manager")]},
        pluck="name", limit=3)
    subject = _("Service Contract {0} expiring in {1} days").format(
        doc.name, frappe.utils.date_diff(doc.end_date, today()))
    message = f"<p>Contract <b>{doc.contract_name}</b> with {doc.vendor} expires on <b>{doc.end_date}</b>.</p>"
    for user in managers:
        try:
            _send_email(user, subject, message)
        except Exception:
            pass


def _check_warranty_alert(doc):
    """Alert if asset is still under warranty when creating a maintenance request."""
    if not doc.asset:
        return
    warranty_end = frappe.db.get_value("Asset", doc.asset, "custom_warranty_end")
    if not warranty_end:
        return
    from frappe.utils import getdate, today
    if getdate(warranty_end) >= getdate(today()):
        frappe.msgprint(
            f"🛡️ <b>تنبيه الضمان:</b> الجهاز <b>{doc.asset}</b> لا يزال تحت الضمان "
            f"حتى <b>{warranty_end}</b>. يُرجى التحقق قبل تحمل أي تكاليف خارجية.",
            title="تنبيه ضمان الجهاز",
            indicator="orange"
        )
