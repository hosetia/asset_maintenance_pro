"""Patch: Create default SLA policies for each priority level."""
import frappe

DEFAULT_POLICIES = [
    {"policy_name": "Critical SLA",  "priority": "Critical", "response_time_hours": 1,  "resolution_time_hours": 4,  "escalation_after_hours": 2,  "send_sla_breach_alert": 1},
    {"policy_name": "High SLA",      "priority": "High",     "response_time_hours": 2,  "resolution_time_hours": 8,  "escalation_after_hours": 4,  "send_sla_breach_alert": 1},
    {"policy_name": "Medium SLA",    "priority": "Medium",   "response_time_hours": 4,  "resolution_time_hours": 24, "escalation_after_hours": 12, "send_sla_breach_alert": 1},
    {"policy_name": "Low SLA",       "priority": "Low",      "response_time_hours": 8,  "resolution_time_hours": 48, "escalation_after_hours": 24, "send_sla_breach_alert": 0},
]

def execute():
    for p in DEFAULT_POLICIES:
        if not frappe.db.exists("Maintenance SLA Policy", p["policy_name"]):
            doc = frappe.get_doc({"doctype": "Maintenance SLA Policy", "is_active": 1, **p})
            doc.flags.ignore_permissions = True
            doc.insert()
    frappe.db.commit()
