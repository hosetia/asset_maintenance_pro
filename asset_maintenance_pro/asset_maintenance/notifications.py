"""
Notification dispatcher for Asset Maintenance Pro.
Supports In-App, Email, and optional SMS (via configurable API).
"""

import frappe
from frappe import _
from frappe.utils import get_url_to_form
import requests


def _settings():
    return frappe.get_single("Asset Maintenance Settings")


# ─── Public entry points ──────────────────────────────────────────────────────

def send_status_change_notification(doc, old_status):
    """Called when a Maintenance Request status changes."""
    settings = _settings()
    if not settings.notify_on_status_change:
        return

    recipients = _get_recipients(doc)
    if not recipients:
        return

    subject = _("Maintenance Request {0}: Status changed to {1}").format(doc.name, doc.status)
    message = _build_status_message(doc, old_status)

    for user in recipients:
        if settings.enable_inapp_notifications:
            _send_inapp(user, subject, message, doc)
        if settings.enable_email_notifications:
            _send_email(user, subject, message)
        if settings.enable_sms_notifications:
            _send_sms(user, subject, settings)


def send_new_request_notification(doc):
    """Called when a new Maintenance Request is created."""
    settings = _settings()
    if not settings.notify_on_new_request:
        return

    recipients = _get_recipients(doc, include_managers=True)
    subject = _("New Maintenance Request {0} for {1}").format(doc.name, doc.asset)
    message = _build_new_request_message(doc)

    for user in recipients:
        if settings.enable_inapp_notifications:
            _send_inapp(user, subject, message, doc)
        if settings.enable_email_notifications:
            _send_email(user, subject, message)
        if settings.enable_sms_notifications:
            _send_sms(user, subject, settings)


def send_overdue_notification(doc):
    """Called by scheduler for overdue requests."""
    settings = _settings()
    if not settings.notify_on_overdue:
        return

    recipients = _get_recipients(doc, include_managers=True)
    subject = _("OVERDUE: Maintenance Request {0} is past due date").format(doc.name)
    message = _build_overdue_message(doc)

    for user in recipients:
        if settings.enable_inapp_notifications:
            _send_inapp(user, subject, message, doc)
        if settings.enable_email_notifications:
            _send_email(user, subject, message)
        if settings.enable_sms_notifications:
            _send_sms(user, subject, settings)


# ─── Recipients ───────────────────────────────────────────────────────────────

def _get_recipients(doc, include_managers=False):
    recipients = set()

    # Always notify assigned technician
    if doc.assigned_to:
        recipients.add(doc.assigned_to)

    # Notify requester
    if doc.requested_by:
        recipients.add(doc.requested_by)

    if include_managers:
        # Find Branch Managers for this branch
        managers = frappe.get_all(
            "Employee",
            filters={"branch": doc.branch, "status": "Active"},
            fields=["user_id"],
        )
        for m in managers:
            if m.user_id:
                user_roles = frappe.get_roles(m.user_id)
                if "Branch Manager" in user_roles:
                    recipients.add(m.user_id)

    # Remove current user (they know what they did)
    recipients.discard(frappe.session.user)
    return list(recipients)


# ─── Message builders ─────────────────────────────────────────────────────────

def _build_status_message(doc, old_status):
    url = get_url_to_form("Maintenance Request", doc.name)
    return """
    <p>{intro}</p>
    <ul>
      <li><b>{asset_label}:</b> {asset}</li>
      <li><b>{branch_label}:</b> {branch}</li>
      <li><b>{old_label}:</b> {old}</li>
      <li><b>{new_label}:</b> {new}</li>
    </ul>
    <p><a href="{url}">{view_label}</a></p>
    """.format(
        intro=_("The status of Maintenance Request {0} has been updated.").format(doc.name),
        asset_label=_("Asset"), asset=doc.asset,
        branch_label=_("Branch"), branch=doc.branch,
        old_label=_("Previous Status"), old=old_status,
        new_label=_("New Status"), new=doc.status,
        url=url, view_label=_("View Request"),
    )


def _build_new_request_message(doc):
    url = get_url_to_form("Maintenance Request", doc.name)
    return """
    <p>{intro}</p>
    <ul>
      <li><b>{asset_label}:</b> {asset}</li>
      <li><b>{branch_label}:</b> {branch}</li>
      <li><b>{type_label}:</b> {mtype}</li>
      <li><b>{priority_label}:</b> {priority}</li>
    </ul>
    <p><a href="{url}">{view_label}</a></p>
    """.format(
        intro=_("A new Maintenance Request {0} has been created.").format(doc.name),
        asset_label=_("Asset"), asset=doc.asset,
        branch_label=_("Branch"), branch=doc.branch,
        type_label=_("Type"), mtype=doc.maintenance_type,
        priority_label=_("Priority"), priority=doc.priority,
        url=url, view_label=_("View Request"),
    )


def _build_overdue_message(doc):
    url = get_url_to_form("Maintenance Request", doc.name)
    return """
    <p>{intro}</p>
    <ul>
      <li><b>{asset_label}:</b> {asset}</li>
      <li><b>{due_label}:</b> {due}</li>
      <li><b>{status_label}:</b> {status}</li>
    </ul>
    <p><a href="{url}">{view_label}</a></p>
    """.format(
        intro=_("Maintenance Request {0} is overdue and requires immediate attention.").format(doc.name),
        asset_label=_("Asset"), asset=doc.asset,
        due_label=_("Due Date"), due=doc.due_date,
        status_label=_("Status"), status=doc.status,
        url=url, view_label=_("View Request"),
    )


# ─── Transport layer ──────────────────────────────────────────────────────────

def _send_inapp(user, subject, message, doc):
    try:
        frappe.publish_realtime(
            "asset_maintenance_notification",
            {"subject": subject, "doc": doc.name},
            user=user,
        )
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": subject,
            "email_content": message,
            "for_user": user,
            "type": "Alert",
            "document_type": "Maintenance Request",
            "document_name": doc.name,
        }).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "In-App Notification Failed")


def _send_email(user, subject, message):
    try:
        email = frappe.db.get_value("User", user, "email")
        if not email:
            return
        frappe.sendmail(
            recipients=[email],
            subject=subject,
            message=message,
            now=True,
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Email Notification Failed")


def _send_sms(user, message_text, settings):
    """Generic SMS dispatcher. Adapt payload to your SMS provider."""
    if not settings.sms_api_url:
        return
    try:
        phone = frappe.db.get_value("User", user, "mobile_no")
        if not phone:
            return
        payload = {
            "to": phone,
            "from": settings.sms_from_number,
            "message": message_text,
            "api_key": settings.sms_api_key,
        }
        headers = {}
        if settings.sms_api_secret:
            headers["Authorization"] = "Bearer {0}".format(settings.sms_api_secret)

        resp = requests.post(settings.sms_api_url, json=payload, headers=headers, timeout=10)
        if not resp.ok:
            frappe.log_error(
                "SMS API returned {0}: {1}".format(resp.status_code, resp.text),
                "SMS Notification Failed"
            )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "SMS Notification Failed")
