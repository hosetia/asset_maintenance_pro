"""
Patch v1.0: Create default Asset Maintenance Settings document if not exists.
"""
import frappe


def execute():
    if frappe.db.exists("Asset Maintenance Settings", "Asset Maintenance Settings"):
        return  # Already set up

    settings = frappe.get_doc({
        "doctype": "Asset Maintenance Settings",
        "enable_email_notifications": 1,
        "enable_inapp_notifications": 1,
        "enable_sms_notifications": 0,
        "notify_on_new_request": 1,
        "notify_on_status_change": 1,
        "notify_on_overdue": 1,
        "overdue_threshold_days": 3,
        "auto_create_stock_entry": 1,
        "stock_entry_type": "Material Issue",
        "enable_preventive_scheduler": 1,
        "scheduler_lookahead_days": 7,
    })
    settings.flags.ignore_permissions = True
    settings.insert()
    frappe.db.commit()
