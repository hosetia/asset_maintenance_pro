"""doc_events handlers."""
import frappe
from frappe import _


def on_maintenance_request_insert(doc, method=None):
    """On new request: auto-set SLA due date, notify."""
    _set_sla_due_date(doc)
    from asset_maintenance_pro.asset_maintenance.notifications import send_new_request_notification
    send_new_request_notification(doc)


def on_maintenance_request_update(doc, method=None):
    """On update: fire webhooks."""
    pass  # Frappe Webhook DocType handles standard webhooks


def on_asset_insert(doc, method=None):
    """On new asset: hint about applicable maintenance schedules."""
    if not doc.asset_category:
        return
    checklists = frappe.get_all(
        "Maintenance Checklist",
        filters={"asset_category": doc.asset_category, "is_active": 1},
        fields=["name", "title"],
    )
    if checklists:
        frappe.msgprint(
            _("{0} preventive maintenance schedule(s) apply to this asset category.").format(
                len(checklists)
            ),
            indicator="blue", alert=True,
        )


def _set_sla_due_date(doc):
    """Auto-set due_date based on SLA policy if not already set."""
    if doc.due_date:
        return
    try:
        from asset_maintenance_pro.asset_maintenance.doctype.maintenance_sla_policy.maintenance_sla_policy import get_sla_for_request
        from frappe.utils import add_to_date
        policy = get_sla_for_request(doc.priority, doc.maintenance_type)
        if policy and policy.resolution_time_hours:
            hours = policy.resolution_time_hours
            due = add_to_date(doc.creation or frappe.utils.now(),
                              hours=int(hours))
            frappe.db.set_value("Maintenance Request", doc.name, "due_date",
                                frappe.utils.getdate(due))
    except Exception:
        pass
