"""
doc_events handlers for external DocTypes (Asset).
For Maintenance Request events, see the controller class.
"""

import frappe
from frappe import _


def on_maintenance_request_update(doc, method=None):
    """
    Fired by hooks.py doc_events on Maintenance Request on_update.
    Secondary hook — used for logging and external integrations.
    """
    # REST hook: notify any registered webhooks
    _fire_status_webhook(doc)


def on_asset_insert(doc, method=None):
    """
    When a new Asset is inserted, check if any Maintenance Checklist
    applies to its category and log it for the scheduler.
    """
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
            indicator="blue",
            alert=True,
        )


def _fire_status_webhook(doc):
    """
    Generic outbound webhook: POST to any URL registered in
    'Webhook' DocType with document_type = 'Maintenance Request'.
    Frappe handles this natively via the Webhook DocType, but this
    function can be extended for custom integrations.
    """
    pass  # Frappe's built-in Webhook DocType handles standard REST webhooks
