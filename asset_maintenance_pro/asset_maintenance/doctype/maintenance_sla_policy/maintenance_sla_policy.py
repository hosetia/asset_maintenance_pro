import frappe
from frappe.model.document import Document


class MaintenanceSLAPolicy(Document):
    pass


def get_sla_for_request(priority, maintenance_type=None):
    """Return the best matching SLA policy for a given request."""
    filters = {"is_active": 1, "priority": priority}
    if maintenance_type:
        filters["maintenance_type"] = maintenance_type
    policy = frappe.get_all("Maintenance SLA Policy", filters=filters,
                             fields=["*"], limit=1)
    if not policy and maintenance_type:
        # Fallback to any policy for this priority
        policy = frappe.get_all("Maintenance SLA Policy",
                                 filters={"is_active": 1, "priority": priority},
                                 fields=["*"], limit=1)
    return policy[0] if policy else None
