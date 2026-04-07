"""
Public REST API for Asset Maintenance Pro.

All endpoints require authentication (standard Frappe token/session).
Base URL: /api/method/asset_maintenance_pro.api.<method>

Endpoints:
  GET  get_maintenance_requests
  GET  get_maintenance_request
  POST transition_status
  POST add_work_log
  GET  get_work_logs
  GET  get_spare_parts
  POST add_meter_reading
  GET  get_asset_maintenance_summary
"""

import frappe
from frappe import _
from frappe.utils import now, today


@frappe.whitelist()
def get_maintenance_requests(
    branch=None,
    asset=None,
    status=None,
    assigned_to=None,
    limit_page_length=20,
    limit_start=0,
):
    """
    GET /api/method/asset_maintenance_pro.api.get_maintenance_requests

    Returns paginated list of Maintenance Requests scoped to the caller's permissions.
    """
    filters = {}
    if branch:
        filters["branch"] = branch
    if asset:
        filters["asset"] = asset
    if status:
        filters["status"] = status
    if assigned_to:
        filters["assigned_to"] = assigned_to

    requests = frappe.get_list(
        "Maintenance Request",
        filters=filters,
        fields=[
            "name", "asset", "branch", "maintenance_type", "priority",
            "status", "kanban_column", "assigned_to", "due_date",
            "total_cost", "requested_by", "requested_on", "closed_on",
        ],
        limit_page_length=int(limit_page_length),
        limit_start=int(limit_start),
        order_by="modified desc",
    )
    return {"data": requests, "total": len(requests)}


@frappe.whitelist()
def get_maintenance_request(name):
    """
    GET /api/method/asset_maintenance_pro.api.get_maintenance_request?name=MNT-2024-00001

    Returns full Maintenance Request document.
    """
    doc = frappe.get_doc("Maintenance Request", name)
    frappe.has_permission("Maintenance Request", doc=doc, throw=True)
    return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def transition_status(name, new_status):
    """
    POST /api/method/asset_maintenance_pro.api.transition_status
    Body: { "name": "MNT-...", "new_status": "In Progress" }

    Transitions a Maintenance Request to a new status.
    """
    doc = frappe.get_doc("Maintenance Request", name)
    frappe.has_permission("Maintenance Request", "write", doc=doc, throw=True)
    return doc.transition_status(new_status)


@frappe.whitelist(methods=["POST"])
def add_work_log(maintenance_request, log_type, description, time_spent_hours=None):
    """
    POST /api/method/asset_maintenance_pro.api.add_work_log
    Body: { "maintenance_request": "MNT-...", "log_type": "Work Note", "description": "..." }

    Adds a Work Log entry to a Maintenance Request.
    """
    frappe.has_permission("Maintenance Work Log", "create", throw=True)
    wl = frappe.get_doc({
        "doctype": "Maintenance Work Log",
        "maintenance_request": maintenance_request,
        "log_type": log_type,
        "description": description,
        "time_spent_hours": time_spent_hours,
        "logged_by": frappe.session.user,
        "log_datetime": now(),
    })
    wl.insert()
    return {"name": wl.name, "status": "created"}


@frappe.whitelist()
def get_work_logs(maintenance_request):
    """
    GET /api/method/asset_maintenance_pro.api.get_work_logs?maintenance_request=MNT-...

    Returns all work logs for a Maintenance Request.
    """
    frappe.has_permission("Maintenance Request", "read",
        doc=frappe.get_doc("Maintenance Request", maintenance_request), throw=True)
    logs = frappe.get_all(
        "Maintenance Work Log",
        filters={"maintenance_request": maintenance_request},
        fields=["name", "log_type", "description", "logged_by",
                "log_datetime", "time_spent_hours", "attachments"],
        order_by="log_datetime desc",
    )
    return {"data": logs}


@frappe.whitelist()
def get_spare_parts(maintenance_request):
    """
    GET /api/method/asset_maintenance_pro.api.get_spare_parts?maintenance_request=MNT-...

    Returns spare part consumption records for a request.
    """
    frappe.has_permission("Maintenance Request", "read",
        doc=frappe.get_doc("Maintenance Request", maintenance_request), throw=True)
    parts = frappe.get_all(
        "Spare Part Consumption",
        filters={"maintenance_request": maintenance_request},
        fields=["name", "item_code", "item_name", "qty", "uom",
                "rate", "amount", "warehouse", "stock_entry"],
        order_by="consumed_on desc",
    )
    return {"data": parts}


@frappe.whitelist(methods=["POST"])
def add_meter_reading(asset, meter_value, uom, notes=None):
    """
    POST /api/method/asset_maintenance_pro.api.add_meter_reading
    Body: { "asset": "AST-...", "meter_value": 12500, "uom": "Hours" }

    Records a new meter reading for an asset.
    """
    frappe.has_permission("Asset Meter Reading", "create", throw=True)
    branch = frappe.db.get_value("Asset", asset, "branch")
    mr = frappe.get_doc({
        "doctype": "Asset Meter Reading",
        "asset": asset,
        "branch": branch,
        "meter_value": meter_value,
        "uom": uom,
        "reading_date": today(),
        "notes": notes,
    })
    mr.insert()
    return {"name": mr.name, "delta": mr.delta, "previous_reading": mr.previous_reading}


@frappe.whitelist()
def get_asset_maintenance_summary(asset=None, branch=None):
    """
    GET /api/method/asset_maintenance_pro.api.get_asset_maintenance_summary

    Returns a summary dashboard payload: counts by status,
    overdue count, total cost by month.
    """
    filters = {}
    if asset:
        filters["asset"] = asset
    if branch:
        filters["branch"] = branch

    all_requests = frappe.get_list(
        "Maintenance Request",
        filters=filters,
        fields=["status", "total_cost", "due_date"],
    )

    status_counts = {}
    total_cost = 0.0
    overdue_count = 0
    today_date = frappe.utils.getdate(today())

    for r in all_requests:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1
        total_cost += float(r.total_cost or 0)
        if r.due_date and frappe.utils.getdate(r.due_date) < today_date and \
                r.status not in ("Completed", "Cancelled"):
            overdue_count += 1

    return {
        "status_counts": status_counts,
        "total_cost": total_cost,
        "overdue_count": overdue_count,
        "total_requests": len(all_requests),
    }


@frappe.whitelist()
def get_kanban_data(branch=None):
    """
    GET /api/method/asset_maintenance_pro.api.get_kanban_data

    Returns requests grouped by kanban_column for board rendering.
    """
    filters = {"status": ["not in", ["Cancelled"]]}
    if branch:
        filters["branch"] = branch

    requests = frappe.get_list(
        "Maintenance Request",
        filters=filters,
        fields=[
            "name", "asset", "branch", "priority", "status",
            "kanban_column", "assigned_to", "due_date", "maintenance_type",
        ],
        order_by="priority desc, due_date asc",
        limit_page_length=500,
    )

    columns = ["New", "Assigned", "In Progress", "Waiting Parts", "Awaiting Close", "Completed"]
    board = {col: [] for col in columns}

    for req in requests:
        col = req.kanban_column or "New"
        if col in board:
            board[col].append(req)

    return {"columns": columns, "board": board}
